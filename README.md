# FHIR Mock Data

## Timewarp

Used to keep demo data in sync, the timewarp utility will advance all date and
datetime attributes found (excluding a few such as Patient.birthDate) in the
provided FHIR store, a given number of days, and then PUT the changed files
back to the same named HAPI store.

Example use:

First, obtain the network address for the FHIR endpoint to be timewarped.  As
an example, from the same directory as the docker-compose.yaml containing the
FHIR endpoint of interest (fhir-internal network in this case):

```
$ INTERNAL_FHIR=$(docker inspect $(docker compose ps -q fhir) --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' | awk '{print $2}')
```

Then, run a container built from this repository, naming the network, volume
and arguments to move all found FHIR resources forward 1 day:

```
$ docker run --network $INTERNAL_FHIR -v /tmp/fhir-timewarp:/tmp/fhir-timewarp --pull always ghcr.io/uwcirg/fhir-mock-data:latest http://fhir-internal:8080/fhir 1 /tmp/fhir-timewarp
```


## Upload

To upload a FHIR transaction Bundle JSON file (`${FHIR_BUNDLE}`) to a FHIR server (`${FHIR_BASE_URL}`), invoke `curl` as follows:

```
curl --header "Content-Type: application/json" --data @${FHIR_BUNDLE} ${FHIR_BASE_URL}
```
