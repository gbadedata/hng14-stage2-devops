#!/bin/bash
set -e

echo "Starting integration test..."

# Start the stack
docker compose up -d --build
echo "Waiting for services to be healthy..."
sleep 30

# Submit a job
echo "Submitting job..."
RESPONSE=$(curl -sf -X POST http://localhost:3000/submit \
  -H "Content-Type: application/json" \
  -d '{}')
echo "Response: $RESPONSE"

JOB_ID=$(echo $RESPONSE | python3 -c "import json,sys; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: $JOB_ID"

# Poll for completion with timeout
echo "Polling for completion..."
for i in $(seq 1 15); do
  STATUS_RESPONSE=$(curl -sf http://localhost:3000/status/$JOB_ID)
  STATUS=$(echo $STATUS_RESPONSE | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])")
  echo "Poll $i: status=$STATUS"
  if [ "$STATUS" = "completed" ]; then
    echo "SUCCESS: Job completed"
    docker compose down -v
    exit 0
  fi
  sleep 5
done

echo "FAILED: Job did not complete within timeout"
docker compose down -v
exit 1
