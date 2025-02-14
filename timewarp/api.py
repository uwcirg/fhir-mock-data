usage = """Usage:
  {script} <input_directory> <FHIR_BASE_URL>

Description:
  for all JSON or NDJSON files found in <input_directory>, adjust the contained
  FHIR Resources ahead in time 24 hours, and POST to the given <FHIR_BASE_URL>
  
  Note: exceptions exist for details like a Patient.birthDate to provide for
  consistent lookup.
"""
import os
import requests
import sys

from .fhir_resource import FHIR_Resource
from .input_util import next_json_object


def bail(reason=None):
    """Print usage and exit"""
    output = usage.format(script=sys.argv[0])
    if reason:
        output = f"{output}\nERROR:\n  {reason}"
    sys.exit(-1)


def move_24_ahead(source_dir, fhir_base_url):
    """POST the FHIR resources found in files, 24 hours forward in time"""
    def timeshift_resource(data):
        fhir_data = FHIR_Resource.parse_fhir(data)
        changed = fhir_data.timeshift(num_days=1)

        # POST the time warped data to the requested FHIR server
        if changed:
            requests.POST(fhir_base_url + fhir_data.resource_type, json=fhir_data)

    for filename in os.listdir(source_dir):
        # could be single JSON file, or NDJSON
        for data in next_json_object(filename):
            timeshift_resource(data)


def main():
    if len(sys.argv != 2):
        bail("wrong arg count")
    input_dir = sys.argv[1]
    if not os.path.isdir(input_dir):
        bail(f"can't access input directory `{input_dir}`")
    fhir_base_url = sys.argv[2]
    response = requests.options(fhir_base_url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as he:
        bail(he.response.text)

    if not fhir_base_url.endswith('/'):
        fhir_base_url += '/'

    return move_24_ahead(input_dir, fhir_base_url)


if __name__ == "__main__":
    main()
