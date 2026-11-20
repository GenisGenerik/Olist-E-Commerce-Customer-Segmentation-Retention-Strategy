
from pathlib import Path

import pandas as pd

from database import Database


class ResultStorage:

    def __init__(self):
        self.database = Database()

    def _validasi_kolom(
        self,
        df: pd.DataFrame,
        kolom: list = None
    ):

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input harus berupa DataFrame.")

        if df.empty:
            raise ValueError("DataFrame tidak boleh kosong.")

        if kolom is not None:

            if not isinstance(kolom, list) or not kolom:
                raise ValueError("Kolom harus berupa list dan tidak boleh kosong.")

            if len(kolom) != len(set(kolom)):
                raise ValueError("Kolom tidak boleh duplikat.")

            kolom_hilang = set(kolom) - set(df.columns)

            if kolom_hilang:
                raise ValueError(f"Kolom tidak ditemukan: {kolom_hilang}")

            return df[kolom].copy()

        return df.copy()

    def simpan_csv(
        self,
        df: pd.DataFrame,
        path: str,
        kolom: list = None
    ):

        if not isinstance(path, str) or not path.strip():
            raise ValueError("Path tidak boleh kosong.")

        data = self._validasi_kolom(df, kolom)

        lokasi = Path(path)
        lokasi.parent.mkdir(parents=True, exist_ok=True)

        data.to_csv(
            lokasi,
            index=False,
            encoding="utf-8-sig"
        )

    def simpan_sql(
        self,
        df: pd.DataFrame,
        nama_tabel: str,
        schema: str = "dbo",
        if_exists: str = "replace",
        kolom: list = None
    ):

        if not isinstance(nama_tabel, str) or not nama_tabel.strip():
            raise ValueError("Nama tabel tidak boleh kosong.")

        if not isinstance(schema, str) or not schema.strip():
            raise ValueError("Schema tidak boleh kosong.")

        if if_exists not in ["fail", "replace", "append"]:
            raise ValueError("if_exists harus fail, replace, atau append.")

        data = self._validasi_kolom(df, kolom)

        engine = self.database.engine()

        try:
            data.to_sql(
                name=nama_tabel,
                con=engine,
                schema=schema,
                if_exists=if_exists,
                index=False
            )
        finally:
            engine.dispose()
