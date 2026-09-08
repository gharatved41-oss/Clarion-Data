"""Service for streaming export of cleaned datasets in CSV and XLSX formats."""
import io
import logging
import pandas as pd
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse

from app.services.cleaning_service import CleaningService

logger = logging.getLogger("app.services.export_service")


class ExportService:
    """Cleaned dataset exporter."""

    @classmethod
    def export_dataset(cls, dataset_id: str, format: str = "csv") -> StreamingResponse:
        """Stream cleaned dataset as downloadable CSV or XLSX attachment."""
        fmt = format.lower().strip()
        if fmt not in ("csv", "xlsx"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format '{format}'. Supported formats are: csv, xlsx."
            )

        df, _ = CleaningService.load_cleaned_dataset(dataset_id)
        buffer = io.BytesIO()

        if fmt == "csv":
            df.to_csv(buffer, index=False, encoding="utf-8")
            buffer.seek(0)
            media_type = "text/csv"
            filename = f"cleaned_{dataset_id[:8]}.csv"
        else:  # xlsx
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Cleaned Data")
            buffer.seek(0)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"cleaned_{dataset_id[:8]}.xlsx"

        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition",
        }

        return StreamingResponse(
            buffer,
            media_type=media_type,
            headers=headers
        )
