from dcc_utils import from_image
from verificac19 import service, verifier


file_test = {
    'vaccine' : 'tests/data/eu_test_certificates/SK_1.png',
    'not_valide_cert' : 'tests/data/not_valid_certificate.png',
    'invalid' : 'tests/data/invalid.png',
    'test' : 'tests/data/eu_test_certificates/TEST.png',
    'sm' : 'tests/data/eu_test_certificates/SM_1.png',
}
# print(verifier.verify_image(file_test['vaccine']))

service.update_all()
dcc_not_sm = from_image(file_test['vaccine'])

# verify first dose with vacine date 2021-11-01, NOT_VALID
dcc_not_sm._payload['v'][-1]['co'] = 'IT'
dcc_not_sm._payload['v'][-1]['dt'] = '2021-11-01'
print(verifier._check_vaccination(dcc_not_sm.payload))

# verify first dose with vacine date 2021-12-29, NOT_VALID_YET
dcc_not_sm._payload['v'][-1]['co'] = 'IT'
dcc_not_sm._payload['v'][-1]['dt'] = '2021-12-10'
print(verifier._check_vaccination(dcc_not_sm.payload))

# verify first dose with vacine date 2021-12-29, NOT_VALID_YET
dcc_not_sm._payload['v'][-1]['co'] = 'IT'
dcc_not_sm._payload['v'][-1]['dt'] = '2021-12-29'
print(verifier._check_vaccination(dcc_not_sm.payload))

# verify second dose with vacine date 2021-12-10, VALID
dcc_not_sm._payload['v'][-1]['co'] = 'IT'
dcc_not_sm._payload['v'][-1]['dt'] = '2021-12-10'
dcc_not_sm._payload['v'][-1]['dn'] = '2'
print(verifier._check_vaccination(dcc_not_sm.payload))

# verify second dose with vacine date 2022-12-10, NOT_VALID
dcc_not_sm._payload['v'][-1]['co'] = 'IT'
dcc_not_sm._payload['v'][-1]['dt'] = '2022-12-10'
dcc_not_sm._payload['v'][-1]['dn'] = '2'
print(verifier._check_vaccination(dcc_not_sm.payload))


dcc_not_sm = from_image('tests/data/eu_test_certificates/TEST.png')
dcc_not_sm._payload['t'][-1]['tr'] = '1111111' # NOT VALID
print(verifier._check_test(dcc_not_sm.payload))

dcc_not_sm = from_image('tests/data/eu_test_certificates/TEST.png')
dcc_not_sm._payload['t'][-1]['sc'] = '2021-12-15T03:03:12Z' # SHOULD BE VALID
print(verifier._check_test(dcc_not_sm.payload))

dcc_not_sm = from_image('tests/data/eu_test_certificates/TEST.png') # NOT VALID
print(verifier._check_test(dcc_not_sm.payload))

dcc_not_sm = from_image('tests/data/mouse.jpeg') # NOT VALID
print(verifier._check_vaccination(dcc_not_sm.payload))
print(verifier._check_certificate(dcc_not_sm))

