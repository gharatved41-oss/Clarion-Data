import json
import logging
import os
import io
import uuid
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple
from utils.test_datasets import generate_test_datasets

logger = logging.getLogger("dataset_store")

class DatasetStore:
    """In-memory and disk-backed dataset storage manager unifying Person 1 and Person 2 modules."""
    def __init__(self):
        self._datasets: Dict[str, pd.DataFrame] = {}
        self._metadata: Dict[str, dict] = {}
        # Pre-seed with benchmark datasets
        self.seed_test_datasets()

    def _sync_to_disk(self, dataset_id: str, df: pd.DataFrame, filename: str = "dataset.csv"):
        """Sync dataframe and metadata to disk for Person 1 services."""
        try:
            from app.core.config import settings
            dataset_dir = settings.uploads_dir / dataset_id
            dataset_dir.mkdir(parents=True, exist_ok=True)
            orig_csv = dataset_dir / "original.csv"
            if not orig_csv.exists():
                df.to_csv(orig_csv, index=False)
            metadata_file = dataset_dir / "metadata.json"
            if not metadata_file.exists():
                meta = {
                    "dataset_id": dataset_id,
                    "filename": filename,
                    "file_type": ".csv",
                    "stored_file": "original.csv",
                    "rows": int(len(df)),
                    "columns": int(len(df.columns)),
                    "column_names": [str(c) for c in df.columns],
                    "missing_values": int(df.isna().sum().sum()),
                    "duplicate_rows": int(df.duplicated().sum()),
                    "memory_usage_bytes": int(df.memory_usage(deep=True).sum())
                }
                with open(metadata_file, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2)
        except Exception as exc:
            logger.debug(f"Disk sync skipped for {dataset_id}: {exc}")

    def seed_test_datasets(self):
        test_dfs = generate_test_datasets()
        for name, df in test_dfs.items():
            dataset_id = f"test-{name}"
            self._datasets[dataset_id] = df
            self._metadata[dataset_id] = {
                "name": f"{name}.csv",
                "rows": len(df),
                "columns": len(df.columns)
            }
            self._sync_to_disk(dataset_id, df, f"{name}.csv")

    def save_dataset(self, df: pd.DataFrame, filename: str = "dataset.csv") -> str:
        dataset_id = str(uuid.uuid4())[:8]
        self._datasets[dataset_id] = df
        self._metadata[dataset_id] = {
            "name": filename,
            "rows": len(df),
            "columns": len(df.columns)
        }
        self._sync_to_disk(dataset_id, df, filename)
        return dataset_id

    def load_csv_bytes(self, content: bytes, filename: str = "dataset.csv") -> str:
        fn_lower = (filename or "").lower()
        # Detect Excel formats via file extension or magic bytes (PK zip header for XLSX, OLE for XLS)
        if (
            fn_lower.endswith((".xlsx", ".xls", ".xlsm"))
            or content.startswith(b"PK\x03\x04")
            or content.startswith(b"\xd0\xcf\x11\xe0")
        ):
            df = pd.read_excel(io.BytesIO(content))
        else:
            try:
                df = pd.read_csv(io.BytesIO(content))
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(io.BytesIO(content), encoding="latin1")
                except Exception:
                    df = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")
        return self.save_dataset(df, filename)

    def get_dataset(self, dataset_id: str) -> Optional[pd.DataFrame]:
        if dataset_id in self._datasets:
            return self._datasets[dataset_id]

        # Check disk: first try cleaned.csv from processed_dir
        try:
            from app.core.config import settings
            cleaned_file = settings.processed_dir / dataset_id / "cleaned.csv"
            if cleaned_file.exists():
                df = pd.read_csv(cleaned_file)
                self._datasets[dataset_id] = df
                return df

            # Next check raw dataset in uploads_dir
            upload_dir = settings.uploads_dir / dataset_id
            meta_file = upload_dir / "metadata.json"
            if meta_file.exists():
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                stored_file = upload_dir / meta.get("stored_file", "original.csv")
                if stored_file.exists():
                    ext = meta.get("file_type", stored_file.suffix.lower())
                    if ext == ".csv":
                        try:
                            df = pd.read_csv(stored_file)
                        except UnicodeDecodeError:
                            df = pd.read_csv(stored_file, encoding="latin1")
                    elif ext in [".xlsx", ".xls"]:
                        engine = "openpyxl" if ext == ".xlsx" else "xlrd"
                        df = pd.read_excel(stored_file, engine=engine)
                    else:
                        df = pd.read_csv(stored_file)
                    self._datasets[dataset_id] = df
                    if dataset_id not in self._metadata:
                        self._metadata[dataset_id] = {
                            "name": meta.get("filename", f"{dataset_id}.csv"),
                            "rows": int(len(df)),
                            "columns": int(len(df.columns))
                        }
                    return df
        except Exception as exc:
            logger.debug(f"Could not load dataset {dataset_id} from disk: {exc}")

        return None

    def get_metadata(self, dataset_id: str) -> Optional[dict]:
        if dataset_id in self._metadata:
            return self._metadata[dataset_id]
        try:
            from app.core.config import settings
            upload_meta = settings.uploads_dir / dataset_id / "metadata.json"
            if upload_meta.exists():
                with open(upload_meta, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                self._metadata[dataset_id] = {
                    "name": meta.get("filename", f"{dataset_id}.csv"),
                    "rows": meta.get("rows", 0),
                    "columns": meta.get("columns", 0)
                }
                return self._metadata[dataset_id]
        except Exception:
            pass
        return None

    def list_datasets(self) -> Dict[str, dict]:
        try:
            from app.core.config import settings
            if settings.uploads_dir.exists():
                for d in settings.uploads_dir.iterdir():
                    if d.is_dir() and d.name not in self._metadata:
                        meta_file = d / "metadata.json"
                        if meta_file.exists():
                            try:
                                with open(meta_file, "r", encoding="utf-8") as f:
                                    m = json.load(f)
                                self._metadata[d.name] = {
                                    "name": m.get("filename", f"{d.name}.csv"),
                                    "rows": m.get("rows", 0),
                                    "columns": m.get("columns", 0)
                                }
                            except Exception:
                                pass
        except Exception:
            pass
        return self._metadata

# Global singleton dataset store
dataset_store = DatasetStore()

