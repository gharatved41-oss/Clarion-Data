import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from services.dataset_store import dataset_store
from utils.helpers import detect_column_types, parse_dates_in_dataframe, sanitize_for_json, clean_numeric_series, clean_dataframe_numeric_columns

class PredictionService:
    """Automatic Time-Series & Tabular Forecasting / Prediction Service (Version 2)."""

    @staticmethod
    def analyze_predictions(
        dataset_id: str,
        target: Optional[str] = None,
        steps: int = 7,
        model_type: Optional[str] = None
    ) -> Dict[str, Any]:
        df = dataset_store.get_dataset(dataset_id)
        if df is None:
            return {"applicable": False, "reason": "Dataset not found"}

        if len(df) < 10:
            return {
                "applicable": False,
                "reason": "Insufficient observations for forecasting (minimum 10 rows required)"
            }

        # Safe forecast steps clamp (1 to 90 days)
        try:
            steps = max(1, min(90, int(steps)))
        except (ValueError, TypeError):
            steps = 7

        df_parsed, date_col = parse_dates_in_dataframe(df)
        df_parsed = clean_dataframe_numeric_columns(df_parsed)
        col_types = detect_column_types(df_parsed)

        numeric_cols = [c for c, t in col_types.items() if t == 'numeric' and df_parsed[c].dropna().nunique() > 1]
        available_targets = list(numeric_cols)

        # Select target column
        target_col = None
        if target and target in df_parsed.columns:
            if target not in numeric_cols:
                df_parsed[target] = clean_numeric_series(df_parsed[target])
                if df_parsed[target].notna().sum() > 5:
                    target_col = target
            else:
                target_col = target

        if not target_col:
            # Prioritize business metrics
            priority_keywords = ['revenue', 'total_sales', 'sales', 'amount', 'spend', 'total', 'price', 'profit', 'conversions', 'clicks', 'demand', 'quantity']
            for kw in priority_keywords:
                matching = [c for c in numeric_cols if kw in c.lower()]
                if matching:
                    target_col = matching[0]
                    break

        if not target_col and len(numeric_cols) > 0:
            # Pick numeric column with highest variance that is not an ID
            variances = {c: df_parsed[c].dropna().var() for c in numeric_cols if df_parsed[c].dropna().nunique() > 5}
            if variances:
                target_col = max(variances, key=variances.get)

        if not target_col:
            return {
                "applicable": False,
                "reason": "No suitable numerical target feature found for prediction"
            }

        # CASE 1: Time-Series Forecasting (Date column present)
        if date_col and df_parsed[date_col].notna().sum() >= 10:
            return PredictionService._forecast_time_series(
                df_parsed, dataset_id, date_col, target_col,
                steps=steps, preferred_model=model_type, available_targets=available_targets
            )

        # CASE 2: Tabular Regression Prediction (No date column, but predictive numeric features exist)
        feature_cols = [c for c in numeric_cols if c != target_col]
        if len(feature_cols) >= 1:
            return PredictionService._predict_tabular_regression(
                df_parsed, dataset_id, target_col, feature_cols,
                preferred_model=model_type, available_targets=available_targets
            )

        return {
            "applicable": False,
            "reason": "No suitable time-series or predictive feature relationships detected"
        }

    @staticmethod
    def _forecast_time_series(
        df: pd.DataFrame,
        dataset_id: str,
        date_col: str,
        target_col: str,
        steps: int = 7,
        preferred_model: Optional[str] = None,
        available_targets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        ts_df = df[[date_col, target_col]].dropna().copy()
        try:
            ts_df[date_col] = pd.to_datetime(ts_df[date_col], format='mixed', errors='coerce')
        except Exception:
            ts_df[date_col] = pd.to_datetime(ts_df[date_col], errors='coerce')
        
        ts_df[target_col] = pd.to_numeric(ts_df[target_col], errors='coerce')
        ts_df = ts_df.dropna().sort_values(by=date_col)

        if len(ts_df) < 8:
            return {
                "applicable": False,
                "reason": "Insufficient non-null time-series observations for forecasting"
            }

        # Aggregate by date: use mean for rates/ratings/averages/percentages, sum for volumes/revenue
        target_lower = target_col.lower()
        if any(kw in target_lower for kw in ['rate', 'rating', 'pct', 'percent', 'ratio', 'avg', 'score']):
            aggregated = ts_df.groupby(ts_df[date_col].dt.date)[target_col].mean().reset_index()
        else:
            aggregated = ts_df.groupby(ts_df[date_col].dt.date)[target_col].sum().reset_index()

        aggregated[date_col] = pd.to_datetime(aggregated[date_col])
        aggregated = aggregated.sort_values(by=date_col)

        if len(aggregated) < 8:
            return {
                "applicable": False,
                "reason": "Insufficient distinct date data points for time-series aggregation"
            }

        # Feature Engineering for Time Series
        aggregated['time_idx'] = np.arange(len(aggregated))
        aggregated['dayofweek'] = aggregated[date_col].dt.dayofweek
        aggregated['month'] = aggregated[date_col].dt.month
        aggregated['day'] = aggregated[date_col].dt.day
        aggregated['is_weekend'] = (aggregated['dayofweek'] >= 5).astype(int)

        feature_cols = ['time_idx', 'dayofweek', 'month', 'day', 'is_weekend']
        
        # Add lag and rolling features if series length permits
        if len(aggregated) >= 15:
            aggregated['lag_1'] = aggregated[target_col].shift(1).bfill()
            aggregated['rolling_mean_3'] = aggregated[target_col].shift(1).rolling(3, min_periods=1).mean().bfill()
            feature_cols.extend(['lag_1', 'rolling_mean_3'])

        X = aggregated[feature_cols]
        y = aggregated[target_col]

        # Train/Test chronological split (80% train, 20% test)
        split_idx = int(len(aggregated) * 0.8)
        if split_idx < 5:
            split_idx = max(1, len(aggregated) - 2)

        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Candidate Model Zoo
        candidate_models = {
            "LinearRegression": LinearRegression(),
            "RandomForestRegressor": RandomForestRegressor(n_estimators=50, random_state=42),
            "GradientBoostingRegressor": GradientBoostingRegressor(n_estimators=50, random_state=42),
            "Ridge": Ridge(alpha=1.0)
        }

        best_model_name = "LinearRegression"
        best_model = candidate_models["LinearRegression"]
        best_r2 = -999.0
        best_rmse = float('inf')
        best_eval = {}
        best_preds = None

        models_to_try = {}
        if preferred_model and preferred_model in candidate_models:
            models_to_try = {preferred_model: candidate_models[preferred_model]}
        else:
            models_to_try = candidate_models

        for m_name, model in models_to_try.items():
            try:
                model.fit(X_train, y_train)
                preds = model.predict(X_test)

                mae = float(mean_absolute_error(y_test, preds))
                rmse = float(root_mean_squared_error(y_test, preds))
                r2 = float(r2_score(y_test, preds)) if len(y_test) > 1 else 0.0

                non_zero_mask = (y_test != 0)
                if non_zero_mask.sum() > 0:
                    mape = float(np.mean(np.abs((y_test[non_zero_mask] - preds[non_zero_mask]) / y_test[non_zero_mask])) * 100)
                else:
                    mape = 0.0

                # Selection logic: prioritize highest R2, fallback to lowest RMSE
                if r2 > best_r2 or (abs(r2 - best_r2) < 1e-4 and rmse < best_rmse):
                    best_r2 = r2
                    best_rmse = rmse
                    best_model_name = m_name
                    best_model = model
                    best_preds = preds
                    best_eval = {
                        "MAE": round(mae, 2),
                        "RMSE": round(rmse, 2),
                        "R2": round(r2, 4),
                        "MAPE_percent": round(mape, 2)
                    }
            except Exception:
                continue

        # Estimate residual standard error for confidence intervals
        if best_preds is not None and len(y_test) > 1:
            residuals = y_test - best_preds
            std_err = float(np.std(residuals))
        else:
            std_err = float(np.std(y)) * 0.1

        if std_err <= 1e-4 or np.isnan(std_err):
            std_err = max(1.0, float(np.mean(y)) * 0.05)

        # Fit best model on entire dataset for future forecasting
        best_model.fit(X, y)

        # Determine non-negativity constraint
        is_non_negative = (y >= 0).all()

        # Generate future forecasts with 95% confidence intervals
        last_date = aggregated[date_col].max()
        last_idx = aggregated['time_idx'].max()
        
        future_forecast = []
        last_val = y.iloc[-1]
        recent_values = list(y.tail(3))

        for i in range(1, steps + 1):
            future_date = last_date + pd.Timedelta(days=i)
            future_idx = last_idx + i
            
            row_dict = {
                'time_idx': future_idx,
                'dayofweek': future_date.dayofweek,
                'month': future_date.month,
                'day': future_date.day,
                'is_weekend': int(future_date.dayofweek >= 5)
            }
            if 'lag_1' in feature_cols:
                row_dict['lag_1'] = last_val
            if 'rolling_mean_3' in feature_cols:
                row_dict['rolling_mean_3'] = np.mean(recent_values[-3:])

            future_X = pd.DataFrame([row_dict])[feature_cols]
            pred_val = float(best_model.predict(future_X)[0])
            if is_non_negative:
                pred_val = max(0.0, pred_val)

            # 95% confidence bound with expanding horizon uncertainty
            margin = 1.96 * std_err * float(np.sqrt(1.0 + 0.08 * i))
            lower_bound = round(max(0.0, pred_val - margin) if is_non_negative else (pred_val - margin), 2)
            upper_bound = round(pred_val + margin, 2)

            last_val = pred_val
            recent_values.append(pred_val)

            future_forecast.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "step": i,
                "predicted_value": round(pred_val, 2),
                "lower_bound": lower_bound,
                "upper_bound": upper_bound
            })

        # Trend and Growth Intelligence
        recent_actuals = y.tail(min(5, len(y)))
        avg_recent = float(recent_actuals.mean())
        avg_forecast = float(np.mean([f["predicted_value"] for f in future_forecast])) if future_forecast else avg_recent
        growth_rate = round(((avg_forecast - avg_recent) / (abs(avg_recent) + 1e-6)) * 100.0, 2)

        if growth_rate > 3.0:
            trend_direction = "increasing"
        elif growth_rate < -3.0:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"

        # Confidence assessment
        r2_val = best_eval.get("R2", 0.0)
        mape_val = best_eval.get("MAPE_percent", 999.0)
        if r2_val > 0.65 or (0 < mape_val < 15.0):
            confidence_level = "high"
        elif r2_val > 0.15 or (mape_val < 35.0):
            confidence_level = "medium"
        else:
            confidence_level = "low"

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "applicable": True,
            "target": target_col,
            "date_column": date_col,
            "prediction_type": "time_series_forecasting",
            "model": best_model_name,
            "evaluation": best_eval,
            "forecast": future_forecast,
            "trend_direction": trend_direction,
            "growth_rate_percent": growth_rate,
            "confidence_level": confidence_level,
            "available_targets": available_targets or [target_col]
        })

    @staticmethod
    def _predict_tabular_regression(
        df: pd.DataFrame,
        dataset_id: str,
        target_col: str,
        feature_cols: List[str],
        preferred_model: Optional[str] = None,
        available_targets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        sub_df = df[[target_col] + feature_cols].dropna().copy()
        for col in [target_col] + feature_cols:
            sub_df[col] = pd.to_numeric(sub_df[col], errors='coerce')
        sub_df = sub_df.dropna()

        if len(sub_df) < 10:
            return {
                "applicable": False,
                "reason": "Insufficient non-null tabular samples for regression"
            }

        X = sub_df[feature_cols]
        y = sub_df[target_col]

        split_idx = int(len(sub_df) * 0.8)
        if split_idx < 5:
            split_idx = max(1, len(sub_df) - 2)

        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # Train model (defaulting to Random Forest Regressor)
        model = RandomForestRegressor(n_estimators=40, random_state=42)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(root_mean_squared_error(y_test, preds))
        r2 = float(r2_score(y_test, preds)) if len(y_test) > 1 else 0.0

        # Feature Importance calculation
        feature_importance = {}
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            feature_importance = {
                feat: round(float(imp), 4)
                for feat, imp in sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
            }

        # Residual std error for bounds
        residuals = y_test - preds
        std_err = float(np.std(residuals)) if len(residuals) > 0 else 1.0
        is_non_negative = (y >= 0).all()

        # Generate sample predictions for held-out features
        sample_forecast = []
        sample_preds = model.predict(X_test.head(5))
        for idx, p_val in enumerate(sample_preds):
            pred_float = float(p_val)
            if is_non_negative:
                pred_float = max(0.0, pred_float)
            margin = 1.96 * std_err
            sample_forecast.append({
                "sample_index": idx,
                "predicted_value": round(pred_float, 2),
                "lower_bound": round(max(0.0, pred_float - margin) if is_non_negative else (pred_float - margin), 2),
                "upper_bound": round(pred_float + margin, 2)
            })

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "applicable": True,
            "target": target_col,
            "date_column": None,
            "prediction_type": "tabular_regression",
            "model": "RandomForestRegressor",
            "evaluation": {
                "MAE": round(mae, 2),
                "RMSE": round(rmse, 2),
                "R2": round(r2, 4)
            },
            "forecast": sample_forecast,
            "feature_importance": feature_importance,
            "confidence_level": "high" if r2 > 0.5 else ("medium" if r2 > 0.1 else "low"),
            "available_targets": available_targets or [target_col]
        })
