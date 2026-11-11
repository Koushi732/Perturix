import pytest
from pydantic import ValidationError

from app.config.settings import Settings
from app.main import validate_configuration


def test_settings_validation_fails_on_missing_secret():
    with pytest.raises(ValidationError):
        # We enforce secret_key to be present, so creating Settings without env vars and without default should fail
        Settings(_env_file=None)

def test_validate_configuration_success():
    # As long as dirs can be created, this should pass
    # Given that tests are running, we assume the environment is fine
    validate_configuration()
