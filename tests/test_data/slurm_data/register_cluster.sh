#!/bin/bash
set -e

docker exec slurmctld /usr/bin/sacctmgr --immediate add cluster name=test
docker-compose restart slurmdbd slurmctld
docker exec slurmctld /usr/bin/sacctmgr --immediate add account test Cluster=test Description=test Organization=test
