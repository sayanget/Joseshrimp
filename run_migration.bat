@echo off
set DATABASE_URL=postgresql://postgres.wvhhswzelfpvllzqotxy:QvbU5t0d8sB4rW7P@aws-0-us-west-2.pooler.supabase.com:6543/postgres
python fix_production_schema.py > migration_output.txt 2>&1
type migration_output.txt
