#!/bin/bash
# stack-edu text: process 0 builds the ranked index alone, then processes 1-3 join.
cd /home/sean/tda
export PATH=/home/sean/elroy/.venv/bin:$PATH PYTHONPATH=/home/sean/elroy
log() { echo "$(date '+%F %T') $*"; }
rm -f data/raw/stack-edu-text/*.tmp
python /home/sean/elroy/scripts/fetch_stack_edu.py --target-bytes 9e9 --workers 32 --process-index 0 --process-count 4 > logs/fetch_stack_edu_0.log 2>&1 &
P0=$!
while ! grep -q "resuming" logs/fetch_stack_edu_0.log 2>/dev/null; do kill -0 $P0 2>/dev/null || { log "proc 0 died"; exit 1; }; sleep 10; done
log "index built, starting 1-3"
for i in 1 2 3; do
  python /home/sean/elroy/scripts/fetch_stack_edu.py --target-bytes 9e9 --workers 32 --process-index $i --process-count 4 > logs/fetch_stack_edu_$i.log 2>&1 &
done
wait
log "stack-edu text done"; du -sh data/raw/*
echo DL DONE
