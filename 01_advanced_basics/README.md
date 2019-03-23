## OTUS Python 01 - Advanced Basics - Log parser

### Setup

* Create directory `log` in the root path and put there logs that needs to be parsed
* Create directory `reports` in the root path
* Put `jquery.tablesorter.min.js` file to `reports` folder (or other folder
  that will contain reports)

### Running

* base command:

```
python log_analyzer.py --config <config name>
```

where `config` - name of the external configuration. Supported formats: `json`, `yaml`

* running tests:

```
python -m unittest log_analyzer_test.py
```

Python version - 2.7.11
