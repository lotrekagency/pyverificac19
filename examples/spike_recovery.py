from verificac19 import service, verifier
from dcc_utils import from_image


service.update_all()


dcc_recovery = from_image('tests/data/eu_test_certificates/SK_6.png')
# dcc_not_sm._payload['v'][-1]['co'] = 'IT'
# dcc_not_sm._payload['v'][-1]['dt'] = '2022-12-10'
# dcc_not_sm._payload['v'][-1]['dn'] = '2'
print(verifier._check_recovery(dcc_recovery.payload))