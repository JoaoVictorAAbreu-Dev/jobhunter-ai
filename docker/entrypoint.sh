#!/bin/sh
set -eu
cd /app
if [ "${RUN_COLLECTION:-0}" = "1" ]; then
  echo "Buscando vagas..."
  python3 job_hunter.py buscar || echo "Aviso: coleta falhou; painel continuará disponível."
fi
python3 scripts/build_site.py
exec php -S 0.0.0.0:8080 -t /app/site /app/docker/router.php
