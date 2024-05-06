import json
from configobj.config import Config

config = Config("config.json", env_file=".env")
print(json.dumps(config.items(), indent=2))
