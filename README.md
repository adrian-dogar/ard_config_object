ConfigObj
=========

ConfigObj is a small library that can be used to load json, yanl and .env config files to your project. 
The benefit that brings is the ability to maintain the structured config data files (json and yaml) free from sensitive info, which can be kept it the .env only. This libreary will load the data files and do the proper replacements in the json and yaml files with the sensitive values from the .env file.

For it, you can write the data config with a few types of placeholders (`${VAR_NAME}`) or references (`$ref`). 

Usage
-----

```python
from configobj import ConfigObj

config = ConfigObj()
config.load('config.json', '.env')
```

```python
from configobj.config import Config

config = Config("config.json", env_file=".env")

```