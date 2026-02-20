from logan.parser import parse_line


def test_parse_format1():
    e = parse_line("2026-02-20 07:18:12 [ERROR] [auth] login failed\n")
    assert e.level == "ERROR"
    assert e.module == "auth"
    assert e.timestamp is not None


def test_parse_fallback_level():
    e = parse_line("something happened ERROR cannot connect\n")
    assert e.level == "ERROR"
