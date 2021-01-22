#!/bin/bash
set -euo pipefail

trap "docker-compose --project-name genGraph down --volumes --remove-orphans" 0
trap "docker-compose --project-name graphViz down --volumes --remove-orphans" 0

docker-compose --project-name genGraph run genGraph < ./Chesapeake.paj.txt | docker-compose --project-name graphViz run graphViz > output/Chesapeake.svg
