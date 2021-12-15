from verificac19.verifier import Verifier
from dcc_utils import from_image
verifier = Verifier()


file_test = {
    'vaccine' : 'tests/data/eu_test_certificates/SK_1.png',
    'not_valide_cert' : 'tests/data/not_valid_certificate.png',
    'invalid' : 'tests/data/invalid.png',
    'test' : 'tests/data/eu_test_certificates/TEST.png',
    'sm' : 'tests/data/eu_test_certificates/SM_1.png',
}
# print(verifier.verify_image(file_test['vaccine']))


dcc_not_sm = from_image(file_test['vaccine'])
dcc_not_sm._payload['v'][-1]['co'] = 'IT'
dcc_not_sm._payload['v'][-1]['dt'] = '2022-12-10'
dcc_not_sm._payload['v'][-1]['dn'] = '2'
dcc_not_sm._payload['v'][-1]['ci'] = '01ITEAF1191644A045ED880309475C08867F#2'
print(verifier._check_vaccination(dcc_not_sm.payload))