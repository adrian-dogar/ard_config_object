import json
from configobj import Config
import os

print(f"initial current directory: {os.path.dirname(os.path.realpath(__file__))}")

config = Config("config.yaml", env_file=".env")

print(json.dumps(config.items(), indent=2))

expected = {
  "definitions": {
    "short_value": "short"
  },
  "element": "In-line variable test",
  "list": [
    "short",
    "variable",
    "test",
    "short_value",
    "Sem"
  ],
  "parent": {
    "child": "Sem",
    "env_ref": "Sem",
    "hardcoded": "test",
    "placeholder": "variable",
    "referenced_property": "short_value",
    "short_value": "short"
  },
  "some_info": "This is a test file for the test branch",
  "some_other_secret_info": None,
  "some_secret_info": "1234",
  "key_with_variable": "value"
}

assert config.items() == expected
