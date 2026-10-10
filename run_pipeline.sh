#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python src/01_prepare_data.py
python src/02_storage_clean_eda.py
python src/03_model_stage2.py
python src/04_chromadb_vector.py
printf '\nDONE. Launch UI: python ui/app.py\n'
