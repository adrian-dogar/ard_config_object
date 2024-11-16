import os
import re
import dotenv
import json
import logging

import yaml

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, data_file, env_file=None):
        """

        :param data_file: route and filename for a json or yaml file
        :param env_file: optional. route and filename for a .env file to load the extra data
        """
        if env_file:
            dotenv.load_dotenv(env_file)
        self.errors = []
        self.data_filename = data_file
        self.original_data = self.load_original()
        self.completed_data = self.fill_in(self.original_data)
        # self.load_config_as_attributes_of_current_class()

    def load_config_as_attributes_of_current_class(self):
        for key, value in self.original_data.items():
            value = self.fill_in(value)
            setattr(self, key, value)

    def to_string(self):
        return str(self.__dict__)

    def to_json(self):
        return json.dumps(self.__dict__, indent=2)

    def load_original(self):
        try:
            with open(self.data_filename, "r", encoding='UTF-8') as f:
                binary = f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.data_filename} not found")

        if self.data_filename.endswith(".json"):
            try:
                settings = json.loads(binary)
            except json.JSONDecodeError:
                raise json.JSONDecodeError(f"File {self.data_filename} is not a valid JSON file", binary, 0)

        elif self.data_filename.endswith(".yaml") or self.data_filename.endswith(".yml"):
            try:
                settings = yaml.safe_load(binary)
            except yaml.YAMLError:
                raise yaml.YAMLError(f"File {self.data_filename} is not a valid YAML file")

        else:
            raise ValueError(f"File {self.data_filename} has an unknown data format")
        return settings

    def fill_in(self, node):
        if isinstance(node, dict) and "$ref" in node:
            node = self._replace_node_style(node)
        elif isinstance(node, dict):
            for key, value in node.items():
                node[key] = self.fill_in(value)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                node[index] = self.fill_in(value)
        elif isinstance(node, str) and re.search(r"\$\{([\@\#\/\w\.\-]+)\}", node):
            node = self._replace_inline_style(node)
        return node

    def _replace_inline_style(self, ref):
        matches = re.findall(r"\$\{([\@\#\/\w\.\-]+)\}", ref)
        for match in matches:
            value = self._fetch_value(match)
            ref = ref.replace(f"${{{match}}}", value)

        return ref

    def _replace_node_style(self, node):
        if "required" in node and node["required"] is True and os.getenv(node["$ref"]) is None:
            error_message = f"Environment variable {node['$ref']} is required but missing in the .env file"
            self.errors.append(error_message)
            raise ValueError(error_message)

        return self._fetch_value(node["$ref"])

    def _fetch_value(self, ref):
        value = ''
        if ref.startswith("@env."):
            ref = ref.replace("@env.", "")
            value = os.getenv(ref)

        elif ref.startswith("#"):
            ref = ref.replace("#", "")
            # ref is now a path to a value in the original_data
            value = self._fetch_nested_value(ref)

        elif "#" in ref:
            filepath, inner_route = ref.split("#")
            sub_file = Config(filepath).items()
            value = self._fetch_nested_value(inner_route, sub_file)

        return value

    def _fetch_nested_value(self, ref, file=None):
        # remove the leading slash if any
        if ref.startswith("/"):
            ref = ref[1:]
        keys = ref.split("/")
        value = self.original_data if file is None else file
        for key in keys:
            value = value[key]
        return value

    def items(self):
        """
        Return the dictionary with the data from the config file, with all the placeholders replaced with referenced values
        :return: dict
        """
        return self.completed_data
