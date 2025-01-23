import pytest
from timewarp.input_util import determine_file_type


def test_single_line_nd(datadir):
    """Single line NDJSON is also a valid JSON file"""
    assert determine_file_type(datadir / "MedicationRequest.ndjson") == "JSON"


def test_multi_line_json(datadir):
    assert determine_file_type(datadir / "valid.json") == "JSON"


def test_valid_nd(datadir):
    assert determine_file_type(datadir / "Patient.ndjson") == "NDJSON"


def test_invalid(datadir):
    with pytest.raises(ValueError):
        determine_file_type(datadir / "bogus.json")
