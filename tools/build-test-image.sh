#!/bin/bash

BASEDIR=$(dirname "$0")
docker build -t fcpindi/c-pac:docker-test $BASEDIR/../tests/test_data