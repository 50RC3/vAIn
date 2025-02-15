#!/bin/bash
set -e

# Forward signals to child processes
trap 'kill -TERM $child' SIGTERM

# Start the main application
exec "$@" &
child=$!
wait $child
