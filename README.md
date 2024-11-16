ConfigObj
=========

ConfigObj is a small library that can be used to load json, yanl and .env config files to your project. 
The benefit that brings is the ability to maintain the structured config data files (json and yaml) free from sensitive info, which can be kept it the .env only. This libreary will load the data files and do the proper replacements in the json and yaml files with the sensitive values from the .env file.

For it, you can write the data config with a few types of placeholders (`${VAR_NAME}`) or references (`$ref`). 

Usage
-----

Write your config files in json or yaml format, using placeholders where sensitive information should be or the data must come from a different source of truth.

### Placeholders
You can use two different types of placeholders
- inline reference: `"${@env.placeholder}"`
- object reference: `{"$ref": "@env.placeholder"}`

The first one is easier and shorter, the latest one gives you the advantage to enforce if the field is required, and you want to raise an exception for the missing value. 
Eg. `{"$ref": "@env.placeholder", "required": false}`

### References
Both placeholders can be used to reference values coming from three different sources types:
- from the env vars (using `.env` file): `@env.placeholder`
- from a value inside the same file: `#/definitions/short_value`
- from a different structured data file (supports yaml and json only): `./some-other-file.json#/spec/some_property`

### Config file example

```json
{
  "some_info": "This is a test file for the test branch",
  "element": "In-line ${@env.placeholder} test",
  "definitions": {
    "short_value": "short"
  },
  "some_secret_info": {
    "$ref": "@env.some_secret"
  },
  "some_other_secret_info": {
    "$ref": "@env.some_other_secret",
    "required": false
  },
  "parent": {
    "child": {
      "$ref": "@env.child"
    },
    "short_value": {"$ref": "#/definitions/short_value"},
    "placeholder": "${@env.placeholder}",
    "hardcoded": "test",
    "referenced_property": {"$ref": "./imported.json#/spec/some_property"},
    "env_ref": {"$ref": "@env.child"}

  },
  "list": [
    {"$ref": "#/definitions/short_value"},
    "${@env.placeholder}",
    "test",
    {"$ref": "./imported.json#/spec/some_property"},
    {"$ref": "@env.child"}
  ]
}
```

### .env file example

```env
child=Sem
some_secret="This is a secret"
placeholder="Secret data"
```

### Load your Config objects

```python
from configobj import ConfigObj

config = ConfigObj()
config.load('config.json', '.env')
```

```python
from configobj.config import Config

config = Config("config.json", env_file=".env")

```