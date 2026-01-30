from dcvt.match import match_vendor


def test_match_with_exact_name():
    master = ["Acme Corp", "Beta LLC", "Gamma Inc"]
    assert match_vendor("Acme Corp", master, threshold=80) == "Acme Corp"


def test_match_partial_name():
    master = ["Acme Corporation", "Beta LLC", "Gamma Inc"]
    assert match_vendor("Acme Corp", master, threshold=60) in (
        "Acme Corporation",
        "Acme Corp",
    )


def test_no_match_low_threshold():
    master = ["Alpha", "Beta"]
    assert match_vendor("Zeta", master, threshold=95) == ""


def test_empty_master():
    assert match_vendor("Any", [], threshold=80) == ""
