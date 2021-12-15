from dcc_utils import from_image, from_raw

super_gp_mode = "2G"

class Verifier():

    @staticmethod
    def verify_image(path, super_gp_mode=super_gp_mode):
        mydcc = from_image(path)
        return mydcc

    @staticmethod
    def verify_raw(raw,super_gp_mode=super_gp_mode):
        mydcc = from_raw(raw)
        return mydcc
