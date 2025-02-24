usage = """Usage:
  {script} <FHIR_BASE_URL> [NUM_DAYS] [TMP_DIR]

Positional Arguments:
  FHIR_BASE_URL  The base URL of the FHIR store to query and store the time shifted FHIR resources
  NUM_DAYS    Optional number of days to move date and time values forward, defaults to 1
  TMP_DIR    Optional temporary directory to use, defaults to /tmp
  
Description:
  Query the FHIR store at FHIR_BASE_URL for all contained FHIR resources.  Shift
  all but a few excluded date and time values forward NUM_DAYS.  Excluded values
  include `Patient.birthDate` and all `meta.lastUpdated` fields.  All FHIR resources
  changed in the process will be PUT back to the same FHIR_BASE_URL.
"""
import os
import requests
import sys

from fhir_resource import FHIR_Resource
from fhir_server_export import run_export
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
    print(f"timeshift of {num_days} day(s) complete")


def main():
    """Main function, see `usage` as top of file for documentation."""
    if len(sys.argv) < 2:
        bail("requires FHIR_BASE_URL")
    fhir_base_url = sys.argv[1]
    response = requests.options(fhir_base_url)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as he:
        bail(f"Unable to access FHIR_BASE_URL: {fhir_base_url}, {he.response.text}")

    num_days = 1
    if len(sys.argv) > 2:
        num_days = int(sys.argv[2])

    input_dir = '/tmp'
    if len(sys.argv) > 3:
        input_dir = sys.argv[3]
        if not os.path.isdir(input_dir):
            bail(f"can't access input directory `{input_dir}`")

    if not fhir_base_url.endswith('/'):
        fhir_base_url += '/'

    # Export all FHIR resources to temp directory
    run_export(base_url=fhir_base_url, directory=input_dir)

    # Timeshift and PUT any changed resources back to FHIR store
    return move_24_ahead(input_dir, fhir_base_url, num_days)


if __name__ == "__main__":
    main()
