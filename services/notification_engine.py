from typing import Dict, Any, List
from services.dataset_store import dataset_store
from services.person1_service import Person1Service
from services.payment_analytics import PaymentAnalyticsService
from services.change_detector import ChangeDetectorService
from services.quality_score import QualityScoreService
from utils.helpers import sanitize_for_json

class NotificationEngineService:
    """Automated Notification and Alert Engine generating severity-rated insights."""

    @staticmethod
    def generate_notifications(dataset_id: str) -> Dict[str, Any]:
        notifications = []

        # 1. Check Data Quality Alerts
        quality_res = QualityScoreService.calculate_score(dataset_id)
        score = quality_res.get("score", 100)
        if score < 70:
            notifications.append({
                "severity": "critical" if score < 50 else "warning",
                "type": "data_quality_alert",
                "message": f"Data quality score is low ({score}/100, Grade {quality_res.get('grade')}). Missing values or formatting issues detected."
            })

        # 2. Check Payment Alerts
        payment_res = PaymentAnalyticsService.analyze_payments(dataset_id)
        if payment_res.get("applicable"):
            pending_amt = payment_res.get("pending_amount", 0)
            failed_amt = payment_res.get("failed_amount", 0)
            total_amt = payment_res.get("total_amount", 1)

            if pending_amt / total_amt > 0.15:
                pending_pct = round(pending_amt / total_amt * 100, 1)
                notifications.append({
                    "severity": "warning",
                    "type": "pending_payments_alert",
                    "message": f"High pending payment volume detected ({pending_pct}% of total amount, total pending: ${pending_amt:,.2f})."
                })

            if failed_amt / total_amt > 0.05:
                failed_pct = round(failed_amt / total_amt * 100, 1)
                notifications.append({
                    "severity": "critical",
                    "type": "failed_payments_alert",
                    "message": f"Significant failed transaction rate detected ({failed_pct}% failed, total: ${failed_amt:,.2f})."
                })

        # 3. Check Change Alerts
        change_res = ChangeDetectorService.detect_changes(dataset_id)
        if change_res.get("applicable"):
            daily = change_res.get("daily", {})
            for key, val in daily.items():
                if key.endswith("_change_percent") and isinstance(val, (int, float)):
                    if val <= -10.0:
                        metric_name = key.replace("_change_percent", "").capitalize()
                        notifications.append({
                            "severity": "warning",
                            "type": "metric_drop_alert",
                            "message": f"{metric_name} decreased by {abs(val)}% compared to the previous period."
                        })

        # 4. Check Outlier Alerts
        try:
            outliers_res = Person1Service.get_outliers(dataset_id)
            outlier_pct = outliers_res.get("outliers_percentage", 0) if isinstance(outliers_res, dict) else 0
            if outlier_pct > 5.0:
                notifications.append({
                    "severity": "info",
                    "type": "high_outlier_alert",
                    "message": f"{outlier_pct}% of dataset records were identified as statistical outliers."
                })
        except Exception:
            pass

        # Default Info Notification if clean dataset
        if not notifications:
            notifications.append({
                "severity": "info",
                "type": "system_status",
                "message": "Dataset analysis complete. All metric trends and data quality indicators are nominal."
            })

        return sanitize_for_json({
            "dataset_id": dataset_id,
            "notifications": notifications
        })
