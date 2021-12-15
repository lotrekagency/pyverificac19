# VerificaC19 Python SDK

## Dev setup

Install dev dependencies

```
pip install -r requirements-dev.txt
```

Make sure `zbar` is installed in your system
  * For Mac OS X, it can be installed via `brew install zbar`
  * Debian systems via `apt install libzbar0`. [Source](https://pypi.org/project/pyzbar/)
  * Fedora / Red Hat `dnf install zbar`

### Run tests

```
make test
``` 

### Example excecution

```sh
python -m examples.try_sum
```

## License
This library is available under the [MIT](https://opensource.org/licenses/mit-license.php) license.
