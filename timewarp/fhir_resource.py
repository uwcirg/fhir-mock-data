"""FHIR resource abstraction for time warp needs

In general, every element in a FHIR resource should be warped a consistent
amount of time forward.  The abstractions herein manage exceptions such
as metadata
"""

import json
from typing import Type, Dict

from timewarp.timeshift import timeshift_json


class FHIR_Resource:
    """
    Base class for FHIR resources. Provides a factory method `parse_file`
    to instantiate the correct subclass based on the `resourceType`.
    """
    resource_type_map: Dict[str, Type['FHIR_Resource']] = {}

    def __init__(self, data: dict = None):
        self.data = data

    @property
    def resource_type(self):
        return self.data and self.data.get('resourceType')

    @classmethod
    def register_resource(cls, resource_type: str):
        """
        Decorator to register a subclass in the resource type map.
        """
        def decorator(subclass: Type['FHIR_Resource']):
            cls.resource_type_map[resource_type] = subclass
            return subclass
        return decorator

    @classmethod
    def parse_file(cls, file_path: str) -> 'FHIR_Resource':
        """
        Factory method to parse a JSON file and return the appropriate subclass instance.
        """
        with open(file_path, 'r') as file:
            data = json.load(file)

        resource_type = data.get('resourceType')
        if not resource_type:
            raise ValueError("The JSON file does not contain a 'resourceType' field.")

        subclass = cls.resource_type_map.get(resource_type)
        if not subclass:
            raise ValueError(f"Unsupported resourceType: {resource_type}")

        return subclass.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> 'FHIR_Resource':
        """
        Create an instance of the class from a dictionary.
        Should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the `from_dict` method.")

    def exclusion_attributes(self) -> 'list':
        """
        Subclasses mad define list of attributes (of datetime type)
        to be excluded from timewarp.  list contains attribute names
        """
        return ["lastUpdated"]

    def timeshift(self):
        self.data = timeshift_json(
            self.data, num_days=1, exclusion_list=self.exclusion_attributes())


@FHIR_Resource.register_resource("Patient")
class Patient(FHIR_Resource):
    def __init__(self, data: dict = None):
        super().__init__(data)

    @classmethod
    def from_dict(cls, data: dict) -> 'Patient':
        return cls(data)

    def exclusion_attributes(self) -> 'list':
        """ Return list of Patient datetime attributes to be excluded from timewarp """
        ex_list = super().exclusion_attributes()
        ex_list.append("birthDate")
        return ex_list


@FHIR_Resource.register_resource("MedicationRequest")
class MedicationRequest(FHIR_Resource):
    def __init__(self, data: dict = None):
        super().__init__(data)

    @classmethod
    def from_dict(cls, data: dict) -> 'MedicationRequest':
        return cls(data)
