
import pandas as pd
from database import Database


class DataExtractor:

    def __init__(self):
        self.engine = Database().engine()

    def extract_rfm(self):
        query = """
            SELECT *
            FROM vw_rfm_customers
        """
        return pd.read_sql_query(query, con=self.engine)
