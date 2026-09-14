-- Create tables as heaps for bulk-loading (avoids slow index maintenance and stops mid-load validation errors)
-- Run YahooArchiveDB_PKDef.sql to add primary keys and indexes after bulk-loading is completed with the
-- db_populate.ipynb notebook.

CREATE DATABASE YahooArchiveDB;
GO

USE YahooArchiveDB;
GO

-- 1. Folders Table
CREATE TABLE Folders (
    FolderID INT IDENTITY(1,1),
    FolderName VARCHAR(100) NOT NULL,
    EmailCount INT,
    AttachmentCount INT,
    EmailSize DECIMAL(10,2),
    AttachmentSize DECIMAL(10,2),
    TotalSizeMB DECIMAL(10,2)
    );

-- 2. Emails Table
CREATE TABLE Emails (
    EmailID BIGINT IDENTITY(1,1),
    FolderID INT,
    EmailUID VARCHAR(50) NOT NULL,
    Sender NVARCHAR(500),
    Recipient NVARCHAR(MAX),
    Cc NVARCHAR(MAX),
    Bcc NVARCHAR(MAX),
    EmailDate DATETIME2,
    EmailSubject NVARCHAR(1000),
    HasAttachments BIT,
    AttachmentExtensions VARCHAR(100),
    LocalEmlPath NVARCHAR(500),
    BodySnippet NVARCHAR(MAX)
    );

-- 3. Attachments Table (Heap)
CREATE TABLE Attachments (
    AttachmentID BIGINT IDENTITY(1,1),
    EmailID BIGINT,
    OriginalFileName NVARCHAR(255),
    FileExtension VARCHAR(20),
    LocalAttachmentPath NVARCHAR(500)
);


