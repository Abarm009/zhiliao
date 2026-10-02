"""用于排查 conftest 路径的 dummy 测试。"""
def test_import_works():
    import octosense_backend.errors as err
    assert err.OctoSenseError is not None
