- [ ] check the .env and config.json (object) files privileges, if not 700 raise a warning.
- [ ] an object that has a `$ref` item, cannot have other items, except `type`, `required` and `pattern` which are used for validation
- [ ] can be rewritten using JSONPaths?
- [ ] Validations must have levels: info, warning, error, critical.
- [ ] Make references to objects in the same file to reuse config blocks/objects

# Testing

    python -m unittest tests/test_config.py -v

- [ ] missing .env file
- [ ] not able to load json from the config.json file which can be accessed
- [ ] load yaml and detect if yaml or json by extension of the file