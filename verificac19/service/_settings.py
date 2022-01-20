from typing import Dict

Dsc = Dict[str, str]

API_URL = "https://get.dgc.gov.it/v1/dgc"

DSC_URL = f"{API_URL}/signercertificate/update"
STATUS_URL = f"{API_URL}/signercertificate/status"
SETTINGS_URL = f"{API_URL}/settings"

DSC_FILE_CACHE_PATH = "dsc.json"
SETTINGS_FILE_CACHE_PATH = "settings.json"
CHECK_CRL_URL = f"{API_URL}/drl/check"
DOWNLOAD_CRL_URL = f"{API_URL}/drl"
CRL_FILE_CACHE = "crl_check.json"

MAX_ERRORS_CRL_DOWNLOAD = 3
