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

from fhir_resource import FHIR_Resource
from input_util import next_json_object


def bail(reason=None):
    """Print usage and exit"""
    output = usage.format(script=sys.argv[0])
    if reason:
        output = f"{output}\nERROR:\n  {reason}"
    print(output, file=sys.stderr)
    sys.exit(-1)


def move_24_ahead(source_dir, fhir_base_url, num_days):
    """Update the FHIR resources found in files, num_days forward in time"""
    def timeshift_resource(data):
        fhir_data = FHIR_Resource.parse_fhir(data)
        changed = fhir_data.timeshift(num_days=num_days)

        # PUT the time warped data to the requested FHIR server
        if changed:
            url = f"{fhir_base_url}{fhir_data.resource_type}/{fhir_data.data['id']}"
            print(f"PUT timeshift change to {url}")
            response = requests.put(url, json=fhir_data.data)
            response.raise_for_status()

    for filename in os.listdir(source_dir):
        # could be single JSON file, or NDJSON
        for data in next_json_object(os.path.join(source_dir, filename)):
            timeshift_resource(data)
    print(f"timeshift of {num_days} days complete")


def main():
    if len(sys.argv) < 3:
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

    num_days = 1
    if len(sys.argv) > 3:
        num_days = int(sys.argv[3])
    if not fhir_base_url.endswith('/'):
        fhir_base_url += '/'

    return move_24_ahead(input_dir, fhir_base_url, num_days)


if __name__ == "__main__":
    main()
