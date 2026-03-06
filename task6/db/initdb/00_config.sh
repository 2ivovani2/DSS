#!/usr/bin/env bash
set -e
echo "listen_addresses = '*'" >> "$PGDATA/postgresql.conf"
echo "password_encryption = 'scram-sha-256'" >> "$PGDATA/postgresql.conf"

