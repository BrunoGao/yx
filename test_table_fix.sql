-- Test script to verify the table existence check fix
-- This would be run against the database to test the fix

-- Check if the problematic table exists
SELECT COUNT(*) as table_exists 
FROM information_schema.tables 
WHERE table_schema = DATABASE() 
AND table_name = 't_user_health_data_202508';

-- Show existing monthly tables
SELECT table_name, table_comment, create_time
FROM information_schema.tables 
WHERE table_schema = DATABASE() 
AND table_name LIKE 't_user_health_data_%'
ORDER BY table_name;

-- The fixed code should now skip non-existent monthly tables
-- and only use the main table t_user_health_data for baseline generation