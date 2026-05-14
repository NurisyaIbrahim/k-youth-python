SELECT 
    (SELECT COUNT(*) FROM jobs WHERE job_title IS NULL OR job_title = '') as null_job_title,
    (SELECT COUNT(*) FROM jobs WHERE company IS NULL OR company = '') as null_company,
    (SELECT COUNT(*) FROM jobs WHERE description IS NULL OR description = '') as null_description
