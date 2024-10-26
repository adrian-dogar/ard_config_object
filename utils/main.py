import json
from configobj import Config
import os

print(f"initial current directory: {os.path.dirname(os.path.realpath(__file__))}")

config = Config("config.json", env_file=".env")
print(json.dumps(config.items(), indent=2))
