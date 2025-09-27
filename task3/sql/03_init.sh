#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -c "ALTER DATABASE \"$POSTGRES_DB\" SET search_path TO csgo, public;" \
  -c "ALTER ROLE app_user IN DATABASE \"$POSTGRES_DB\" SET search_path TO csgo, public;"
