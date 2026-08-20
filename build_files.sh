#!/bin/bash
echo "Building Vercel deployment..."
python3 -m pip install -r requirements.txt
python3 manage.py collectstatic --noinput --clear
echo "Vercel build completed successfully."
