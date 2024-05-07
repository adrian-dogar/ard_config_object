import json
import unittest
from unittest.mock import patch, mock_open
from configobj.config import Config


class ConfigTest(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open)
    def test_load_original_file_not_found(self, mock_file):
        mock_file.side_effect = FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            Config("config.json")

    @patch('builtins.open', new_callable=mock_open, read_data='not a json')
    def test_load_original_invalid_format(self, mock_file):
        with self.assertRaises(json.JSONDecodeError):
            Config("config.json")

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": {"$ref": "SECRET_KEY"}}')
    @patch('os.getenv', return_value=None)
    def test_add_secrets_with_missing_env_var(self, mock_getenv, mock_file):
        config = Config("config.json").items()
        self.assertIsNone(config['key'])

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": {"$ref": "SECRET_KEY", "required": true}}')
    @patch('os.getenv', return_value=None)
    def test_add_secrets_with_required_but_missing_env_var(self, mock_getenv, mock_file):
        with self.assertRaises(ValueError):
            Config("config.json")

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_original_happy_path(self, mock_file):
        config = Config("config.json")
        self.assertEqual(config.original, {"key": "value"})

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": {"$ref": "SECRET_KEY"}}')
    @patch('os.getenv', return_value="secret_value")
    def test_add_secrets_with_ref(self, mock_getenv, mock_file):
        config = Config("config.json").items()
        self.assertEqual(config['key'], "secret_value")

    @patch('builtins.open', new_callable=mock_open, read_data='{"key1": "value1", "key2": "value2"}')
    def test_load_config_as_attributes(self, mock_file):
        config = Config("config.json").items()
        self.assertEqual(config['key1'], "value1")
        self.assertEqual(config['key2'], "value2")

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_to_string(self, mock_file):
        config = Config("config.json")
        self.assertEqual(config.to_string(), "{'errors': [], 'object': 'config.json', 'original': {'key': 'value'}, 'completed': {'key': 'value'}}")

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_to_json(self, mock_file):
        config = Config("config.json")
        self.assertEqual(config.to_json(), '{\n  "errors": [],\n  "object": "config.json",\n  "original": {\n    "key": "value"\n  },\n  "completed": {\n    "key": "value"\n  }\n}')

    @patch('builtins.open', new_callable=mock_open, read_data='{"list": [{"$ref": "SECRET"}]}')
    @patch('os.getenv', return_value="secret_value")
    def test_load_completed_with_list(self, mock_file, mock_getenv):
        config = Config("config.json").items()
        self.assertEqual(config['list'], ["secret_value"])


if __name__ == '__main__':
    unittest.main()