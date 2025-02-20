# FHIR Mock Data

## Timewarp

Used to keep demo data in sync, the timewarp utility will advance all date and
datetime attributes found in the named directory of FHIR Resource files, a 
given number of days and then PUT the changed files to the named HAPI store.

Example use:

Copy `fhir-walk.py` into the `timewarp` container and export current resources:
```
docker cp ~/fhir-walk/fhir-walk.py `docker ps|grep timewarp|awk '{print $1}'`:.
docker-compose exec timewarp bash
/fhir-walk.py /tmp http://fhir-internal:8080/fhir
```
Push all but the excluded date/time fields (such as `metadata` and
`Patient.birthdate`) forward 1 day, and put the results back to the same
FHIR store:
```
docker-compose exec timewarp bash
python timewarp/api.py /tmp http://fhir-internal:8080/fhir
```

## Upload

To upload a FHIR transaction Bundle JSON file (`${FHIR_BUNDLE}`) to a FHIR server (`${FHIR_BASE_URL}`), invoke `curl` as follows:

```
curl --header "Content-Type: application/json" --data @${FHIR_BUNDLE} ${FHIR_BASE_URL}
```
