@echo off
echo ==========================================
echo Updating total_kg for Production Database
echo ==========================================
echo.

REM Set the DATABASE_URL environment variable for production
set DATABASE_URL=postgresql://postgres.wvhhswzelfpvllzqotxy:QvbU5t0d8sB4rW7P@aws-0-us-west-2.pooler.supabase.com:6543/postgres

echo Running update script on PRODUCTION database...
python update_total_kg.py > update_total_kg_output.txt 2>&1

echo.
echo Update complete! Check update_total_kg_output.txt for details.
echo.
pause
