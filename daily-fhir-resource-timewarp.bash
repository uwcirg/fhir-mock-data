#!/bin/bash

FEMR_DIR="/home/pbugni/cosri-environments/dev/freestanding/femr"
TMP_DIR="/tmp/fhir-timewarp"
SYSTEM="demo"
LOG_FILE="/var/log/fhir-timewarp/${SYSTEM}-$(date +%F).log"

cd "$FEMR_DIR" || { echo "directory not found $FEMR_DIR" | tee -a "$LOG_FILE"; exit 1; }

# Lookup fhir-internal network from running docker `fhir` container
INTERNAL_FHIR=$(docker inspect $(docker compose ps -q fhir) \
  --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}} {{end}}' \
  | awk '{print $2}')

# Confirm presence of the temporary directory, and purge to avoid
# timewarping stale files

if [ ! -d "$TMP_DIR" ]; then
  mkdir "$TMP_DIR" || { echo "can't create tmp dir $TMP_DIR" | tee -a "$LOG_FILE"; exit 1; }
fi

# Delete files but not directory
find "$TMP_DIR" -type f -delete 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Error: couldn't delete files in $TMP_DIR" | tee -a "$LOG_FILE"
  exit 1
fi

# Run the timewarp process against:
#   the desired FHIR endpoint, number of days, named temp directory
docker run --network $INTERNAL_FHIR -v /tmp/fhir-timewarp:/tmp/fhir-timewarp \
  --pull always ghcr.io/uwcirg/fhir-mock-data:latest \
  http://fhir-internal:8080/fhir 1 /tmp/fhir-timewarp > "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
  exit 0
else
  echo "Daily timewarp of $SYSTEM failed.  See $LOG_FILE"
  exit 1
fi

