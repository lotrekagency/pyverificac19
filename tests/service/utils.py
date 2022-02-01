import os
import json


def open_json(name: str) -> dict:
    path = os.path.join("tests", "data", "mock_request", name)
    with open(path, "r") as file:
        return json.load(file)
