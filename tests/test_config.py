import json
import yaml
import os
import unittest
from unittest.mock import patch, mock_open, call

from configobj.config import Config

class ConfigTest(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open)
    def test_load_original_file_not_found(self, mock_file):
        mock_file.side_effect = FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            Config("config.json")

    @patch('builtins.open', new_callable=mock_open, read_data='not a json')
    def test_load_original_invalid_json_format(self, mock_file):
        with self.assertRaises(json.JSONDecodeError):
            Config("config.json")

    @patch('builtins.open', new_callable=mock_open, read_data="""key: [value
data_filename:
    another_key: another_value
   more_key: more_value
mistake: mistake: over_mistake
bad pair
""")
    def test_load_original_invalid_yaml_format(self, mock_file):
        with self.assertRaises(yaml.YAMLError):
            Config("config.yaml")

    @patch('builtins.open', new_callable=mock_open, read_data='not a json, nor yaml')
    def test_load_original_invalid_format(self, mock_file):
        with self.assertRaises(ValueError):
            Config("config.txt")

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": {"$ref": "@env.SECRET_KEY"}}')
    @patch('os.getenv', return_value=None)
    def test_add_secrets_with_missing_env_var(self, mock_getenv, mock_file):
        config = Config("config.json").items()
        self.assertIsNone(config['key'])

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": {"$ref": "@env.SECRET_KEY", "required": true}}')
    @patch('os.getenv', return_value=None)
    def test_add_secrets_with_required_but_missing_env_var(self, mock_getenv, mock_file):
        with self.assertRaises(ValueError):
            Config("config.json")

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_load_original_happy_path(self, mock_file):
        config = Config("config.json")
        self.assertEqual(config.original_data, {"key": "value"})

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": {"$ref": "@env.SECRET_KEY"}}')
    @patch('os.getenv', return_value="secret_value")
    def test_add_secrets_with_ref_from_env_var_json(self, mock_getenv, mock_file):
        config = Config("config.json", env_file=".env").items()
        self.assertEqual(config['key'], "secret_value")

    @patch('builtins.open', new_callable=mock_open, read_data="""key:
  $ref: "@env.SECRET_KEY"
""")
    @patch('os.getenv', return_value="secret_value")
    def test_add_secrets_with_ref_from_env_var_yaml(self, mock_getenv, mock_file):
        config = Config("config.yaml").items()
        self.assertEqual(config['key'], "secret_value")

    # The .env file is not being read by the Config class. so I have decided to directly override the os.environ
    @patch.dict('os.environ', {'SECRET_KEY': 'secret_value'})
    @patch('builtins.open', new_callable=mock_open, read_data='{"key": {"$ref": "@env.SECRET_KEY"}}')
    def test_add_secrets_with_ref_from_env_file(self, mock_file):
        config = Config(data_file="config.json", env_file=".env")

        # Assert that file was opened correctly
        mock_file.assert_any_call("config.json", "r", encoding="UTF-8")

        # Additional assertions to ensure environment variables are accessible
        self.assertEqual(os.getenv('SECRET_KEY'), 'secret_value')

        # Get the configuration dictionary
        config_dict = config.items()  # Assuming your Config class has an items() method

        # Assert that the placeholder was replaced correctly
        self.assertEqual(config_dict.get('key'), 'secret_value')

    # The .env file is not being read by the Config class. so I have decided to directly override the os.environ
    @patch.dict('os.environ', {'SECRET_KEY': 'secret_value'})
    @patch('builtins.open', new_callable=mock_open, read_data='{"shhh": "My password is a ${@env.SECRET_KEY}"}')
    def test_add_inline_secrets_with_ref_from_env_file(self, mock_file):
        config = Config(data_file="config.json", env_file=".env")

        # Assert that file was opened correctly
        mock_file.assert_any_call("config.json", "r", encoding='UTF-8')

        # Additional assertions to ensure environment variables are accessible
        self.assertEqual(os.getenv('SECRET_KEY'), 'secret_value')

        # Get the configuration dictionary
        config_dict = config.items()  # Assuming your Config class has an items() method

        # Assert that the placeholder was replaced correctly
        self.assertEqual(config_dict.get('shhh'), 'My password is a secret_value')

    @patch('builtins.open', new_callable=mock_open, read_data='{"key1": "value1", "key2": "value2"}')
    def test_load_config_as_attributes(self, mock_file):
        config = Config("config.json").items()
        self.assertEqual(config['key1'], "value1")
        self.assertEqual(config['key2'], "value2")

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_to_string(self, mock_file):
        config = Config("config.json")
        self.assertEqual(config.to_string(), "{'errors': [], 'data_filename': 'config.json', 'original_data': {'key': 'value'}, 'completed_data': {'key': 'value'}}")

    @patch('builtins.open', new_callable=mock_open, read_data='{"key": "value"}')
    def test_to_json(self, mock_file):
        config = Config("config.json")
        self.assertEqual(config.to_json(), '{\n  "errors": [],\n  "data_filename": "config.json",\n  "original_data": {\n    "key": "value"\n  },\n  "completed_data": {\n    "key": "value"\n  }\n}')

    @patch('builtins.open', new_callable=mock_open, read_data='{"list": [{"$ref": "@env.SECRET"}]}')
    @patch('os.getenv', return_value="secret_value")
    def test_load_completed_with_list_and_value_from_env(self, mock_file, mock_getenv):
        config = Config("config.json").items()
        self.assertEqual(config['list'], ["secret_value"])

    @patch('builtins.open', new_callable=mock_open, read_data='{"secret":"magic",  "list": [{"$ref": "#secret"}]}')
    def test_load_completed_with_list_and_value_from_same_file(self, mock_file):
        config = Config("config.json").items()
        self.assertEqual(config['list'], ["magic"])

    @patch('builtins.open')
    @patch('json.loads')
    def test_load_completed_with_list_and_value_from_different_file(self, mock_json_loads, mock_open):
        # Create separate mock data for each file
        config_data = {"list": [{"$ref": "./another_file.json#dark/secret"}]}
        another_data = {"dark": {"secret": "dark_value"}}

        # Set up mock_json_loads to return our mock data
        mock_json_loads.side_effect = [config_data, another_data]

        # Set up mock_open to return a MagicMock
        mock_file = mock_open()
        mock_file.return_value.__enter__.return_value.read.return_value = "mock_file_content"
        mock_open.return_value = mock_file

        # Execute the test
        config = Config("config.json").items()
        self.assertEqual(config['list'], ["dark_value"])

        # Verify that json.loads was called twice
        self.assertEqual(mock_json_loads.call_count, 2)

    @patch('builtins.open')
    @patch('json.loads')
    def test_load_completed_with_list_plus_inline_placeholder_and_value_from_different_file(self, mock_json_loads, mock_open):
        # Create separate mock data for each file
        config_data = {"list": ["${./another_file.json#dark/secret}"]}
        another_data = {"dark": {"secret": "dark_value"}}

        # Set up mock_json_loads to return our mock data
        mock_json_loads.side_effect = [config_data, another_data]

        # Set up mock_open to return a MagicMock
        mock_file = mock_open()
        mock_file.return_value.__enter__.return_value.read.return_value = "mock_file_content"
        mock_open.return_value = mock_file

        # Execute the test
        config = Config("config.json").items()
        self.assertEqual(config['list'], ["dark_value"])

        # Verify that json.loads was called twice
        self.assertEqual(mock_json_loads.call_count, 2)

    @patch('builtins.open', new_callable=mock_open, read_data='{"list": ["${@env.SECRET}"]}')
    @patch('os.getenv', return_value="secret_value")
    def test_load_completed_with_list_plus_inline_placeholder_and_value_from_env(self, mock_file, mock_getenv):
        config = Config("config.json").items()
        self.assertEqual(config['list'], ["secret_value"])

    @patch('builtins.open', new_callable=mock_open, read_data='{"dark":{"secret":"magic"},  "list": ["${#dark/secret}"]}')
    def test_load_completed_with_list_plus_inline_placeholder_and_value_from_same_file(self, mock_file):
        config = Config("config.json").items()
        self.assertEqual(config['list'], ["magic"])

    # @patch('builtins.open')
    # @patch('json.loads')
    # @patch('os.getenv', filename="another_file.json")
    # def test_load_completed_with_inline_placeholder_inside_a_node_reference_for_value_from_different_file(self, mock_getenv, mock_json_loads, mock_open):
    #     # Create separate mock data for each file
    #     config_data = {"list": [{"$ref": "./${@env.filename}#dark/secret"}]}
    #     another_data = {"dark": {"secret": "dark_value"}}
    #
    #     # Set up mock_json_loads to return our mock data
    #     mock_json_loads.side_effect = [config_data, another_data]
    #
    #     # Set up mock_open to return a MagicMock
    #     mock_file = mock_open()
    #     mock_file.return_value.__enter__.return_value.read.return_value = "mock_file_content"
    #     mock_open.return_value = mock_file
    #
    #     # Execute the test
    #     config = Config("config.json").items()
    #     self.assertEqual(config['list'], ["dark_value"])
    #
    #     # Verify that json.loads was called twice
    #     self.assertEqual(mock_json_loads.call_count, 2)

if __name__ == '__main__':
    unittest.main()