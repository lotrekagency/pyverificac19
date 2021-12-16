# VerificaC19 Python SDK

Official VerificaC19 SDK implementation for Node.js ([official SDKs list](https://github.com/ministero-salute/it-dgc-verificac19-sdk-onboarding#lista-librerie)).

### Example excecution

```sh
python -m examples.try_sum
```
## Usage

### Download and cache rules and DSCs

You can download and cache rules and DSCs using `Service` module.

```python

```

⚠️ By default rules and DSCs will be cached in a folder called `.cache`, 
to change it please set `VC19_CACHE_FOLDER` env variable.

👉🏻  See an example [examples/syncdata.js](https://github.com/italia/verificac19-sdk/blob/master/examples/syncdata.js).

### Verify a DCC

You can load a DCC from an image or from a raw string using `Certificate` module.

```python
```

Loaded DCC has the following structure:

```python

```

You can verify a DCC using `Validator` module.

```python

```

`Validator.validate` returns an object containing `person` name, 
`date_of_birth`, `code` and a `message` alongside the `result`

```python

```

you can compare the resulting `code` with `Validator.codes` values

| | Code            | Description                              |
|-| --------------- | ---------------------------------------- |
|✅| VALID           | Certificate is valid                     |
|❌| NOT_VALID       | Certificate is not valid                 | 
|❌| NOT_VALID_YET   | Certificate is not valid yet             | 
|❌| NOT_EU_DCC      | Certificate is not an EU DCC             | 

for example 

```python

```

👉🏻  See an example [examples/verifydccs.js](https://github.com/italia/verificac19-sdk/blob/master/examples/verifydccs.js).


### Verification mode

If you want to change verification mode and verify whether a certificate is a 
Super Green Pass or not, you need to pass `Validator.mode.SUPER_DGP` to 
`Validator.validate` method.

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

### Alternative methods

To update rules and DSCs you can also use `updateRules`, 
`updateSignaturesList` and `updateSignatures` methods

```python
```

To verify a DCC you can also use `Validator.checkRules` and 
`Validator.checkSignature` methods.

```python

```
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
VerificaC19-SDK for Node.js is available under the [MIT](https://opensource.org/licenses/mit-license.php) license.
