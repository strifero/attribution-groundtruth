#!/bin/bash
# Wait for the Hub download (pid $1), then fetch stack-edu text with 4 processes.
cd /home/sean/tda
export PATH=/home/sean/elroy/.venv/bin:$PATH PYTHONPATH=/home/sean/elroy
log() { echo "$(date '+%F %T') $*"; }
while kill -0 "$1" 2>/dev/null; do sleep 20; done
log "hub downloads done"; du -sh data/raw/*
for i in 0 1 2 3; do
  python /home/sean/elroy/scripts/fetch_stack_edu.py --target-bytes 9e9 --workers 32 --process-index $i --process-count 4 > logs/fetch_stack_edu_$i.log 2>&1 &
done
wait
log "stack-edu text done"; du -sh data/raw/*
echo DL DONE
