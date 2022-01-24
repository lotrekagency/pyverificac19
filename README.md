# VerificaC19 Python SDK

🐍 VerificaC19 SDK implementation for Python.

[![Latest Version](https://img.shields.io/pypi/v/verificac19.svg)](https://pypi.python.org/pypi/verificac19/)
[![CI](https://github.com/lotrekagency/pyverificac19/actions/workflows/ci.yml/badge.svg)](https://github.com/lotrekagency/pyverificac19)
[![codecov](https://codecov.io/gh/lotrekagency/pyverificac19/branch/main/graph/badge.svg?token=UGMC9QK5F5)](https://codecov.io/gh/lotrekagency/pyverificac19)
[![Supported Python versions](https://img.shields.io/badge/python-3.7%2C%203.8%2C%203.9%2C%203.10-blue.svg)](https://pypi.python.org/pypi/verificac19/)
[![Downloads](https://img.shields.io/pypi/dm/verificac19.svg)](https://pypi.python.org/pypi/verificac19/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Requirements

- Python version >= 3.7
- MongoDB version >= 5.x (used to store CRL)

Make sure `zbar` is installed in your system. [Source](https://pypi.org/project/pyzbar/).
  * For Mac OS X, it can be installed via `brew install zbar`
  * Debian systems via `apt install libzbar0`
  * Fedora / Red Hat `dnf install zbar`

## Install

```sh
pip install verificac19
```

## Usage

### Download and cache rules, CRL data and DSCs

You can download and cache rules, CRL Data and DSCs using `service`.

```python
from verificac19 import service

service.update_all()
```

`update_all` may rise `VerificaC19Error`

```py
from verificac19.exceptions import VerificaC19Error
```

⚠️ By default rules and DSCs will be cached in local folder, 
to change it please set `VC19_CACHE_FOLDER` env variable.

⚠️ CRL data will be stored in a MongoDB database. By default the
connection string is `mongodb://root:example@localhost:27017/VC19?authSource=admin`,
if you want to change it, set `VC19_MONGODB_URL` env variable.

### Verify a DCC

You can verify a DCC using `verifier`. You can verify a DCC using 
`verify_image` for images and `verify_raw` for raw data.

```python
from verificac19 import verifier

result = verifier.verify_image("my_dcc.png")
result = verifier.verify_raw("HC1:GH.....1GH")
```

`verify_image` and `verify_raw` return a dictionary containing `person` name, 
`date_of_birth`, `code` and a `message` alongside the `result`

```python
{
  'code': verifier.Codes.NOT_VALID, 
  'result': False, 
  'message': 'Certificate is not valid', 
  'person': 'Sčasný Svätozár', 
  'date_of_birth': '1984-09-27'
}
```

you can compare the resulting `code` with `verifier.Codes` values

| | Code            | Description                              | Result |
|-| --------------- | ---------------------------------------- | ------ |
|✅| VALID           | Certificate is valid                     | `True` |
|⚠️| TEST_NEEDED     | Test needed if verification mode is BOOSTER_DGP | `False` |
|❌| NOT_VALID       | Certificate is not valid                 | `False` |
|❌| NOT_VALID_YET   | Certificate is not valid yet             | `False` |
|❌| REVOKED   | Certificate is revoked           | `False` |
|❌| NOT_EU_DCC      | Certificate is not an EU DCC             | `False` |

for example 

```python
result = verifier.verify_image("my_dcc.png")
assert result['code'] == verifier.Codes.NOT_VALID
```

⚠️ `verify_image` and `verify_raw` may rise `VerificaC19Error` in case you cache 
is not initialized. You need to call `service.update_all()` at least once!

### Verification mode

If you want to change verification mode and verify whether a certificate is a 
Super Green Pass or not, you need to pass `verifier.Mode.SUPER_DGP` to 
`verify_image` and `verify_raw` methods.

```python
from verificac19 import verifier

result = verifier.verify_image("my_dcc.png", verifier.Mode.SUPER_DGP)
```

`verifier.Mode` exposes 2 possible values

| Code           | Description                              |
| -------------- | ---------------------------------------- |
| NORMAL_DGP     | Normal verification (default value)      |
| SUPER_DGP      | Super Green Pass verification            | 
| BOOSTER_DGP    | Booster verification mode                | 

Details

- `SUPER_DGP Mode`: VerificaC19 SDK considers a green certificate valid only for
people who have been vaccinated against or who have recovered from Covid19, 
and will prevent all the others from 
entering bars, restaurants, cinemas, gyms, theatres, discos and stadiums.

- `BOOSTER_DGP Mode`: VerificaC19 SDK considers green certificates generated after a 
booster dose to be valid. Furthermore, green certificates generated after the 
first vaccination cycle or recovery with the simultaneous presentation of a 
digital document certifying the negative result of a SARS-CoV-2 test 
are considered valid.

## Development

Install dev dependencies

```
pip install -r requirements-dev.txt
```

Make sure `zbar` is installed in your system. [Source](https://pypi.org/project/pyzbar/).
  * For Mac OS X, it can be installed via `brew install zbar`
  * Debian systems via `apt install libzbar0`
  * Fedora / Red Hat `dnf install zbar`

CRL data will be stored in a MongoDB database. This repository provides a simple 
`docker-compose.yml` file (dev instance) with a replica set. By default the
connection string is `mongodb://root:example@localhost:27017/VC19?authSource=admin`,
if you want to change it, set `VC19_MONGODB_URL` env variable.

### Run tests

```
make test
``` 

### Run examples

```sh
python -m examples.<example_name>
```

## Authors
Copyright (c) 2022 - [Lotrèk Digital Agency](https://lotrek.it/)

## Contributors
Thank you to everyone involved for improving this project, day by day.

<a href="https://github.com/lotrekagency/pyverificac19">
  <img
  src="https://contributors-img.web.app/image?repo=lotrekagency/pyverificac19"
  />
</a>

## License
This library is available under the [MIT](https://opensource.org/licenses/mit-license.php) license.
