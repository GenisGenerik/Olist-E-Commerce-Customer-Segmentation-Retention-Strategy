
from extractor import DataExtractor
from cleaning.rfm import RFMCleaning
from transform.rfm import RFMTransform
from analysis.rfm import RFMAnalysis
from result_storage import ResultStorage


def main():
    cleaning = RFMCleaning()
    transform = RFMTransform()
    analysis = RFMAnalysis()
    result = ResultStorage()

    data = DataExtractor().extract_rfm()
    data = cleaning.jalankan_pembersihan(data)

    fitur = transform.siapkan_fitur(data)

    data = analysis.kelompokan_rfm(data, fitur, 4)
    data = analysis.segmentasi_customer(data)

    result.simpan_csv(data, "outputs/rfm_clustered.csv")
    result.simpan_sql(data, "customer_segmentation")


if __name__ == "__main__":
    main()
