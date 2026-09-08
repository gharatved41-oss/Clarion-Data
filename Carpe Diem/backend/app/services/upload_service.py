"""Service handling dataset upload, validation, persistence, and overview extraction."""
import json
import logging
import uuid
from pathlib import Path
from typing import Any
import pandas as pd
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings
from app.schemas.dataset import UploadResponse, DatasetOverviewResponse

logger = logging.getLogger("app.services.upload_service")

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


class UploadService:
    """Service for dataset uploads and storage."""

    @staticmethod
    def _validate_extension(filename: str | None) -> str:
        """Validate file extension and return lowercase extension."""
        if not filename or "." not in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is missing or has no file extension."
            )
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed formats are: {allowed}"
            )
        return ext

    @classmethod
    def _read_dataframe(cls, file_path: Path, ext: str) -> pd.DataFrame:
        """Read dataframe from file with multiple encoding fallbacks."""
        try:
            if ext == ".csv":
                encodings = ["utf-8", "utf-8-sig", "latin1", "cp1252", "iso-8859-1"]
                df = None
                last_error = None
                for enc in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=enc)
                        break
                    except (UnicodeDecodeError, pd.errors.ParserError) as err:
                        last_error = err
                        continue
                if df is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to parse CSV file: {last_error}"
                    )
            elif ext == ".xlsx":
                df = pd.read_excel(file_path, engine="openpyxl")
            elif ext == ".xls":
                df = pd.read_excel(file_path, engine="xlrd")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file extension: {ext}"
                )
            return df
        except HTTPException:
            raise
        except pd.errors.EmptyDataError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )
        except Exception as exc:
            logger.error(f"Error parsing uploaded file {file_path}: {exc}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read dataset file: {str(exc)}"
            )

    @classmethod
    async def upload_dataset(cls, file: UploadFile) -> UploadResponse:
        """Validate, store original file, and extract initial metadata."""
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file was uploaded or filename is empty."
            )

        ext = cls._validate_extension(file.filename)

        # Generate unique dataset ID
        dataset_id = str(uuid.uuid4())
        dataset_dir = settings.uploads_dir / dataset_id
        dataset_dir.mkdir(parents=True, exist_ok=True)

        stored_file_path = dataset_dir / f"original{ext}"

        # Stream and save file contents to disk
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            # Clean up empty directory
            stored_file_path.unlink(missing_ok=True)
            dataset_dir.rmdir()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes)."
            )

        with open(stored_file_path, "wb") as f:
            f.write(file_bytes)

        # Read into DataFrame to validate contents
        try:
            df = cls._read_dataframe(stored_file_path, ext)
        except Exception:
            # Clean up invalid uploaded file
            stored_file_path.unlink(missing_ok=True)
            dataset_dir.rmdir()
            raise

        rows, cols = df.shape

        if cols == 0:
            stored_file_path.unlink(missing_ok=True)
            dataset_dir.rmdir()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset contains no columns."
            )

        if rows == 0:
            stored_file_path.unlink(missing_ok=True)
            dataset_dir.rmdir()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dataset contains no rows."
            )

        # Calculate metadata
        col_names = [str(c) for c in df.columns]
        missing_count = int(df.isna().sum().sum())
        duplicate_count = int(df.duplicated().sum())
        memory_bytes = int(df.memory_usage(deep=True).sum())

        metadata = {
            "dataset_id": dataset_id,
            "filename": file.filename,
            "file_type": ext,
            "stored_file": str(stored_file_path.name),
            "rows": rows,
            "columns": cols,
            "column_names": col_names,
            "missing_values": missing_count,
            "duplicate_rows": duplicate_count,
            "memory_usage_bytes": memory_bytes,
        }

        # Write metadata.json
        metadata_path = dataset_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Dataset successfully uploaded: id={dataset_id}, file={file.filename}, shape=({rows}, {cols})")

        return UploadResponse(
            dataset_id=dataset_id,
            filename=file.filename,
            rows=rows,
            columns=cols,
            message="Dataset uploaded successfully"
        )

    @classmethod
    def get_dataset_dir(cls, dataset_id: str) -> Path:
        """Retrieve the dataset directory, raising 404 if not found."""
        dataset_dir = settings.uploads_dir / dataset_id
        if not dataset_dir.exists() or not dataset_dir.is_dir():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset with ID '{dataset_id}' not found."
            )
        return dataset_dir

    @classmethod
    def get_dataset_overview(cls, dataset_id: str) -> DatasetOverviewResponse:
        """Retrieve dataset overview information from metadata."""
        dataset_dir = cls.get_dataset_dir(dataset_id)
        metadata_path = dataset_dir / "metadata.json"

        if not metadata_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metadata for dataset '{dataset_id}' is missing."
            )

        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        preview_rows: list[dict[str, Any]] = []
        try:
            df, _ = cls.load_raw_dataset(dataset_id)
            sample_df = df.head(5).copy()
            for record in sample_df.to_dict(orient="records"):
                clean_record = {}
                for k, v in record.items():
                    if pd.isna(v):
                        clean_record[str(k)] = None
                    elif hasattr(v, "isoformat"):
                        clean_record[str(k)] = v.isoformat()
                    elif isinstance(v, (str, int, float, bool)):
                        clean_record[str(k)] = v
                    else:
                        clean_record[str(k)] = str(v)
                preview_rows.append(clean_record)
        except Exception as err:
            logger.warning(f"Could not extract preview rows for {dataset_id}: {err}")

        return DatasetOverviewResponse(
            dataset_id=meta["dataset_id"],
            filename=meta["filename"],
            rows=meta["rows"],
            columns=meta["columns"],
            column_names=meta["column_names"],
            file_type=meta["file_type"],
            missing_values=meta["missing_values"],
            duplicate_rows=meta["duplicate_rows"],
            memory_usage_bytes=meta["memory_usage_bytes"],
            preview_rows=preview_rows
        )

    @classmethod
    def load_raw_dataset(cls, dataset_id: str) -> tuple[pd.DataFrame, dict]:
        """Load the raw dataset as DataFrame and return alongside metadata."""
        dataset_dir = cls.get_dataset_dir(dataset_id)
        metadata_path = dataset_dir / "metadata.json"

        if not metadata_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Metadata for dataset '{dataset_id}' is missing."
            )

        with open(metadata_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        stored_file_path = dataset_dir / meta["stored_file"]
        if not stored_file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Underlying raw file for dataset '{dataset_id}' is missing."
            )

        df = cls._read_dataframe(stored_file_path, meta["file_type"])
        return df, meta

