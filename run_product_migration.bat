@echo off
echo ==========================================
echo Running Product Table Migration
echo ==========================================
echo.

REM Set the DATABASE_URL environment variable
set DATABASE_URL=postgresql://postgres.wvhhswzelfpvllzqotxy:QvbU5t0d8sB4rW7P@aws-0-us-west-2.pooler.supabase.com:6543/postgres

echo Running migration script...
python migrate_add_product_table.py > product_migration_output.txt 2>&1

echo.
echo Migration complete! Check product_migration_output.txt for details.
echo.
pause
