SELECT source_id, job_title, LENGTH(description) as len
FROM jobs 
ORDER BY len DESC
LIMIT 1
