"""Normalizer unit tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cofepris_brsdm_scraper.exceptions import MissingColumnError
from cofepris_brsdm_scraper.transform.column_mapping import EXPECTED_COLUMNS
from cofepris_brsdm_scraper.transform.normalizer import Normalizer, normalize_header


def test_normalize_header_removes_accents_symbols_and_uses_snake_case() -> None:
    """Header normalization must output snake_case ASCII."""
    assert normalize_header("Subgrupo QuÍmico") == "subgrupo_quimico"
    assert normalize_header("Número de Registro") == "numero_de_registro"


def test_normalize_reads_sample_excel_and_returns_29_columns() -> None:
    """Normalizer should preserve required 29-column shape."""
    normalizer = Normalizer()
    sample_path = Path("info/Visor_Registros_Medicamentos.xlsx")
    dataframe = normalizer.normalize(sample_path)
    assert len(dataframe.columns) == 29
    assert list(dataframe.columns) == list(EXPECTED_COLUMNS)
    assert len(dataframe.index) > 0


def test_normalize_raises_missing_column_error_when_required_column_absent(
    tmp_path: Path,
) -> None:
    """Normalizer must fail fast if required columns are absent."""
    columns = list(EXPECTED_COLUMNS[:-1])
    dataframe = pd.DataFrame([{col: "x" for col in columns}])
    excel_path = tmp_path / "missing-column.xlsx"
    dataframe.to_excel(excel_path, index=False)

    with pytest.raises(MissingColumnError):
        Normalizer().normalize(excel_path)


def test_normalize_casts_fecha_emision_to_datetime() -> None:
    """fecha_emision should be converted to datetime."""
    normalizer = Normalizer()
    dataframe = normalizer.normalize(Path("info/Visor_Registros_Medicamentos.xlsx"))
    assert str(dataframe["fecha_emision"].dtype).startswith("datetime64")
