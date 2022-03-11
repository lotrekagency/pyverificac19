from typing import Any, Callable

class VerifierCheck:
    checks_count = -1

    def __init__(self):
        VerifierCheck.checks_count += 1

    def __call__(self, fun: Callable) -> Callable:
        fun.verifier_check_order = VerifierCheck.checks_count
        return fun
