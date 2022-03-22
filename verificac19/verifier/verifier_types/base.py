from enum import Enum, auto
from typing import Any, Callable, Union, Tuple, List
from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError
from .certificate_types import CertificateType
from verificac19.verifier.common.result import NOTHING_FOUND
from verificac19.verifier.asserters import BaseAsserter
import inspect



class BaseVerifier:

    vaccination = None
    recovery = None
    test = None,
    esemption = None,


    def __init__(self, dcc: dcc.DCC):
        self.dcc = dcc
        self.payload = self.dcc.payload
        self._result = None


    def _setup_asserter(self):
        valid_type = self._check_certificate_type()
        if not valid_type:
            return

        self._set_asserter()

    def verify(self):
        if self._result:
            return self._result

        self._result = self._asserter.run_checks()
        return self._result

    def _set_asserter(self):
        asserter_name = self._certificate_type.value
        AsserterClass = getattr(self, asserter_name)
        error_msg = f"Expected subclass of BaseAsserter, got {AsserterClass}"

        if inspect.isclass(AsserterClass):
            raise ValueError(error_msg)
        if not issubclass(AsserterClass, BaseAsserter):
            raise ValueError(error_msg)

        self._asserter = AsserterClass(self.dcc)


    def _check_certificate_type(self) -> bool:
        self._certificate_type = None

        if "v" in self.payload:
            self._certificate_type = CertificateType.VACCINATION
        elif "r" in self.payload:
            self._certificate_type = CertificateType.RECOVERY
        elif "t" in self.payload:
            self._certificate_type = CertificateType.TEST
        elif "e" in self.payload:
            self._certificate_type = CertificateType.ESEMPTION

        if self._certificate_type:
            return True

        self._result = NOTHING_FOUND
        return False
