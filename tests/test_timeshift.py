import pytest

from timewarp.timeshift import timeshift_json


@pytest.fixture
def dateonly():
    return {"d1": "2025-01-01"}


def test_dateshift(dateonly):
    result = timeshift_json(dateonly, num_days=1, exclusion_list=[])
    assert result == {"d1": "2025-01-02"}


@pytest.fixture
def datetimeonly():
    return {"dt1": "2025-01-01T01:01:00Z"}


def test_no_dateshift(datetimeonly):
    result = timeshift_json(datetimeonly, num_days=0, exclusion_list=[])
    assert result == datetimeonly


def test_dateshift(datetimeonly):
    result = timeshift_json(datetimeonly, num_days=30, exclusion_list=[])
    assert result["dt1"] == "2025-01-31T01:01:00Z"
