from typing import Any, Callable, Union, Tuple, List
from dcc_utils import dcc
from dcc_utils.exceptions import DCCParsingError
from verificac19.verifier.decorators import AsserterCheck

class BaseAsserter:
    def __init__(self, dcc: dcc.DCC):
        self.__store_asserter_check_methods()

        self.dcc = dcc
        self.payload = self.dcc.payload

    def run_checks(self):
        for check in self._checks:
            result = check()
            if result:
                return result

    def __store_asserter_check_methods(self):
        all_properties = self.__list_of_properties()
        properties_with_order = filter(self.__is_function_asserter_check, all_properties)
        asserter_checks = sorted(properties_with_order, key=self.__get_asserter_check_order)
        self._checks = asserter_checks

    def __list_of_properties(self):
        properties_strings = dir(self)
        return [ getattr(self, property) for property in properties_strings ]

    def __is_function_asserter_check(self, fun: Any) -> bool:
        return hasattr(fun, 'asserter_check_order')

    def __get_asserter_check_order(self, fun) -> int:
        order = getattr(fun, 'asserter_check_order', -1)
        return order
