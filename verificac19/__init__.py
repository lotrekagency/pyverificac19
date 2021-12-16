from .exceptions import VerificaC19Error
from .service import service
from .verifier import verifier

__version__ = "0.0.0"


def sum(a: int, b: int) -> int:
    if a < 0 or b < 0:
        raise VerificaC19Error("Negative numbers not allowed!")
    return a + b
