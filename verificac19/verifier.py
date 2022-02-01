from enum import Enum
from typing import Callable
from datetime import datetime, timedelta
from OpenSSL import crypto

from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError

from .service import _service as service


GENERIC_TYPE = "GENERIC"

TEST_RAPID = "LP217198-3"
TEST_MOLECULAR = "LP6464-4"

TEST_DETECTED = "260373001"

JOHNSON_VACCINE_ID = "EU/1/20/1525"

OID_BIS_RECOVERY = ["1.3.6.1.4.1.1847.2021.1.3", "1.3.6.1.4.1.0.1847.2021.1.3"]


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
        TEST_NEEDED = "TEST_NEEDED"
        VALID = "VALID"

    class Mode(Enum):
        SUPER_GP_MODE = "2G"
        NORMAL_DGP = "3G"
        BOOSTER_DGP = "BOOSTER"

    def _check_vaccination(self, dcc: dcc.DCC, mode: Mode):
        payload = dcc.payload
        if len(payload["v"]) == 0:
            return Result(
                self.Codes.NOT_EU_DCC,
                False,
                "No vaccination, test, recovery or exemption statement found in payload",
            )
        last = payload["v"][-1]
        vaccine_type = last["mp"]

        if vaccine_type == "Sputnik-V" and last["co"] != "SM":
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
            if mode == self.Mode.BOOSTER_DGP:
                return Result(
                    self.Codes.NOT_VALID,
                    False,
                    "Vaccine is not valid in Booster mode",
                )

            vaccine_start_day_not_complete = int(
                service.get_setting("vaccine_start_day_not_complete", vaccine_type)[
                    "value"
                ]
            )
            vaccine_end_day_not_complete = int(
                service.get_setting("vaccine_end_day_not_complete", vaccine_type)[
                    "value"
                ]
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
                service.get_setting("vaccine_start_day_complete", vaccine_type)["value"]
            )
            vaccine_end_day_complete = int(
                service.get_setting("vaccine_end_day_complete", vaccine_type)["value"]
            )
            check_start_day_complete = vaccine_date + timedelta(
                days=vaccine_start_day_complete
            )
            check_end_day_complete = vaccine_date + timedelta(
                days=vaccine_end_day_complete
            )

            if vaccine_type == JOHNSON_VACCINE_ID and (
                current_dose > necessary_dose
                or current_dose == necessary_dose
                and current_dose >= 2
            ):
                check_start_day_complete = vaccine_date

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

            if mode == self.Mode.BOOSTER_DGP:
                if vaccine_type == JOHNSON_VACCINE_ID:
                    if current_dose == necessary_dose and current_dose < 2:
                        return Result(
                            self.Codes.TEST_NEEDED,
                            False,
                            "Test needed",
                        )
                elif current_dose == necessary_dose and current_dose < 3:
                    return Result(
                        self.Codes.TEST_NEEDED,
                        False,
                        "Test needed",
                    )

            return Result(
                self.Codes.VALID,
                True,
                f"{doses_str} - Vaccination is valid - [{check_start_day_complete.strftime('%Y-%m-%d')} - {check_end_day_complete.strftime('%Y-%m-%d')}]",
            )

    def _check_test(self, dcc: dcc.DCC, mode: Mode):
        payload = dcc.payload
        if len(payload["t"]) == 0:
            return Result(
                self.Codes.NOT_EU_DCC,
                False,
                "No vaccination, test, recovery or exemption statement found in payload",
            )
        if mode != self.Mode.NORMAL_DGP:
            return Result(
                self.Codes.NOT_VALID,
                False,
                "Not valid. Super DGP or Booster required.",
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

    def _check_recovery(self, dcc: dcc.DCC, mode: Mode):
        payload = dcc.payload
        if len(payload["r"]) == 0:
            return Result(
                self.Codes.NOT_EU_DCC,
                False,
                "No vaccination, test, recovery or exemption statement found in payload",
            )
        if mode == self.Mode.BOOSTER_DGP:
            return Result(
                self.Codes.TEST_NEEDED,
                False,
                "Test needed",
            )

        last = payload["r"][-1]
        cert_info = (
            self._get_dsc_info(service.get_dsc(dcc.kid))
            if self._verify_dsc(dcc)
            else {}
        )
        recovery_type = (
            "recovery_pv"
            if cert_info.get("country") == "IT"
            and cert_info.get("oid") in OID_BIS_RECOVERY
            else "recovery"
        )
        recovery_start_day = int(
            service.get_setting(f"{recovery_type}_cert_start_day", "GENERIC")["value"]
        )
        recovery_end_day = int(
            service.get_setting(f"{recovery_type}_cert_end_day", "GENERIC")["value"]
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

    def _check_exemption(self, dcc: dcc.DCC, mode: Mode):
        payload = dcc.payload
        if len(payload["e"]) == 0:
            return Result(
                self.Codes.NOT_EU_DCC,
                False,
                "No vaccination, test, recovery, or exemption statement found in payload",
            )
        if mode == self.Mode.BOOSTER_DGP:
            return Result(
                self.Codes.TEST_NEEDED,
                False,
                "Test needed",
            )

        last = payload["e"][-1]

        start_date = datetime.strptime(last["df"], "%Y-%m-%d")
        end_date = datetime.strptime(last["du"], "%Y-%m-%d")
        now = datetime.now()

        if start_date > now:
            return Result(
                self.Codes.NOT_VALID_YET,
                False,
                f"Exemption is not valid yet, starts at: {start_date.strftime('%Y-%m-%d')}",
            )
        if now > end_date:
            return Result(
                self.Codes.NOT_VALID,
                False,
                f"Exemption is expired at: {end_date.strftime('%Y-%m-%d')}",
            )

        return Result(
            self.Codes.VALID,
            True,
            f"Exemption is valid [{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}]",
        )

    def _format_dsc(self, dsc: str) -> str:
        return ("-----BEGIN CERTIFICATE-----\n{}\n-----END CERTIFICATE-----").format(
            dsc
        )

    def _get_dsc_info(self, dsc: str):
        info = {"country": None, "oid": None}
        cert = crypto.load_certificate(
            crypto.FILETYPE_PEM, self._format_dsc(dsc).encode("utf-8")
        )
        issuer = cert.get_issuer()
        info["country"] = issuer.C
        for i in range(cert.get_extension_count()):
            ext = cert.get_extension(i)
            if ext.get_short_name() == b"extendedKeyUsage":
                info["oid"] = str(ext)
                break
        return info

    def _verify_dsc(self, dcc_obj: dcc.DCC):
        dsc = service.get_dsc(dcc_obj.kid)
        try:
            return dcc_obj.check_signature(self._format_dsc(dsc).encode("utf-8"))
        except ValueError:
            return False

    def _verify_uvci(self, payload: dict, certificate_type: str):
        if certificate_type not in payload:
            return False
        if len(payload[certificate_type]) == 0:
            return False
        certificate = payload[certificate_type][-1]
        return not service.is_blacklisted(certificate["ci"])

    def _verify_rules(self, dcc_obj: dcc.DCC, mode: Mode):
        payload = dcc_obj.payload
        if "v" in payload:
            result = self._check_vaccination(dcc_obj, mode)
        elif "t" in payload:
            result = self._check_test(dcc_obj, mode)
        elif "r" in payload:
            result = self._check_recovery(dcc_obj, mode)
        elif "e" in payload:
            result = self._check_exemption(dcc_obj, mode)
        else:
            result = Result(
                self.Codes.NOT_EU_DCC,
                False,
                "No vaccination, test or recovery statement found in payload",
            )
        if result._result and not any(
            self._verify_uvci(payload, t) for t in ["v", "t", "r", "e"]
        ):
            result = Result(
                self.Codes.NOT_VALID,
                False,
                "UVCI in blacklist",
            )
        return result.add_person(
            f"{payload['nam']['fn']} {payload['nam']['gn']}", payload["dob"]
        ).payload

    def _verify(
        self,
        f: Callable[[str, DCCParsingError], dcc.DCC],
        path_or_raw: str,
        mode: Mode = None,
    ):
        if mode is None:
            mode = self.Mode.NORMAL_DGP
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
            response = self._verify_rules(dcc, mode)
            return response
        except DCCParsingError:
            return Result(
                self.Codes.NOT_EU_DCC,
                False,
                "Certificate is not valid",
            ).payload

    def verify_image(self, path: str, mode: Mode = None):
        return self._verify(dcc.from_image, path, mode)

    def verify_raw(self, raw: str, mode: Mode = None):
        return self._verify(dcc.from_raw, raw, mode)


_verifier = Verifier()
