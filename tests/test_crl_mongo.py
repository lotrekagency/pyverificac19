from verificac19.service.crl.mongo import MongoCRL


crl = MongoCRL()


def test_mongo_crl_insert_and_deletions():
    crl.update_crl(["a", "b"], ["b"])
    assert crl.is_uvci_revoked("a")
    crl.clean_all()
    assert not crl.is_uvci_revoked("a")


def test_mongo_crl_multiple_insert():
    crl.update_crl(["a", "b"], ["b"])
    crl.update_crl(["a", "b", "c"])
    assert crl.is_uvci_revoked("a")
    assert crl.is_uvci_revoked("b")
    assert crl.is_uvci_revoked("c")
    crl.clean_all()
    assert not crl.is_uvci_revoked("a")
    assert not crl.is_uvci_revoked("b")
    assert not crl.is_uvci_revoked("c")
