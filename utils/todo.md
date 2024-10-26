- [?] Check the .env and config.json (object) files privileges, if not 700 raise a warning.
- [ ] An object that has a `$ref` item, cannot have other items, except `type`, `required` and `pattern` which are used for validation
- [ ] Can be rewritten using JSONPaths?
- [ ] Validations must have levels: info, warning, error, critical.
- [ ] Make references to objects in the same file to reuse config blocks/objects
- [ ] Implement yaml config too
- [ ] Add good documentation (for python interpreter)
- [ ] Add readme.md file
- [ ] Add license ???

# Testing

    python -m unittest tests/test_config.py -v

- [x] missing .env file
- [?] not able to load json from the config.json file which can be accessed
- [x] Accept config in yaml format too