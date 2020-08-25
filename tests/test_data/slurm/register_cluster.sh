#!/bin/bash
set -e

docker exec slurmctld /usr/bin/sacctmgr --immediate add cluster name=linux
docker-compose restart slurmdbd slurmctld
docker exec slurmctld /usr/bin/sacctmgr --immediate add account test Cluster=linux Description=test Organization=test
