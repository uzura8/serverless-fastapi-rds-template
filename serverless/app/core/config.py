from pydantic import MySQLDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # model_config = SettingsConfigDict(
    #     # Use top level .env file (one level above ./serverless/)
    #     env_file="../.env",
    #     env_file_encoding = "utf-8"
    #     env_ignore_empty=True,
    #     extra="ignore",
    # )
    API_V1_STR: str = "/api/v1"

    MYSQL_HOST: str
    MYSQL_PORT: int = 3306
    MYSQL_USER: str
    MYSQL_PASSWORD: str = ""
    MYSQL_DBNAME: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> MySQLDsn:
        return MultiHostUrl.build(
            scheme="mysql+aiomysql",
            username=self.MYSQL_USER,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_HOST,
            port=self.MYSQL_PORT,
            path=self.MYSQL_DBNAME,
        )


settings = Settings()  # type: ignore
