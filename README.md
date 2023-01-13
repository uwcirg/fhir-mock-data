# FHIR Mock Data

## Upload

To upload a FHIR transaction Bundle JSON file (`${FHIR_BUNDLE}`) to a FHIR server (`${FHIR_BASE_URL}`), invoke `curl` as follows:

```
curl --header "Content-Type: application/json" --data @${FHIR_BUNDLE} ${FHIR_BASE_URL}
```
