#!/bin/bash
set -euo pipefail

#docker-compose run genGraph < ./Chesapeake.paj.txt | docker-compose run graphViz > output/Chesapeake.svg
docker-compose run genGraph < ./Chesapeake.paj.txt | docker-compose run graphViz > output/Chesapeake.svg
