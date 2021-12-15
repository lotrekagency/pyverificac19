from dcc_utils import from_image, from_raw
from dcc_utils.exceptions import DCCParsingError
from .service import service
from datetime import datetime, timedelta

SUPER_GP_MODE = "2G"

GENERIC_TYPE = "GENERIC"

NOT_EU_DCC = 'NOT_EU_DCC'
NOT_VALID = 'NOT_VALID'
NOT_VALID_YET = 'NOT_VALID_YET'
VALID = 'VALID'

TEST_RAPID = 'LP217198-3'
TEST_MOLECULAR = 'LP6464-4'

TEST_DETECTED = '260373001'

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
        test = payload['t'][-1]
        if test['tr'] == TEST_DETECTED:
            return {
                "code": NOT_VALID,
                "result": False,
                "message" : 'Test Result is DETECTED',
            }

        test_type = 'molecular' if test['tt'] == TEST_MOLECULAR else 'rapid'

        test_datetime = datetime.strptime(test['sc'], "%Y-%m-%dT%H:%M:%S%z")
        now = datetime.now(test_datetime.tzinfo)

        start_hours = int(service.get_setting(f'{test_type}_test_start_hours', GENERIC_TYPE)['value'])
        end_hours = int(service.get_setting(f'{test_type}_test_end_hours', GENERIC_TYPE)['value'])
        start_datetime = test_datetime + timedelta(hours=start_hours)
        end_datetime = test_datetime + timedelta(hours=end_hours)

        if now < start_datetime:
            return {
                "code": NOT_VALID_YET,
                "result": False,
                "message" : f'Test Result is not valid yet, starts at : {start_datetime.strftime("%Y-%m-%d %H:%M:%S%z")}',
            }

        if end_datetime < now:
            return {
                "code": NOT_VALID,
                "result": False,
                "message" : f'Test Result is not valid, ended at : {end_datetime.strftime("%Y-%m-%d %H:%M:%S%z")}',
            }

        return {
            "code": VALID,
            "result": True,
            "message": f'Test Result is valid [{start_datetime.strftime("%Y-%m-%d %H:%M:%S")} - {end_datetime.strftime("%Y-%m-%d %H:%M:%S")}]',
        }

    @classmethod
    def _check_recovery(cls, payload): 
        service.update_settings()
        print('Ricovero')
        print(payload)
        last = payload['r'][-1]
        recovery_start_day = int(service.get_setting('recovery_cert_start_day', "GENERIC")['value'])
        recovery_end_day = int(service.get_setting('recovery_cert_end_day', "GENERIC")['value'])

        start_date = datetime.strptime(last['df'], "%Y-%m-%d")
        end_date = datetime.strptime(last['du'], "%Y-%m-%d")
        start_date_validation =  start_date + timedelta(days=recovery_start_day)
        now = datetime.now()

        if start_date_validation > now:
            return {
                "code": NOT_VALID_YET,
                "result": False,
                "message": 'Recovery statement is not valid yet',
            }
        if now > start_date_validation + timedelta(days=recovery_end_day): 
            return {
                'code': NOT_VALID,
                "result": False,
                'message': 'Recovery statement is expired',
            }
        return {
            'code': VALID,
            "result": True,
            'message': 'Recovery statement is expired',
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
