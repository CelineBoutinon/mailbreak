@echo off
cd /d "%~dp0"
call yahooarchive_env\Scripts\activate
streamlit run app.py
pause