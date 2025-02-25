"""FHIR resource abstraction for time warp needs

In general, every element in a FHIR resource should be warped a consistent
amount of time forward.  The abstractions herein manage exceptions such
as metadata and birthdate.
"""
from copy import deepcopy
from typing import Type, Dict

from timeshift import timeshift_json


class FHIR_Resource:
    """FHIR Resource base class for time warp needs.

    Specialize subclasses for specific time warp needs.
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
    def parse_fhir(cls, data: dict) -> 'FHIR_Resource':
        """
        Factory method to parse a JSON dict and return the base class or appropriate
        subclass instance when applicable.
        """
        resource_type = data.get('resourceType')
        if not resource_type:
            raise ValueError("The JSON file does not contain a 'resourceType' field.")

        subclass = cls.resource_type_map.get(resource_type)
        if not subclass:
            # w/o subclass, no specialization needed; return base class
            subclass = FHIR_Resource()

        return subclass.from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> 'FHIR_Resource':
        return cls(data)

    def exclusion_attributes(self) -> 'list':
        """
        Subclasses mad define list of attributes (of datetime type)
        to be excluded from timewarp.  list contains attribute names
        """
        return ["lastUpdated"]

    def timeshift(self, num_days: int) -> bool:
        """Timeshift forward requested number of days

        :returns: True if timeshift resulted in any change, False otherwise
        """
        data_b4 = deepcopy(self.data)
        self.data = timeshift_json(
            self.data, num_days=num_days, exclusion_list=self.exclusion_attributes())
        return data_b4 != self.data


@FHIR_Resource.register_resource("Patient")
class Patient(FHIR_Resource):
    def __init__(self, data: dict = None):
        super().__init__(data)

    def exclusion_attributes(self) -> 'list':
        """ Return list of Patient datetime attributes to be excluded from timewarp """
        ex_list = super().exclusion_attributes()
        ex_list.append("birthDate")
        return ex_list
