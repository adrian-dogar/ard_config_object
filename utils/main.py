from configobj.config import Config

config = Config("config.json", env_file=".env")
print(config.items())
