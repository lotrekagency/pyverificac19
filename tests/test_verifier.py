import os
import re
import time_machine
import datetime as dt

from verificac19 import verifier
from dcc_utils.dcc import from_image


def verify_rules_from_certificate(
    dcc,
    expected_result,
    expected_code,
    expected_msg_reg=None,
    mode=verifier.Mode.NORMAL_DGP,
):
    result = verifier._verify_rules(dcc, mode)
    assert result["result"] == expected_result
    assert result["code"] == expected_code
    if expected_msg_reg:
        assert not re.search(expected_msg_reg, result["message"]) is None


def verify_rules_from_image(
    img_path,
    expected_result,
    expected_code,
    expected_msg_reg=None,
    mode=verifier.Mode.NORMAL_DGP,
):
    dcc = from_image(img_path)
    return verify_rules_from_certificate(
        dcc, expected_result, expected_code, expected_msg_reg, mode
    )


def verify_signature(img_path, expected_result):
    dcc = from_image(img_path)
    result = verifier._verify_dsc(dcc)
    assert result == expected_result


def test_get_dsc_info():
    with open(os.path.join("tests", "data", "raw_dsc")) as dsc:
        info = verifier._get_dsc_info(dsc.read())
        assert info["country"] == "IT"
        assert info["oid"] == "1.3.6.1.4.1.1847.2021.1.3"


def test_dcc_not_valid_from_image():
    result = verifier.verify_image(os.path.join("tests", "data", "2.png"))
    assert not result["result"]


def test_dcc_not_valid_from_raw():
    with open(os.path.join("tests", "data", "raw_cert")) as cert:
        result = verifier.verify_raw(cert.read())
        assert not result["result"]


def test_certificates_signatures():
    verify_signature(os.path.join("tests", "data", "shit.png"), True)
    verify_signature(os.path.join("tests", "data", "2.png"), False)
    verify_signature(
        os.path.join("tests", "data", "example_qr_vaccine_recovery.png"), False
    )
    verify_signature(os.path.join("tests", "data", "mouse.jpeg"), True)
    verify_signature(os.path.join("tests", "data", "signed_cert.png"), False)
    verify_signature(os.path.join("tests", "data", "uk_qr_vaccine_dose1.png"), False)


def test_invalid_certificates():
    verify_rules_from_image(
        os.path.join("tests", "data", "shit.png"),
        False,
        verifier.Codes.NOT_VALID,
    )
    verify_rules_from_image(
        os.path.join("tests", "data", "2.png"),
        False,
        verifier.Codes.NOT_VALID,
    )
    verify_rules_from_image(
        os.path.join("tests", "data", "mouse.jpeg"),
        False,
        verifier.Codes.NOT_VALID,
    )


