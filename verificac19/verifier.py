from enum import Enum
from typing import Callable
from datetime import datetime, timedelta

from dcc_utils import from_image, from_raw
from dcc_utils.dcc import DCC
from dcc_utils.exceptions import DCCParsingError

from .service import _service as service


GENERIC_TYPE = "GENERIC"

TEST_RAPID = "LP217198-3"
TEST_MOLECULAR = "LP6464-4"

TEST_DETECTED = "260373001"


class Result:
    def __init__(
        self,
        code: str,
        result: bool,
        message: str,
        name: str = "-",
        date_of_birth: str = "-",
    ):
        self._code = code
        self._result = result
        self._message = message
        self._name = name
        self._date_of_birth = date_of_birth

    def add_person(self, name: str, date_of_birth: str):
        self._name = name
        self._date_of_birth = date_of_birth
        return self

    @property
    def payload(self) -> dict:
        return {
            "code": self._code,
            "result": self._result,
            "message": self._message,
            "person": self._name,
            "date_of_birth": self._date_of_birth,
        }


class Verifier:
    class Codes(Enum):
        NOT_EU_DCC = "NOT_EU_DCC"
        NOT_VALID = "NOT_VALID"
        NOT_VALID_YET = "NOT_VALID_YET"
        VALID = "VALID"

    class Mode(Enum):
        SUPER_GP_MODE = "2G"
        NORMAL_DGP = "3G"

    def _check_vaccination(self, payload: dict):
        if len(payload["v"]) == 0:
            return Result(
                self.Codes.NOT_EU_DCC,
                False,
                "No vaccination, test or recovery statement found in payload",
            )
        last = payload["v"][-1]
        if service.is_blacklisted(last["ci"]):
            return Result(
                self.Codes.NOT_VALID,
                False,
                "UVCI is in blacklist",
            )

        if last["mp"] == "Sputnik-V" and last["co"] != "SM":
            return Result(
                self.Codes.NOT_VALID,
                False,
                "Vaccine Sputnik-V is valid only in San Marino",
            )

        not_valid_doses = Result(
            self.Codes.NOT_VALID,
            False,
            "Current or necessary doses are not valid",
        )

        try:
            current_dose = int(last["dn"])
            necessary_dose = int(last["sd"])
        except ValueError:
            return not_valid_doses

        if current_dose < 0 or necessary_dose < 0:
            return not_valid_doses

        doses_str = f"Doses {current_dose}/{necessary_dose}"

        vaccine_date = datetime.strptime(last["dt"], "%Y-%m-%d")
        now = datetime.now()

        if current_dose < necessary_dose:
            vaccine_start_day_not_complete = int(
                service.get_setting("vaccine_start_day_not_complete", last["mp"])[
                    "value"
                ]
            )
            vaccine_end_day_not_complete = int(
                service.get_setting("vaccine_end_day_not_complete", last["mp"])["value"]
            )
            check_start_day_not_complete = vaccine_date + timedelta(
                days=vaccine_start_day_not_complete
            )
            check_end_day_not_complete = vaccine_date + timedelta(
                days=vaccine_end_day_not_complete
            )
            if now < check_start_day_not_complete:
                return Result(
                    self.Codes.NOT_VALID_YET,
                    False,
                    f"{doses_str} - Vaccination is not valid yet, starts at : {check_start_day_not_complete.strftime('%Y-%m-%d')}",
                )
            if now > check_end_day_not_complete:
                return Result(
                    self.Codes.NOT_VALID,
                    False,
                    f"{doses_str} - Vaccination is expired at : {check_end_day_not_complete.strftime('%Y-%m-%d')}",
                )
            return Result(
                self.Codes.VALID,
                True,
                f"{doses_str} - Vaccination is valid - [{check_start_day_not_complete.strftime('%Y-%m-%d')} - {check_end_day_not_complete.strftime('%Y-%m-%d')}]",
            )
        else:
            vaccine_start_day_complete = int(
                service.get_setting("vaccine_start_day_complete", last["mp"])["value"]
            )
            vaccine_end_day_complete = int(
                service.get_setting("vaccine_end_day_complete", last["mp"])["value"]
            )
            check_start_day_complete = vaccine_date + timedelta(
                days=vaccine_start_day_complete
            )
            check_end_day_complete = vaccine_date + timedelta(
                days=vaccine_end_day_complete
            )
            if now < check_start_day_complete:
                return Result(
                    self.Codes.NOT_VALID_YET,
                    False,
                    f"{doses_str} - Vaccination is not valid yet, starts at: {check_start_day_complete.strftime('%Y-%m-%d')}",
                )
            if now > check_end_day_complete:
                return Result(
                    self.Codes.NOT_VALID,
                    False,
                    f"{doses_str} - Vaccination is expired at : {check_end_day_complete.strftime('%Y-%m-%d')}",
                )
            return Result(
                self.Codes.VALID,
                True,
                f"{doses_str} - Vaccination is valid - [{check_start_day_complete.strftime('%Y-%m-%d')} - {check_end_day_complete.strftime('%Y-%m-%d')}]",
            )

    def _check_test(self, payload: dict):
        if len(payload["t"]) == 0:
            return Result(
                self.Codes.NOT_EU_DCC,
                False,
                "No vaccination, test or recovery statement found in payload",
            )
        test = payload["t"][-1]
        if test["tr"] == TEST_DETECTED:
            return Result(
                self.Codes.NOT_VALID,
                False,
                "Test Result is DETECTED",
            )

        test_type = "molecular" if test["tt"] == TEST_MOLECULAR else "rapid"

        test_datetime = datetime.strptime(test["sc"], "%Y-%m-%dT%H:%M:%S%z")
        now = datetime.now(test_datetime.tzinfo)

        start_hours = int(
            service.get_setting(f"{test_type}_test_start_hours", GENERIC_TYPE)["value"]
        )
        end_hours = int(
            service.get_setting(f"{test_type}_test_end_hours", GENERIC_TYPE)["value"]
        )
        start_datetime = test_datetime + timedelta(hours=start_hours)
        end_datetime = test_datetime + timedelta(hours=end_hours)

        if now < start_datetime:
            return Result(
                self.Codes.NOT_VALID_YET,
                False,
                f'Test Result is not valid yet, starts at : {start_datetime.strftime("%Y-%m-%d %H:%M:%S%z")}',
            )

        if end_datetime < now:
            return Result(
                self.Codes.NOT_VALID,
                False,
                f'Test Result is expired at : {end_datetime.strftime("%Y-%m-%d %H:%M:%S%z")}',
            )

        return Result(
            self.Codes.VALID,
            True,
            f'Test Result is valid [{start_datetime.strftime("%Y-%m-%d %H:%M:%S")} - {end_datetime.strftime("%Y-%m-%d %H:%M:%S")}]',
        )

    def _check_recovery(self, payload: dict):
        if len(payload["r"]) == 0:
            return Result(
                self.Codes.NOT_EU_DCC,
                False,
                "No vaccination, test or recovery statement found in payload",
            )
        last = payload["r"][-1]
        recovery_start_day = int(
            service.get_setting("recovery_cert_start_day", "GENERIC")["value"]
        )
        recovery_end_day = int(
            service.get_setting("recovery_cert_end_day", "GENERIC")["value"]
        )

        start_date = datetime.strptime(last["df"], "%Y-%m-%d")
        start_date_validation = start_date + timedelta(days=recovery_start_day)
        now = datetime.now()

        if start_date_validation > now:
            return Result(
                self.Codes.NOT_VALID_YET,
                False,
                "Recovery statement is not valid yet",
            )
        if now > start_date_validation + timedelta(days=recovery_end_day):
            return Result(
                self.Codes.NOT_VALID,
                False,
                "Recovery statement is expired",
            )
        return Result(
            self.Codes.VALID,
            True,
            "Recovery statement is valid",
        )

    def _verify_dsc(self, dcc: DCC):
        signature = (
            "-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----"
        ).format(service.get_dsc(dcc.kid))
        try:
            return dcc.check_signature(signature.encode("utf-8"))
        except ValueError:
            return False

    def _verify_rules(self, dcc: DCC, super_gp_mode: Mode):
        payload = dcc.payload
        if "v" in payload:
            result = self._check_vaccination(payload)
        elif "t" in payload:
            if super_gp_mode == self.Mode.SUPER_GP_MODE:
                result = Result(
                    self.Codes.NOT_VALID,
                    False,
                    "Not valid. Super DGP required.",
                )
            else:
                result = self._check_test(payload)
        elif "r" in payload:
            result = self._check_recovery(payload)
        else:
            result = Result(
                self.Codes.NOT_EU_DCC,
                False,
                "No vaccination, test or recovery statement found in payload",
            )
        return result.add_person(
            f"{payload['nam']['fn']} {payload['nam']['gn']}", payload["dob"]
        ).payload

    def _verify(
        self,
        f: Callable[[str, DCCParsingError], DCC],
        path_or_raw: str,
        super_gp_mode: Mode = None,
    ):
        if super_gp_mode is None:
            super_gp_mode = self.Mode.NORMAL_DGP
        try:
            dcc = f(path_or_raw)
            if not self._verify_dsc(dcc):
                result = Result(
                    self.Codes.NOT_VALID,
                    False,
                    "Signature is not valid",
                )
                if "nam" in dcc.payload:
                    result = result.add_person(
                        f"{dcc.payload['nam']['fn']} {dcc.payload['nam']['gn']}",
                        dcc.payload["dob"],
                    )
                return result.payload
            response = self._verify_rules(dcc, super_gp_mode)
            return response
        except DCCParsingError:
            return Result(
                self.Codes.NOT_EU_DCC,
                False,
                "Certificate is not valid",
            ).payload

    def verify_image(self, path: str, super_gp_mode: Mode = None):
        return self._verify(from_image, path, super_gp_mode)

    def verify_raw(self, raw: str, super_gp_mode: Mode = None):
        return self._verify(from_raw, raw, super_gp_mode)


_verifier = Verifier()
