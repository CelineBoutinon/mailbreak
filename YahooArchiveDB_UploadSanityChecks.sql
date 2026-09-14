USE YahooArchiveDB;
GO

-- Compare the total row counts between your source dataframes and SQL Server to ensure no data was dropped:
SELECT COUNT(*) AS TotalEmails FROM Emails;
SELECT COUNT(*) AS TotalAttachments FROM Attachments;

-- Verify that foreign key relationships (if any exist between attachments and emails) are intact and no orphan records slipped through:
SELECT COUNT(*) AS OrphanedAttachments 
FROM Attachments a
LEFT JOIN Emails e ON a.EmailID = e.EmailID
WHERE e.EmailID IS NULL;

-- Check for unexpected nulls in critical columns (like IDs, timestamps, or subject lines):
SELECT 
    SUM(CASE WHEN EmailID IS NULL THEN 1 ELSE 0 END) AS NullIDs,
    SUM(CASE WHEN EmailDate IS NULL THEN 1 ELSE 0 END) AS MissingDates
FROM Emails;

-- Volume & Date Range Validation:
SELECT 
    MIN(EmailDate) AS EarliestEmail,
    MAX(EmailDate) AS LatestEmail,
    COUNT(DISTINCT CAST(EmailDate AS DATE)) AS UniqueDaysRecorded
FROM Emails;

-- Future emails count:
SELECT COUNT(*) AS FutureEmailsCount 
FROM Emails 
WHERE EmailDate > GETDATE();

-- Storage & Table Size Check:
EXEC sp_spaceused 'Emails';
EXEC sp_spaceused 'Attachments';

-- Check if missing dates belong to specific batches, folders, or email sources
SELECT 
    e.FolderID, 
    COUNT(*) AS MissingCount, 
    f.FolderName
FROM Emails e
JOIN Folders f ON e.FolderID = f.FolderID
WHERE e.EmailDate IS NULL
GROUP BY e.FolderID, f.FolderName;

-- Check for mismatched attachments:
SELECT COUNT(*) AS MismatchedAttachmentsCount
FROM Emails
WHERE HasAttachments = 1 
  AND (AttachmentExtensions IS NULL OR LTRIM(RTRIM(AttachmentExtensions)) = '');

-- Check for missing body snippets:
SELECT COUNT(*) AS EmptyBodySnippetsCount
FROM Emails
WHERE BodySnippet IS NULL OR LTRIM(RTRIM(BodySnippet)) = '';