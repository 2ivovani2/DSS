#!/usr/bin/env bash
set -e
cat > "$PGDATA/pg_hba.conf" <<'EOF'
local   all             all                                     scram-sha-256
host    all             all             0.0.0.0/0               scram-sha-256
host    all             all             ::0/0                   scram-sha-256
EOF

