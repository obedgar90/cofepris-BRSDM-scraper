"""Normalization utilities for BRSDM XLSX dataset."""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd

from cofepris_brsdm_scraper.exceptions import EmptyDatasetError, MissingColumnError
from cofepris_brsdm_scraper.transform.column_mapping import EXPECTED_COLUMNS


def normalize_header(header: str) -> str:
    """Normalize source header to snake_case ASCII."""
    ascii_header = unicodedata.normalize("NFKD", header).encode("ascii", "ignore").decode("ascii")
    no_symbols = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_header)
    return re.sub(r"_+", "_", no_symbols.strip("_")).lower()


class Normalizer:
    """Read and normalize COFEPRIS Excel dataset."""

    def __init__(self, expected_columns: tuple[str, ...] = EXPECTED_COLUMNS) -> None:
        self._expected_columns = expected_columns

    def normalize(self, excel_path: Path) -> pd.DataFrame:
        """Load an XLSX file and return normalized DataFrame."""
        dataframe = pd.read_excel(excel_path)
        dataframe.columns = [normalize_header(str(col)) for col in dataframe.columns]

        missing_columns = [
            column for column in self._expected_columns if column not in dataframe.columns
        ]
        if missing_columns:
            missing_joined = ", ".join(sorted(missing_columns))
            raise MissingColumnError(f"Missing required columns: {missing_joined}")

        normalized = dataframe[list(self._expected_columns)].copy()
        if normalized.empty:
            raise EmptyDatasetError("Dataset has no rows after normalization.")

        if "fecha_emision" in normalized.columns:
            normalized["fecha_emision"] = pd.to_datetime(
                normalized["fecha_emision"], errors="coerce"
            )

        return normalized