def test_certificates_rules():
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_1.png"),
        False,
        verifier.Codes.NOT_VALID,
        "^Doses 1/2 - Vaccination is expired at .*$",
    )
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_2.png"),
        False,
        verifier.Codes.NOT_VALID,
        "^Doses 1/2 - Vaccination is expired at .*$",
    )
    traveller = time_machine.travel(dt.datetime(2021, 10, 1))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_3.png"),
        True,
        verifier.Codes.VALID,
        "^Doses 2/2 - Vaccination is valid .*$",
    )
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_4.png"),
        True,
        verifier.Codes.VALID,
        "^Doses 2/2 - Vaccination is valid .*$",
    )
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_5.png"),
        True,
        verifier.Codes.VALID,
        "^Doses 1/1 - Vaccination is valid .*$",
    )
    traveller.stop()
    traveller = time_machine.travel(dt.datetime(2022, 1, 1))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_6.png"),
        False,
        verifier.Codes.NOT_VALID,
        "^Recovery statement is expired",
    )
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_7.png"),
        False,
        verifier.Codes.NOT_VALID,
        "^Test Result is expired at .*$",
    )
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_8.png"),
        False,
        verifier.Codes.NOT_VALID,
        "^Test Result is expired at .*$",
    )
    # Doses 2/2 needs test with Booster Mode
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_4.png"),
        False,
        verifier.Codes.TEST_NEEDED,
        "^Test needed$",
        verifier.Mode.BOOSTER_DGP,
    )
    # Doses 3/2 ok with Booster Mode
    dcc_booster_vaccination = from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_4.png"),
    )
    dcc_booster_vaccination._payload["v"][-1]["dn"] = 3
    verify_rules_from_certificate(
        dcc_booster_vaccination,
        True,
        verifier.Codes.VALID,
        "^Doses 3/2 - Vaccination is valid .*$",
        verifier.Mode.BOOSTER_DGP,
    )
    traveller.stop()

    # Doses 1/1 Johnson with Booster Mode
    dcc_johnson_vaccination = from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_5.png"),
    )
    dcc_johnson_vaccination._payload["v"][-1]["mp"] = "EU/1/20/1525"

    traveller = time_machine.travel(dt.datetime(2021, 6, 20))
    traveller.start()
    verify_rules_from_certificate(
        dcc_johnson_vaccination,
        False,
        verifier.Codes.TEST_NEEDED,
        "^Test needed$",
        verifier.Mode.BOOSTER_DGP,
    )
    # Doses 2/2 Johnson with Booster Mode
    dcc_johnson_vaccination._payload["v"][-1]["dn"] = 2
    dcc_johnson_vaccination._payload["v"][-1]["sd"] = 2
    verify_rules_from_certificate(
        dcc_johnson_vaccination,
        True,
        verifier.Codes.VALID,
        "^Doses 2/2 - Vaccination is valid .*$",
        verifier.Mode.BOOSTER_DGP,
    )
    traveller.stop()

    # Valid test results
    traveller = time_machine.travel(dt.datetime(2021, 5, 22))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_7.png"),
        True,
        verifier.Codes.VALID,
        "^Test Result is valid .*$",
    )
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_8.png"),
        True,
        verifier.Codes.VALID,
        "^Test Result is valid .*$",
    )
    # Verify with Super Green Pass
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_8.png"),
        False,
        verifier.Codes.NOT_VALID,
        "^Not valid. Super DGP or Booster required.$",
        verifier.Mode.SUPER_GP_MODE,
    )
    # Verify with Booster Mode
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_7.png"),
        False,
        verifier.Codes.NOT_VALID,
        "^Not valid. Super DGP or Booster required.$",
        verifier.Mode.BOOSTER_DGP,
    )
    traveller.stop()
    # Doses 1/2 valid only in Italy
    traveller = time_machine.travel(dt.datetime(2021, 6, 24))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_1.png"),
        True,
        verifier.Codes.VALID,
        "^Doses 1/2 - Vaccination is valid .*$",
    )
    # Doses 1/2 not valid with Booster Mode
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_1.png"),
        False,
        verifier.Codes.NOT_VALID,
        "^Vaccine is not valid in Booster mode$",
        verifier.Mode.BOOSTER_DGP,
    )
    traveller.stop()
    # Test result not valid yet
    traveller = time_machine.travel(dt.datetime(2021, 4, 22))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_7.png"),
        False,
        verifier.Codes.NOT_VALID_YET,
        "^Test Result is not valid yet, starts at .*$",
    )
    traveller.stop()
    # Doses 1/2 not valid yet
    traveller = time_machine.travel(dt.datetime(2021, 5, 24))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_1.png"),
        False,
        verifier.Codes.NOT_VALID_YET,
        "^Doses 1/2 - Vaccination is not valid yet, .*$",
    )
    traveller.stop()
    # Doses 2/2 not valid yet
    traveller = time_machine.travel(dt.datetime(2021, 5, 18))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_3.png"),
        False,
        verifier.Codes.NOT_VALID_YET,
        "^Doses 2/2 - Vaccination is not valid yet, .*$",
    )
    traveller.stop()
    # Doses 2/2 expired
    traveller = time_machine.travel(dt.datetime(2022, 6, 17))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_4.png"),
        False,
        verifier.Codes.NOT_VALID,
        "^Doses 2/2 - Vaccination is expired at .*$",
    )
    traveller.stop()
    # Recovery statement is valid
    traveller = time_machine.travel(dt.datetime(2021, 10, 20))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_6.png"),
        True,
        verifier.Codes.VALID,
        "^Recovery statement is valid$",
    )
    traveller.stop()
    # Recovery statement is not valid yet
    traveller = time_machine.travel(dt.datetime(2021, 4, 22))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_6.png"),
        False,
        verifier.Codes.NOT_VALID_YET,
        "^Recovery statement is not valid yet",
    )
    traveller.stop()
    # Recovery statement is not valid
    traveller = time_machine.travel(dt.datetime(2022, 4, 22))
    traveller.start()
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_6.png"),
        False,
        verifier.Codes.NOT_VALID,
        "^Recovery statement is expired",
    )
    traveller.stop()
    # Recovery needs test with Booster Mode
    verify_rules_from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_6.png"),
        False,
        verifier.Codes.TEST_NEEDED,
        "^Test needed",
        verifier.Mode.BOOSTER_DGP,
    )
    # Not valid greenpass without recovery
    dcc_without_recovery = from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_6.png"),
    )
    dcc_without_recovery._payload["r"] = []
    verify_rules_from_certificate(
        dcc_without_recovery,
        False,
        verifier.Codes.NOT_EU_DCC,
    )
    # Not valid greenpass without tests
    dcc_without_tests = from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_7.png"),
    )
    dcc_without_tests._payload["t"] = []
    verify_rules_from_certificate(
        dcc_without_tests,
        False,
        verifier.Codes.NOT_EU_DCC,
    )
    # Not valid greenpass without vaccinations
    dcc_without_vaccinations = from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_3.png"),
    )
    dcc_without_vaccinations._payload["v"] = []
    verify_rules_from_certificate(
        dcc_without_vaccinations,
        False,
        verifier.Codes.NOT_EU_DCC,
    )
    # Negative vaccination
    dcc_with_negative_vaccination = from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_3.png"),
    )
    dcc_with_negative_vaccination._payload["v"][-1]["dn"] = -1
    verify_rules_from_certificate(
        dcc_with_negative_vaccination,
        False,
        verifier.Codes.NOT_VALID,
    )
    # Malformed vaccination
    dcc_malformed_vaccinations = from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SK_3.png"),
    )
    dcc_malformed_vaccinations._payload["v"][-1]["dn"] = "a"
    verify_rules_from_certificate(
        dcc_malformed_vaccinations,
        False,
        verifier.Codes.NOT_VALID,
    )
    # SM vaccination (Sputnik-V)
    dcc_sm_sputnik = from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SM_1.png"),
    )
    verify_rules_from_certificate(
        dcc_sm_sputnik,
        True,
        verifier.Codes.VALID,
    )
    # Other countries vaccination with Sputnik-V
    dcc_it_sputnik = from_image(
        os.path.join("tests", "data", "eu_test_certificates", "SM_1.png"),
    )
    dcc_it_sputnik._payload["v"][0]["co"] = "IT"
    verify_rules_from_certificate(
        dcc_it_sputnik,
        False,
        verifier.Codes.NOT_VALID,
    )

    # Verify exemption rules
    exemption_certificate = dcc_without_vaccinations
    del exemption_certificate._payload["v"]
    exemption_certificate._payload["e"] = [
        {
            "df": "2021-02-15",
            "du": "2021-12-15",
            "co": "IT",
            "ci": "TESTIDFAKEEXEMPTION#2",
            "is": "",
            "tg": "",
        }
    ]

    traveller = time_machine.travel(dt.datetime(2021, 5, 22))
    traveller.start()
    verify_rules_from_certificate(
        exemption_certificate,
        True,
        verifier.Codes.VALID,
        r"^Exemption is valid \[2021-02-15 - 2021-12-15\]$",
    )

    verify_rules_from_certificate(
        exemption_certificate,
        False,
        verifier.Codes.TEST_NEEDED,
        "^Test needed$",
        verifier.Mode.BOOSTER_DGP,
    )
    traveller.stop()
    traveller = time_machine.travel(dt.datetime(2022, 5, 23))
    traveller.start()
    verify_rules_from_certificate(
        exemption_certificate,
        False,
        verifier.Codes.NOT_VALID,
        "^Exemption is expired at: 2021-12-15$",
    )
    traveller.stop()
    traveller = time_machine.travel(dt.datetime(2020, 5, 22))
    traveller.start()
    verify_rules_from_certificate(
        exemption_certificate,
        False,
        verifier.Codes.NOT_VALID_YET,
        "^Exemption is not valid yet, starts at: 2021-02-15$",
    )
    traveller.stop()
