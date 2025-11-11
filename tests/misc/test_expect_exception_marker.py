import pytest
pytestmark = pytest.mark.api

@pytest.mark.expect_exception(exc=ValueError, match=r"bad things?")
def test_expected_via_marker():
    raise ValueError("very bad things?")
