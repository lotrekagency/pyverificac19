from verificac19 import sum
from verificac19.exceptions import VerificaC19Error

print(sum(2, 3))

try:
    print(sum(-1, -2))
except VerificaC19Error as ex:
    print(ex)
