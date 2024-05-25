#!/bin/bash

kafka-topics.sh --create --topic wiki-events --bootstrap-server kafka:9092 --replication-factor 1 --partitions 3
