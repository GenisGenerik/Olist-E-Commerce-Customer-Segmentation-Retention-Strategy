
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class RFMAnalysis:

    def __init__(self):
        self.model = None

    def _validasi_fitur(self, fitur: pd.DataFrame):

        if not isinstance(fitur, pd.DataFrame):
            raise TypeError("Fitur harus berupa DataFrame.")

        if fitur.empty:
            raise ValueError("Data fitur kosong.")

        if fitur.columns.duplicated().any():
            raise ValueError("Nama kolom fitur tidak boleh duplikat.")

        if not all(
            pd.api.types.is_numeric_dtype(fitur[col])
            for col in fitur.columns
        ):
            raise TypeError("Semua fitur harus bertipe numerik.")

        if not np.isfinite(fitur.to_numpy()).all():
            raise ValueError("Fitur mengandung nilai tidak valid.")

    def kelompokan_rfm(
        self,
        df: pd.DataFrame,
        fitur: pd.DataFrame,
        jumlah_kelompok: int = 4
    ) -> pd.DataFrame:

        self._validasi_fitur(fitur)

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Data harus berupa DataFrame.")

        if df.empty:
            raise ValueError("Data customer kosong.")

        if len(df) != len(fitur):
            raise ValueError("Jumlah baris df dan fitur tidak sama.")

        if not df.index.equals(fitur.index):
            raise ValueError("Index df dan fitur tidak sesuai.")

        if not isinstance(jumlah_kelompok, (int, np.integer)):
            raise TypeError("Jumlah cluster harus berupa integer.")

        if not 2 <= jumlah_kelompok < len(fitur):
            raise ValueError("Jumlah cluster tidak valid.")

        self.model = KMeans(
            n_clusters=jumlah_kelompok,
            random_state=42,
            n_init=10
        )

        df = df.copy()
        df["kelompok"] = self.model.fit_predict(fitur)

        return df

    def elbow_method(
        self,
        fitur: pd.DataFrame,
        max_kelompok: int = 10
    ) -> pd.DataFrame:

        self._validasi_fitur(fitur)

        if not isinstance(max_kelompok, (int, np.integer)):
            raise TypeError("Batas cluster harus berupa integer.")

        if max_kelompok < 1:
            raise ValueError("Batas cluster minimal 1.")

        batas = min(max_kelompok, len(fitur))

        inertia = []

        for k in range(1, batas + 1):

            model = KMeans(
                n_clusters=k,
                random_state=42,
                n_init=10
            )

            model.fit(fitur)
            inertia.append(model.inertia_)

        hasil = pd.DataFrame({
            "jumlah_kelompok": range(1, batas + 1),
            "inertia": inertia
        })

        plt.figure(figsize=(8, 5))
        plt.plot(
            hasil["jumlah_kelompok"],
            hasil["inertia"],
            marker="o"
        )

        plt.xlabel("Jumlah Kelompok")
        plt.ylabel("Inertia")
        plt.title("Elbow Method")
        plt.xticks(range(1, batas + 1))
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        return hasil

    def cek_silhouette_score(
        self,
        fitur: pd.DataFrame,
        max_kelompok: int = 10,
        sample_size: int = 10000
    ) -> pd.DataFrame:

        self._validasi_fitur(fitur)

        if not isinstance(max_kelompok, (int, np.integer)):
            raise TypeError("Batas cluster harus berupa integer.")

        if not isinstance(sample_size, (int, np.integer)):
            raise TypeError("Sample size harus berupa integer.")

        if max_kelompok < 2:
            raise ValueError("Batas cluster minimal 2.")

        if sample_size < 2:
            raise ValueError("Sample size minimal 2.")

        batas = min(max_kelompok, len(fitur) - 1)
        ukuran_sampel = min(sample_size, len(fitur))

        hasil = []

        for k in range(2, batas + 1):

            model = KMeans(
                n_clusters=k,
                random_state=42,
                n_init=10
            )

            label = model.fit_predict(fitur)

            score = silhouette_score(
                fitur,
                label,
                sample_size=ukuran_sampel,
                random_state=42
            )

            hasil.append({
                "jumlah_kelompok": k,
                "silhouette_score": score
            })

        return pd.DataFrame(hasil)

    def summary(self, df: pd.DataFrame) -> pd.DataFrame:

        kolom_wajib = [
            "kelompok",
            "hari_semenjak_pembelian_terakhir",
            "frekuensi_pembelian",
            "total_nilai_pembelian",
            "customer_unique_id"
        ]

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Data harus berupa DataFrame.")

        kolom_hilang = set(kolom_wajib) - set(df.columns)

        if kolom_hilang:
            raise ValueError(
                f"Kolom tidak ditemukan: {kolom_hilang}"
            )

        if df.empty:
            raise ValueError("Data customer kosong.")

        hasil = df.groupby("kelompok").agg(
            hari_semenjak_pembelian_terakhir=(
                "hari_semenjak_pembelian_terakhir",
                "median"
            ),
            frekuensi_pembelian=(
                "frekuensi_pembelian",
                "median"
            ),
            total_nilai_pembelian=(
                "total_nilai_pembelian",
                "median"
            ),
            total_customer=(
                "customer_unique_id",
                "nunique"
            )
        )

        hasil["persentase_customer"] = (
            hasil["total_customer"]
            / hasil["total_customer"].sum()
            * 100
        )

        return hasil

    def segmentasi_customer(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        kolom_wajib = [
            "kelompok",
            "hari_semenjak_pembelian_terakhir",
            "frekuensi_pembelian",
            "total_nilai_pembelian"
        ]

        if not isinstance(df, pd.DataFrame):
            raise TypeError("Data harus berupa DataFrame.")

        kolom_hilang = set(kolom_wajib) - set(df.columns)

        if kolom_hilang:
            raise ValueError(
                f"Kolom tidak ditemukan: {kolom_hilang}"
            )

        if df.empty:
            raise ValueError("Data customer kosong.")

        df = df.copy()

        profil = df.groupby("kelompok").agg(
            recency=(
                "hari_semenjak_pembelian_terakhir",
                "median"
            ),
            frequency=("frekuensi_pembelian", "median"),
            monetary=("total_nilai_pembelian", "median")
        )

        batas_recency = profil["recency"].median()
        batas_frequency = profil["frequency"].median()
        batas_monetary = profil["monetary"].median()

        def tentukan_segmen(row):

            if row["frequency"] > batas_frequency:
                return "Repeat Customers"

            elif row["recency"] <= batas_recency:
                return "Recent Customers"

            elif row["monetary"] > batas_monetary:
                return "At Risk High Value"

            else:
                return "Hibernating"

        profil["segmen_customer"] = profil.apply(
            tentukan_segmen,
            axis=1
        )

        df["segmen_customer"] = df["kelompok"].map(
            profil["segmen_customer"]
        )

        return df
