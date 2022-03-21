from enum import Enum, auto, unique

@unique
class CertificateType(Enum):
    VACCINATION_IT = 'vaccination_it'
    VACCINATION_NOT_IT = 'vaccintaion_not_it'

    RECOVERY_IT = 'recovery_it'
    RECOVERY_NOT_IT = 'recovery_not_it'

    TEST = 'test'

    ESEMPTION = 'esemption'
