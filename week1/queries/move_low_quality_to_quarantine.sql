-- Insert low quality records into quarantine
INSERT OR IGNORE INTO jobs_quarantine 
SELECT * FROM jobs WHERE quality = 'LOW';

-- Delete low quality records from main table
DELETE FROM jobs WHERE quality = 'LOW'
