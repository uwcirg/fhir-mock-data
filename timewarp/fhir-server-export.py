#!/usr/bin/env python3
"""Util to download all resources from the given FHIR server"""
import argparse, requests, sys, json, time


def download_file(url, filename=None, auth_token=None):
    """Download given large file via streaming"""
    # https://stackoverflow.com/a/16696317
    headers = {}
    if auth_token is not None:
        headers["Authorization"] = f"Bearer {auth_token}"

    if not filename:
        filename = url.split("/")[-1]
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                # if chunk:
                f.write(chunk)
    return filename


def fixup_url(url, base_url):
    """
    Replace FHIR base URL in given FHIR API call with different base_url
    Helpful when a FHIR server is configured with a server_name that does not match its public one
    No generalized solution when urls significantly different
    """

    # Hapi ignores server_name configuration
    if base_url.startswith("https://"):
        url = url.replace("http://", "https://")

    if url.startswith(base_url):
        return url

    second_last_path, last_path = url.split("/")[-2:]
    # FHIR operations
    if last_path.startswith("$"):
        return f"{base_url}/{last_path}"

    # known resources (Hapi FHIR uses Binary)
    if second_last_path in ("Binary"):
        return f"{base_url}/{second_last_path}/{last_path}"


def poll_status(status_poll_url, auth_token=None, max_rety_time=600):
    """Poll given status URL until ready (or timeout). Returns response JSON when ready to download"""

    headers = {}
    if auth_token is not None:
        headers["Authorization"] = f"Bearer {auth_token}"

    rety_time = 0
    while rety_time < max_rety_time:
        status_poll_response = requests.get(status_poll_url, headers=headers)
        status_poll_response.raise_for_status()

        retry_after = int(status_poll_response.headers.get("Retry-After", 0))
        if not retry_after:
            return status_poll_response

        progress = status_poll_response.headers.get("X-Progress")
        if progress:
            print("progress: ", progress)

        print(f"waiting {retry_after} seconds")
        rety_time += retry_after
        time.sleep(retry_after)
    print("timeout exceeded")
    exit(1)


def kickoff(base_url, no_cache=False, auth_token=None, type=None, since=None):
    """Initate a Bulk Export, return endpoint to poll"""
    headers = {
        "Accept": "application/fhir+json",
        "Prefer": "respond-async",
    }

    params = {}
    if no_cache:
        print("server-side caching disabled")
        headers["Cache-control"] = "no-cache"

    if auth_token is not None:
        headers["Authorization"] = f"Bearer {auth_token}"

    if type is not None:
        params["_type"] = type

    if since is not None:
        params["_since"] = since

    kickoff_response = requests.get(
        url=f"{base_url}/$export",
        headers=headers,
        params=params,
    )
    # raise exceptions when response status is not 2XX
    try:
        kickoff_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("recieved error from Hapi in kickoff request")
        print("response: ", kickoff_response.content)
        if kickoff_response.status_code == 400:
            print("recieved 400 in kickoff response; is Bulk Export enabled?")
        exit(1)

    return kickoff_response.headers["Content-Location"]


def main():
    parser = argparse.ArgumentParser(description="Download FHIR resources using Bulk Export")
    parser.add_argument("base_url", help="FHIR base URL")
    parser.add_argument("--directory", action="store", help="Save files to given directory", default="./")
    parser.add_argument("--no-cache", action="store_true", help="Disable server-side caching")
    parser.add_argument("--max-timeout", action="store", help="Max timeout in seconds before failing", type=int, default=60*10)
    parser.add_argument("--auth-token", action="store", help="Use given token to authenticate")
    parser.add_argument("--type", action="store", help="Restrict Export to specific (comma-separated) resource types; see _type")
    parser.add_argument("--since", action="store", help="Restrict Export to resources last updated on or after the given time (format eg '2019-10-25T11:14:00Z'); see _since")

    args = parser.parse_args()

    status_poll_url = kickoff(
        base_url=args.base_url,
        no_cache=args.no_cache,
        auth_token=args.auth_token,
        type=args.type,
        since=args.since,
    )
    complete_response = poll_status(
        fixup_url(url=status_poll_url, base_url=args.base_url),
        auth_token=args.auth_token,
        max_rety_time=args.max_timeout,
    )
    try:
        complete_json = complete_response.json()
    except json.decoder.JSONDecodeError:
        print("error: export completed successfully, but response is not JSON: ", complete_response.text)
        print("warning: the Bulk Export request (for Hapi) likely did not return any resources")
        exit(1)

    errors = complete_json.get("errors")
    if errors:
        print(errors)

    file_items = complete_json.get("output")
    if not file_items:
        print("warning: no files listed in Complete status response:")
        print(complete_json)
        exit(1)

    for file_item in file_items:
        url = fixup_url(url=file_item["url"], base_url=args.base_url)

        local_filename = ".".join((
            url.split("/")[-1],
            file_item["type"],
            "ndjson",
        ))
        local_filename = f"{args.directory}{local_filename}"
        print("downloading: ", url)
        download_file(url=url, filename=local_filename, auth_token=args.auth_token)
        print("saved to: ", local_filename)


if __name__ == "__main__":
    main()
