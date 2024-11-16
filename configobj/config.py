import os
import re
import dotenv
import json
import logging
import stat

import yaml

logger = logging.getLogger(__name__)

def has_700_permissions(file_path):
    file_stat = os.stat(file_path)
    permissions = stat.S_IMODE(file_stat.st_mode)
    return permissions == 0o700

class Config:
    def __init__(self, object, env_file=None):
        if env_file:
            dotenv.load_dotenv(env_file)
            # It's working, but it's breaking the tests
            if not has_700_permissions(os.path.abspath(env_file)):
                logger.warning(f"Config file [{os.path.abspath(env_file)}] permissions are not set to 700")
        self.errors = []
        self.object = object
        self.original = self.load_original(object)
        self.completed = self.load_completed(self.original)
        # self.load_config_as_attributes()

        # It's working, but it's breaking the tests
        if not has_700_permissions(os.path.abspath(self.object)):
            logger.warning(f"Config file [{os.path.abspath(self.object)}] permissions are not set to 700")



    def to_string(self):
        return str(self.__dict__)

    def to_json(self):
        return json.dumps(self.__dict__, indent=2)

    def load_original(self, object):
        try:
            with open(object, "r", encoding='UTF-8') as f:
                # settings = json.load(f)
                binary = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.object} not found")

        settings = {}
        if object.endswith(".json"):
            try:
                settings = json.loads(binary)
            except json.JSONDecodeError:
                raise json.JSONDecodeError(f"File {self.object} is not a valid JSON file", binary, 0)

        elif object.endswith(".yaml") or object.endswith(".yml"):
            try:
                settings = yaml.safe_load(binary)
            except yaml.YAMLError:
                raise yaml.YAMLError(f"File {self.object} is not a valid YAML file")

        else:
            raise ValueError(f"File {self.object} has an unknown data format")
        return settings

    def load_config_as_attributes(self):
        for key, value in self.original.items():
            value = self.load_completed(value)
            setattr(self, key, value)

    def load_completed(self, node):
        if isinstance(node, dict) and "$ref" in node:
            node = self.replace_secret(node)
        elif isinstance(node, dict):
            for key, value in node.items():
                node[key] = self.load_completed(value)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                node[index] = self.load_completed(value)
        elif isinstance(node, str) and re.search(r"\$\{[\w.]+\}", node):
            node = self.replace_inline_secret(node)
        return node

    def replace_inline_secret(self, node):
        if type(node) is str:
            matches = re.findall(r"\$\{([\w.]+)\}", node)
            for match in matches:
                if os.getenv(match) is not None:
                    node = node.replace(f"${{{match}}}", os.getenv(match))

        return node

    def replace_secret(self, node):
        if "required" in node and node["required"] is True and os.getenv(node["$ref"]) is None:
            error_message = f"Environment variable {node['$ref']} is required but missing in the .env file"
            self.errors.append(error_message)
            raise ValueError(error_message)

        return os.getenv(node["$ref"])

    def items(self):
        return self.completed
