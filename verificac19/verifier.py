from dcc_utils import from_image, from_raw
from dcc_utils.exceptions import DCCParsingError

SUPER_GP_MODE = "2G"

NOT_EU_DCC = 'NOT_EU_DCC'
NOT_VALID = 'NOT_VALID'
NOT_VALID_YET = 'NOT_VALID_YET'
VALID = 'VALID'

class Verifier():

    @classmethod
    def _check_vaccination(cls, payload): 
        print('Vaccino')
        print(payload)
        if payload['v'][-1]["mp"] == "Sputnik-V" and payload['v'][-1]["co"] != "SM":
            return {
                "code": NOT_VALID,
                "result": False,
                "message" : 'Vaccine Sputnik-V is valid only in San Marino',
            }

    @classmethod
    def _check_test(cls, payload): 
        print('Test')
        print(payload)

    @classmethod
    def _check_recovery(cls, payload): 
        print('Ricovero')
        print(payload)

    @classmethod
    def _verify(cls, dcc, super_gp_mode):
        payload = dcc.payload
        if 'v' in payload:
            result = cls._check_vaccination(payload)
        elif 't' in payload:
            if super_gp_mode == SUPER_GP_MODE:
                return {
                        "code": NOT_VALID,
                        "result": False,
                        "message" : 'Certificate is not valid',
                    }
            result = cls._check_test(payload)
        elif 'r' in payload:
            result = cls._check_recovery(payload)
        else: print('schianto')
        return result

    @classmethod
    def verify_image(cls, path, super_gp_mode=SUPER_GP_MODE):
        try:
            mydcc = from_image(path)
            response = cls._verify(mydcc, super_gp_mode)
            return response
        except DCCParsingError:
            return {
                    "code": NOT_VALID,
                    "result": False,
                    "message" : 'Certificate is not valid',
                }

    @classmethod
    def verify_raw(cls, raw,super_gp_mode=SUPER_GP_MODE):
        mydcc = from_raw(raw)
        return mydcc
