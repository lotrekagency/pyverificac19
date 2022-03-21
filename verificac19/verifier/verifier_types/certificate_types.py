from enum import Enum, auto, unique

@unique
class CertificateType(Enum):
    VACCINATION = 'vaccination'
    RECOVERY = 'recovery'
    TEST = 'test'
    ESEMPTION = 'esemption'
