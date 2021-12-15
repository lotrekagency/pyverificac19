from dcc_utils import from_image, from_raw
from dcc_utils.exceptions import DCCParsingError
from .service import service
from datetime import datetime, timedelta

SUPER_GP_MODE = "2G"

NOT_EU_DCC = 'NOT_EU_DCC'
NOT_VALID = 'NOT_VALID'
NOT_VALID_YET = 'NOT_VALID_YET'
VALID = 'VALID'

class Verifier():

    @classmethod
    def _check_vaccination(cls, payload): 
        service.update_settings()
        print('Vaccino')
        print(payload)
        last = payload['v'][-1]
        if service.is_blacklisted(last['ci']):
            return {
                "code": NOT_VALID,
                "result": False,
                "message" : 'No vaccination, test or recovery statement found in payload or UVCI is in blacklist',
            }

        if last["mp"] == "Sputnik-V" and last["co"] != "SM":
            return {
                "code": NOT_VALID,
                "result": False,
                "message" : 'Vaccine Sputnik-V is valid only in San Marino',
            }

        current_dose = int(last['dn'])
        necessary_dose = int(last['sd'])

        vaccine_date = datetime.strptime(last['dt'], "%Y-%m-%d")
        now = datetime.now()

        if current_dose < necessary_dose:
            vaccine_start_day_not_complete = int(service.get_setting('vaccine_start_day_not_complete', last['mp'])['value'])
            vaccine_end_day_not_complete = int(service.get_setting('vaccine_end_day_not_complete', last['mp'])['value'])
            check_start_day_not_complete = vaccine_date + timedelta(days=vaccine_start_day_not_complete)
            check_end_day_not_complete = vaccine_date + timedelta(days=vaccine_end_day_not_complete)
            if now < check_start_day_not_complete:
                return {
                    "code": NOT_VALID_YET,
                    "result": False,
                    "message" : 'Certificate is not valid yet',
                }
            if now > check_end_day_not_complete:
                return {
                    "code": NOT_VALID,
                    "result": False,
                    "message" : 'Certificate is not valid',
                }
        else:
            vaccine_start_day_complete = int(service.get_setting('vaccine_start_day_complete', last['mp'])['value'])
            vaccine_end_day_complete = int(service.get_setting('vaccine_end_day_complete', last['mp'])['value'])
            check_start_day_complete = vaccine_date + timedelta(days=vaccine_start_day_complete)
            check_end_day_complete = vaccine_date + timedelta(days=vaccine_end_day_complete)
            if now < check_start_day_complete:
                return {
                    "code": NOT_VALID_YET,
                    "result": False,
                    "message" : 'Certificate is not valid yet',
                }
            if now > check_end_day_complete:
                return {
                    "code": NOT_VALID,
                    "result": False,
                    "message" : 'Certificate is not valid',
                }
        return {
            "code": VALID,
            "result": True,
            "message" : 'Certificate is valid',
        }

    @classmethod
    def _check_test(cls, payload): 
        service.update_settings()
        print('Test')
        print(payload)
        last = payload['v'][-1]
        if service.is_blacklisted(last['ci']):
            return {
                "code": NOT_VALID,
                "result": False,
                "message" : 'No vaccination, test or recovery statement found in payload or UVCI is in blacklist',
            }

    @classmethod
    def _check_recovery(cls, payload): 
        service.update_settings()
        print('Ricovero')
        print(payload)
        last = payload['v'][-1]
        if service.is_blacklisted(last['ci']):
            return {
                "code": NOT_VALID,
                "result": False,
                "message" : 'No vaccination, test or recovery statement found in payload or UVCI is in blacklist',
            }

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
