# VerificaC19 Python SDK

## Install

```sh
pip install verificac19
```

Make sure `zbar` is installed in your system
  * For Mac OS X, it can be installed via `brew install zbar`
  * Debian systems via `apt install libzbar0`. [Source](https://pypi.org/project/pyzbar/)
  * Fedora / Red Hat `dnf install zbar`

## Usage

### Download and cache rules and DSCs

You can download and cache rules and DSCs using `service`.

```python
from verificac19 import service

service.update_all()
```

⚠️ By default rules and DSCs will be cached in local folder, 
to change it please set `VC19_CACHE_FOLDER` env variable.

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
  'code': 'NOT_VALID', 
  'result': False, 
  'message': 'Certificate is not valid', 
  'person': 'Sčasný Svätozár', 
  'date_of_birth': '1984-09-27'
}
```

you can compare the resulting `code` with `verifier.Codes` values

| | Code            | Description                              |
|-| --------------- | ---------------------------------------- |
|✅| VALID           | Certificate is valid                     |
|❌| NOT_VALID       | Certificate is not valid                 | 
|❌| NOT_VALID_YET   | Certificate is not valid yet             | 
|❌| NOT_EU_DCC      | Certificate is not an EU DCC             | 

for example 

```python
result = verifier.verify_image("my_dcc.png")
assert result['code'] == verifier.Codes.NOT_VALID
```

### Verification mode

If you want to change verification mode and verify whether a certificate is a 
Super Green Pass or not, you need to pass `verifier.Mode.SUPER_DGP` to 
`verify_image` and `verify_raw` methods.

```python

```

| Code           | Description                              |
| -------------- | ---------------------------------------- |
| NORMAL_DGP     | Normal verification (default value)      |
| SUPER_DGP      | Super Green Pass verification            | 

***Super Green Pass, which will come into force from 6 December to 15 January 2021, 
will be a certificate valid only for people who have been vaccinated against 
or who have recovered from Covid19, and will prevent all the others from 
entering bars, restaurants, cinemas, gyms, theatres, discos and stadiums.***

## Development

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

### Run examples

```sh
python -m examples.<example_name>
```

## Authors
Copyright (c) 2021 - [Lotrèk Digital Agency](https://lotrek.it/)

## Contributors
Here is a list of contributors. Thank you to everyone involved for improving this project, day by day.

<a href="https://github.com/lotrekagency/pyverificac19">
  <img
  src="https://contributors-img.web.app/image?repo=lotrekagency/pyverificac19"
  />
</a>

## License
This library is available under the [MIT](https://opensource.org/licenses/mit-license.php) license.
