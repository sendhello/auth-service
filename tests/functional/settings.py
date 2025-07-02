from async_fastapi_jwt_auth import AuthJWT
from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    authjwt_secret_key: str = Field("secret", env="SECRET_KEY")


@AuthJWT.load_config
def get_config():
    return TestSettings()


test_settings = TestSettings()
