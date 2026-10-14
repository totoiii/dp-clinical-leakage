#!/usr/bin/env bash
# Block until the queue logs a failure, N more completions, empties, or dies.
# usage: scripts/watch_queue.sh [N=10]
cd "$(dirname "$0")/../runs"
N=${1:-10}
n0=$(grep -c " END " queue.out); f0=$(grep -c " FAIL " queue.out)
while true; do
  n=$(grep -c " END " queue.out); f=$(grep -c " FAIL " queue.out)
  if [ "$f" -gt "$f0" ]; then echo "REASON: failure"; break; fi
  if [ "$n" -ge $((n0 + N)) ]; then echo "REASON: $N completions"; break; fi
  if grep -q "queue empty" queue.out; then echo "REASON: queue empty"; break; fi
  if ! pgrep -f "queue.py --gpus" >/dev/null; then echo "REASON: queue process died"; break; fi
  sleep 120
done
date; tail -12 queue.out
