import unittest
from omotes_rest.config import POSTGRESConfig


class MyTest(unittest.TestCase):
    def test__construct_orchestrator_config__no_exception(self) -> None:
        # Arrange

        # Act
        result = POSTGRESConfig()

        # Assert
        self.assertIsNotNone(result)
