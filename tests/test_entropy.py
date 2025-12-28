from pwstrength.features.entropy import length_and_classes, shannon_entropy_total


def test_entropy_empty_string():
    assert shannon_entropy_total("") == 0.0


def test_entropy_repeated_vs_distinct():
    repeated = shannon_entropy_total("aaaaaaaa")
    distinct = shannon_entropy_total("abcdefgh")
    assert repeated < distinct


def test_entropy_monotonicity():
    prev = 0.0
    for candidate in ["a", "aa", "aaa", "aaaa"]:
        current = shannon_entropy_total(candidate)
        assert current >= prev
        prev = current


def test_length_and_classes_flags():
    length, class_count, flags = length_and_classes("Aa1!")
    assert length == 4
    assert class_count >= 3
    assert flags["lower"] and flags["upper"] and flags["digit"]
