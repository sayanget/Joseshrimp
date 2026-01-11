@echo off
echo ==========================================
echo Fixing Sales with total_kg = 0
echo ==========================================
echo.

set DATABASE_URL=postgresql://postgres.wvhhswzelfpvllzqotxy:QvbU5t0d8sB4rW7P@aws-0-us-west-2.pooler.supabase.com:6543/postgres

echo Running fix on PRODUCTION database...
python fix_zero_total_kg.py

echo.
echo Done!
pause
