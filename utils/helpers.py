import pandas as pd
import numpy as np
import math
from typing import Any, List, Dict, Tuple, Optional

def sanitize_for_json(val: Any) -> Any:
    """Recursively convert numpy types, NaNs, infinities, and timestamps to JSON-serializable primitives."""
    if val is None:
        return None
    if isinstance(val, (bool, np.bool_)):
        return bool(val)
    if isinstance(val, (float, np.floating)):
        if math.isnan(val) or math.isinf(val):
            return None
        return float(val)
    if isinstance(val, (int, np.integer)):
        return int(val)
    if isinstance(val, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(val).isoformat()
    if isinstance(val, dict):
        return {str(k): sanitize_for_json(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, np.ndarray, pd.Series)):
        return [sanitize_for_json(v) for v in val]
    return str(val)

def clean_numeric_series(series: pd.Series) -> pd.Series:
    """Strips currency symbols (₹, $, €, £, ¥, INR, USD), percentage signs, commas, and quotes to convert to numeric."""
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors='coerce')
    cleaned = (
        series.astype(str)
        .str.replace(r'[₹$€£¥,%\"\'\s]', '', regex=True)
        .str.replace(r'(?i)\b(inr|usd|eur|rs|gbp|cad)\b', '', regex=True)
    )
    return pd.to_numeric(cleaned, errors='coerce')

def clean_dataframe_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Creates a copy of the dataframe with dirty currency/percentage columns converted to clean floats."""
    df_copy = df.copy()
    for col in df_copy.columns:
        if pd.api.types.is_numeric_dtype(df_copy[col]):
            continue
        cleaned = clean_numeric_series(df_copy[col])
        non_null_count = df_copy[col].dropna().shape[0]
        if non_null_count > 5 and (cleaned.notna().sum() > 0.6 * non_null_count):
            col_lower = str(col).lower()
            is_id = any(col_lower == kw or col_lower.endswith('_' + kw) or col_lower.startswith(kw + '_') 
                        for kw in ['id', 'uuid', 'index', 'code', 'sk', 'pk', 'key', 'no', 'number', 'ref'])
            if not is_id:
                df_copy[col] = cleaned
    return df_copy

def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Categorize columns into:
    - 'datetime'
    - 'identifier'
    - 'numeric'
    - 'categorical'
    - 'text'
    """
    column_types = {}
    total_rows = len(df)

    for col in df.columns:
        col_lower = str(col).lower()
        series = df[col]

        # Check datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            column_types[col] = 'datetime'
            continue
        
        # Try datetime conversion if string and named like date/time
        if series.dtype == 'object' or pd.api.types.is_string_dtype(series):
            if any(dt_kw in col_lower for dt_kw in ['date', 'time', 'timestamp', 'dt', 'day', 'month', 'year']):
                try:
                    parsed = pd.to_datetime(series.dropna().head(50), format='mixed', errors='coerce')
                    if parsed.notna().sum() > 0.5 * len(series.dropna().head(50)):
                        column_types[col] = 'datetime'
                        continue
                except Exception:
                    try:
                        parsed = pd.to_datetime(series.dropna().head(50), errors='coerce')
                        if parsed.notna().sum() > 0.5 * len(series.dropna().head(50)):
                            column_types[col] = 'datetime'
                            continue
                    except Exception:
                        pass

        # Check Identifier
        is_id_name = any(col_lower == kw or col_lower.endswith('_' + kw) or col_lower.startswith(kw + '_') 
                         for kw in ['id', 'uuid', 'index', 'code', 'sk', 'pk', 'key', 'no', 'number', 'ref'])
        
        nunique = series.nunique(dropna=True)
        if total_rows > 5 and nunique == total_rows and (is_id_name or series.dtype == 'object'):
            column_types[col] = 'identifier'
            continue
        if is_id_name and nunique > 0.8 * total_rows:
            column_types[col] = 'identifier'
            continue

        # Check Boolean
        if pd.api.types.is_bool_dtype(series):
            column_types[col] = 'categorical'
            continue

        # Check Numeric
        if pd.api.types.is_numeric_dtype(series):
            if is_id_name and nunique == total_rows:
                column_types[col] = 'identifier'
            else:
                column_types[col] = 'numeric'
            continue

        # Try converting string to numeric natively
        numeric_series = pd.to_numeric(series, errors='coerce')
        if numeric_series.notna().sum() > 0.8 * total_rows:
            column_types[col] = 'numeric'
            continue

        # Categorical vs Text
        if nunique < 0.5 * total_rows or nunique < 50:
            column_types[col] = 'categorical'
        else:
            column_types[col] = 'text'

    return column_types

def parse_dates_in_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[str]]:
    """Identifies and parses the primary date column in the dataframe."""
    df_copy = df.copy()
    col_types = detect_column_types(df_copy)
    
    date_cols = [col for col, ctype in col_types.items() if ctype == 'datetime']
    
    if not date_cols:
        # Fallback search for any column that parses to datetime
        for col in df_copy.columns:
            if df_copy[col].dtype == 'object':
                try:
                    parsed = pd.to_datetime(df_copy[col], format='mixed', errors='coerce')
                    if parsed.notna().sum() > 0.5 * len(df_copy):
                        df_copy[col] = parsed
                        return df_copy, col
                except Exception:
                    pass
        return df_copy, None
        
    primary_date = date_cols[0]
    if not pd.api.types.is_datetime64_any_dtype(df_copy[primary_date]):
        try:
            df_copy[primary_date] = pd.to_datetime(df_copy[primary_date], format='mixed', errors='coerce')
        except Exception:
            df_copy[primary_date] = pd.to_datetime(df_copy[primary_date], errors='coerce')
        
    return df_copy, primary_date
