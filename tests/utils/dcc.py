import json
import os
from dcc_utils.dcc import from_image

def get_dcc_from_image(image_name:str):
    image = os.path.join("tests", "data", "eu_test_certificates", image_name)
    dcc = from_image(image)
    return dcc

def open_json(name: str) -> dict:
    path = os.path.join("tests", "data", "mock_request", name)
    with open(path, "r") as file:
        return json.load(file)
