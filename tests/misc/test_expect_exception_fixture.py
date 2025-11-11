import pytest

def test_expected_via_fixture(expect_raises):
    with expect_raises(KeyError, contains="token"):
        raise KeyError("missing token in payload")
