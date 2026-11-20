
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler


class RFMTransform:

    RFM_COLUMNS = [
        "hari_semenjak_pembelian_terakhir",
        "frekuensi_pembelian",
        "total_nilai_pembelian"
    ]

    def __init__(self):
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.X = None
        self.X_log = None
        self.X_scaled = None

    def _validasi_data(self, df: pd.DataFrame, kolom=None):

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input harus berupa DataFrame.")

        if df.empty:
            raise ValueError("DataFrame kosong.")

        if kolom is None:
            kolom = self.RFM_COLUMNS

        kolom_hilang = set(kolom) - set(df.columns)

        if kolom_hilang:
            raise ValueError(
                f"Kolom tidak ditemukan: {kolom_hilang}"
            )

        data = df[kolom]

        if data.isnull().any().any():
            raise ValueError("Data mengandung missing value.")

        if not all(
            pd.api.types.is_numeric_dtype(data[col])
            for col in kolom
        ):
            raise TypeError("Semua fitur harus bertipe numerik.")

        if not np.isfinite(data.to_numpy()).all():
            raise ValueError("Data mengandung nilai inf atau -inf.")

        if (data < 0).any().any():
            raise ValueError("Fitur RFM tidak boleh memiliki nilai negatif.")

    def fitur(self, df: pd.DataFrame) -> pd.DataFrame:

        self._validasi_data(df)

        return df[self.RFM_COLUMNS].copy()

    def transformasi_log_fitur(
        self,
        X: pd.DataFrame
    ) -> pd.DataFrame:

        self._validasi_data(X, X.columns.tolist())

        return np.log1p(X)

    def standarisasi_skala_fitur(
        self,
        X_log: pd.DataFrame
    ) -> pd.DataFrame:

        self._validasi_data(X_log, X_log.columns.tolist())

        X_scaled = self.scaler.fit_transform(X_log)

        self.is_fitted = True

        return pd.DataFrame(
            X_scaled,
            columns=X_log.columns,
            index=X_log.index
        )

    def transform_skala_fitur(
        self,
        X_log: pd.DataFrame
    ) -> pd.DataFrame:

        if not self.is_fitted:
            raise RuntimeError("Scaler belum dilatih.")

        self._validasi_data(X_log, X_log.columns.tolist())

        if list(X_log.columns) != list(self.scaler.feature_names_in_):
            raise ValueError(
                "Urutan atau nama fitur tidak sesuai dengan data training."
            )

        X_scaled = self.scaler.transform(X_log)

        return pd.DataFrame(
            X_scaled,
            columns=X_log.columns,
            index=X_log.index
        )

    def siapkan_fitur(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        self.X = self.fitur(df)

        self.X_log = self.transformasi_log_fitur(
            self.X
        )

        self.X_scaled = self.standarisasi_skala_fitur(
            self.X_log
        )

        return self.X_scaled

    def hitung_skor_rfm(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        self._validasi_data(df)

        df = df.copy()

        ranking = df[self.RFM_COLUMNS].rank(
            method="average",
            pct=True
        )

        df["R_skor"] = (
            6 - np.ceil(
                ranking["hari_semenjak_pembelian_terakhir"] * 5
            )
        ).astype(int)

        df["F_skor"] = np.ceil(
            ranking["frekuensi_pembelian"] * 5
        ).astype(int)

        df["M_skor"] = np.ceil(
            ranking["total_nilai_pembelian"] * 5
        ).astype(int)

        return df

    def gabung_skor_rfm(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        df = df.copy()

        kolom_skor = [
            "R_skor",
            "F_skor",
            "M_skor"
        ]

        self._validasi_data(df, kolom_skor)

        if not df[kolom_skor].isin(range(1, 6)).all().all():
            raise ValueError("Skor RFM harus berada pada rentang 1-5.")

        df["skor_RFM"] = (
            df["R_skor"].astype(str) +
            df["F_skor"].astype(str) +
            df["M_skor"].astype(str)
        )

        return df
