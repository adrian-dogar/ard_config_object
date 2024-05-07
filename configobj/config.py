import os
import dotenv
import json


class Config:
    def __init__(self, object, env_file=".env"):
        dotenv.load_dotenv(env_file)
        self.errors = []
        self.object = object
        self.original = self.load_original()
        self.completed = self.load_completed(self.original)
        # self.load_config_as_attributes()

    def to_string(self):
        return str(self.__dict__)

    def to_json(self):
        return json.dumps(self.__dict__, indent=2)

    def load_original(self):
        try:
            with open(self.object) as f:
                settings = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File {self.object} not found")
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
        return node

    def replace_secret(self, node):
        if "required" in node and node["required"] is True and os.getenv(node["$ref"]) is None:
            error_message = f"Environment variable {node['$ref']} is required but missing in the .env file"
            self.errors.append(error_message)
            raise ValueError(error_message)

        return os.getenv(node["$ref"])

    def items(self):
        return self.completed
