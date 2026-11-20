
import pandas as pd


class RFMCleaning:

    def _validasi_data(self, df: pd.DataFrame) -> None:

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input harus berupa DataFrame.")

        if df.empty:
            raise ValueError("DataFrame tidak boleh kosong.")

        kolom_wajib = [
            "hari_semenjak_pembelian_terakhir",
            "frekuensi_pembelian",
            "total_nilai_pembelian"
        ]

        kolom_hilang = set(kolom_wajib) - set(df.columns)

        if kolom_hilang:
            raise ValueError(f"Kolom tidak ditemukan: {kolom_hilang}")

        if not all(
            pd.api.types.is_numeric_dtype(df[kolom])
            for kolom in kolom_wajib
        ):
            raise TypeError("Kolom RFM harus bertipe numerik.")

    def _hapus_data_kosong(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna().copy()

    def _hapus_duplikat(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.drop_duplicates().copy()

    def _hapus_data_belanja_tidak_valid(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        return df[df["total_nilai_pembelian"] > 0].copy()

    def _validasi_nilai_rfm(self, df: pd.DataFrame) -> None:

        if (df["hari_semenjak_pembelian_terakhir"] < 0).any():
            raise ValueError("Recency tidak boleh negatif.")

        if (df["frekuensi_pembelian"] <= 0).any():
            raise ValueError("Frequency harus lebih besar dari nol.")

        if (df["total_nilai_pembelian"] <= 0).any():
            raise ValueError("Monetary harus lebih besar dari nol.")

    def jalankan_pembersihan(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        self._validasi_data(df)

        df = self._hapus_data_kosong(df)
        df = self._hapus_duplikat(df)
        df = self._hapus_data_belanja_tidak_valid(df)

        if df.empty:
            raise ValueError("Tidak ada data tersisa setelah pembersihan.")

        self._validasi_nilai_rfm(df)

        return df
