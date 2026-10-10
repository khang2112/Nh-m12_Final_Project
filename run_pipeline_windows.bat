@echo off
cd /d "%~dp0"
python src\01_prepare_data.py || goto error
python src\02_storage_clean_eda.py || goto error
python src\03_model_stage2.py || goto error
python src\04_chromadb_vector.py || goto error
python tests\test_pipeline.py || goto error
start http://127.0.0.1:7860
python ui\app.py
exit /b 0
:error
 echo Pipeline failed. Check the error above and README.md.
 exit /b 1
