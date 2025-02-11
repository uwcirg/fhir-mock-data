from copy import deepcopy
import json
import pytest

from timewarp.fhir_resource import (
    FHIR_Resource,
    Patient,
)


@pytest.fixture
def patient_resource(datadir):
    filepath = str(datadir / "Patient.json")
    with open(filepath, "r") as json_file:
        data = json.load(json_file)
    return FHIR_Resource.parse_fhir(data)


def test_parse_patient(patient_resource):
    assert isinstance(patient_resource, Patient)


def test_patient_exclusions(patient_resource):
    assert patient_resource.exclusion_attributes() == ["lastUpdated", "birthDate"]


def test_timeshit_patient(patient_resource):
    assert patient_resource.timeshift(num_days=1) is False


@pytest.fixture
def medrequest_resource(datadir):
    filepath = str(datadir / "MedicationRequest.json")
    with open(filepath, "r") as json_data:
        data = json.load(json_data)
    return FHIR_Resource.parse_fhir(data)


def test_parse_medrequest(medrequest_resource):
    assert isinstance(medrequest_resource, FHIR_Resource)
    assert medrequest_resource.resource_type == "MedicationRequest"


def test_medrequest_exclusions(medrequest_resource):
    assert medrequest_resource.exclusion_attributes() == ["lastUpdated"]


def test_medrequest_timeshift(medrequest_resource):
    assert medrequest_resource.data['authoredOn'] == "2024-11-06"
    assert medrequest_resource.timeshift(num_days=20) is True
    assert medrequest_resource.data['authoredOn'] == "2024-11-26"


@pytest.fixture
def encounter_resource(datadir):
    filepath = str(datadir / "Encounter.ndjson")
    with open(filepath, "r") as json_data:
        data = json.load(json_data)
    return FHIR_Resource.parse_fhir(data)


def test_parse_encounter(encounter_resource):
    assert isinstance(encounter_resource, FHIR_Resource)
    assert encounter_resource.resource_type == "Encounter"
    data_b4 = deepcopy(encounter_resource.data)
    assert encounter_resource.timeshift(num_days=1) is False
    assert data_b4 == encounter_resource.data


@pytest.fixture
def qnr_resource(datadir):
    filepath = str(datadir / "QuestionnaireResponse.json")
    with open(filepath, "r") as json_data:
        data = json.load(json_data)
    return FHIR_Resource.parse_fhir(data)


def test_parse_qnr(qnr_resource):
    data_b4 = deepcopy(qnr_resource.data)
    assert qnr_resource.timeshift(num_days=1) is True
    assert data_b4['authored'] != qnr_resource.data['authored']
    # authored should be only value changed
    data_b4['authored'] = qnr_resource.data['authored']
    assert data_b4 == qnr_resource.data


@pytest.fixture
def location_resource(datadir):
    filepath = str(datadir / "Location.json")
    with open(filepath, "r") as json_data:
        data = json.load(json_data)
    return FHIR_Resource.parse_fhir(data)


def test_parse_location(location_resource):
    assert location_resource.timeshift(num_days=1) is False


@pytest.fixture
def procedure_resource(datadir):
    filepath = str(datadir / "Procedure.json")
    with open(filepath, "r") as json_data:
        data = json.load(json_data)
    return FHIR_Resource.parse_fhir(data)


def test_parse_procedure(procedure_resource):
    data_b4 = deepcopy(procedure_resource.data)
    assert procedure_resource.timeshift(num_days=1) is True
    assert data_b4['performedDateTime'] != procedure_resource.data['performedDateTime']
    # should be only value changed
    data_b4['performedDateTime'] = procedure_resource.data['performedDateTime']
    assert data_b4 == procedure_resource.data
