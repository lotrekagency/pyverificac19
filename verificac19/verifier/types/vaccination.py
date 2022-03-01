from .base_verifier import Verifier
from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError
from verificac19.verifier.result import Result
from verificac19.service import service
from datetime import datetime, timedelta

class VaccinationVerifier(Verifier):

    def check_dcc(self, dcc: dcc.DCC, mode: Verifier.Mode):
        payload = dcc.payload
        if len(payload["v"]) == 0:
            return Result(
                super().Codes.NOT_EU_DCC.value,
                False,
                "No vaccination, test, recovery or exemption statement found in payload",
            )
        last = payload["v"][-1]
        vaccine_type = last["mp"]

        if vaccine_type == "Sputnik-V" and last["co"] != "SM":
            return Result(
                super().Codes.NOT_VALID.value,
                False,
                "Vaccine Sputnik-V is valid only in San Marino",
            )

        not_valid_doses = Result(
            super().Codes.NOT_VALID.value,
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
            if mode == super().Mode.BOOSTER_DGP:
                return Result(
                    super().Codes.NOT_VALID.value,
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
                    super().Codes.NOT_VALID_YET.value,
                    False,
                    f"{doses_str} - Vaccination is not valid yet, starts at : {check_start_day_not_complete.strftime('%Y-%m-%d')}",
                )
            if now > check_end_day_not_complete:
                return Result(
                    super().Codes.NOT_VALID.value,
                    False,
                    f"{doses_str} - Vaccination is expired at : {check_end_day_not_complete.strftime('%Y-%m-%d')}",
                )
            return Result(
                super().Codes.VALID.value,
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
                    super().Codes.NOT_VALID_YET.value,
                    False,
                    f"{doses_str} - Vaccination is not valid yet, starts at: {check_start_day_complete.strftime('%Y-%m-%d')}",
                )
            if now > check_end_day_complete:
                return Result(
                    super().Codes.NOT_VALID.value,
                    False,
                    f"{doses_str} - Vaccination is expired at : {check_end_day_complete.strftime('%Y-%m-%d')}",
                )

            if mode == super().Mode.BOOSTER_DGP:
                if vaccine_type == super.JOHNSON_VACCINE_ID:
                    if current_dose == necessary_dose and current_dose < 2:
                        return Result(
                            super().Codes.TEST_NEEDED.value,
                            False,
                            "Test needed",
                        )
                elif current_dose == necessary_dose and current_dose < 3:
                    return Result(
                        super().Codes.TEST_NEEDED.value,
                        False,
                        "Test needed",
                    )

            return Result(
                super().Codes.VALID.value,
                True,
                f"{doses_str} - Vaccination is valid - [{check_start_day_complete.strftime('%Y-%m-%d')} - {check_end_day_complete.strftime('%Y-%m-%d')}]",
            )
