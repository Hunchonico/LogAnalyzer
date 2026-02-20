from logan.parser import parse_line
from logan.analyze import analyze


def test_analyze_counts():
    lines = [
        "2026-02-20 07:18:12 [INFO] [core] ok\n",
        "2026-02-20 07:18:13 [ERROR] [db] failed id=123\n",
        "2026-02-20 07:18:14 [ERROR] [db] failed id=999\n",
    ]
    entries = [parse_line(x) for x in lines]
    res = analyze(entries, top_n=5)
    assert res.total_lines == 3
    assert res.level_counts["ERROR"] == 2
    assert res.top_modules[0][0] == "db"
    assert res.top_error_messages[0][1] == 2 
