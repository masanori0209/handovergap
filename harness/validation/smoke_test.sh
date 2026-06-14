#!/usr/bin/env bash
set -euo pipefail

handovergap --help
handovergap demo
handovergap detect --scenario S001 --role CS
handovergap evaluate
