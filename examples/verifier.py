import os
from verificac19 import verifier


outcome = verifier.verify_image(os.path.join("tests", "data", "2.png"))
print(outcome)
