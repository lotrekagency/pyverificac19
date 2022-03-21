from typing import Any, Callable

class AsserterCheck:
    checks_count = -1

    def __init__(self):
        AsserterCheck.checks_count += 1

    def __call__(self, fun: Callable) -> Callable:
        fun.asserter_check_order = AsserterCheck.checks_count
        return fun
