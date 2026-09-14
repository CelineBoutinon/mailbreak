#!/bin/bash
cd "$(dirname "$0")"
source yahooarchive_env/bin/activate
streamlit run app.py
