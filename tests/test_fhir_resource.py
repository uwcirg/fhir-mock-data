import pytest

from timewarp.fhir_resource import FHIR_Resource, Patient, MedicationRequest


@pytest.fixture
def patient_resource(datadir):
    filepath = str(datadir / "Patient.json")
    return FHIR_Resource.parse_file(filepath)


def test_parse_patient(patient_resource):
    assert isinstance(patient_resource, Patient)


def test_patient_exclusions(patient_resource):
    assert patient_resource.exclusion_attributes() == ["lastUpdated", "birthDate"]


def test_timeshit_patient(patient_resource):
    patient_resource.timeshift()


@pytest.fixture
def medrequest_resource(datadir):
    filepath = str(datadir / "MedicationRequest.json")
    return FHIR_Resource.parse_file(filepath)


def test_parse_medrequest(medrequest_resource):
    assert isinstance(medrequest_resource, MedicationRequest)


def test_medrequest_exclusions(medrequest_resource):
    assert medrequest_resource.exclusion_attributes() == ["lastUpdated"]


