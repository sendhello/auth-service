from async_fastapi_jwt_auth import AuthJWT
from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    authjwt_secret_key: str = Field("secret", validation_alias="SECRET_KEY")


@AuthJWT.load_config
def get_config():
    return TestSettings()


test_settings = TestSettings()
