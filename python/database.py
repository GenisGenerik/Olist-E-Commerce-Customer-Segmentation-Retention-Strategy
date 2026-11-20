
import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


class Database:

    def __init__(self):
        self.server = os.getenv("DB_SERVER", "localhost\\MSSQLSERVER01")
        self.database_name = os.getenv("DB_DATABASE", "OlistECommerceDB")
        self.driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    def _connection_string(self):
        return URL.create(
            "mssql+pyodbc",
            host=self.server,
            database=self.database_name,
            query={
                "driver": self.driver,
                "trusted_connection": "yes"
            }
        )

    def engine(self):
        return create_engine(self._connection_string())
