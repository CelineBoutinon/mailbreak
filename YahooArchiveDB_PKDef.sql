-- Apply primary keys and constraints

-- 1. Add Primary Keys
ALTER TABLE Folders ADD CONSTRAINT PK_Folders PRIMARY KEY CLUSTERED (FolderID);
ALTER TABLE Folders ADD CONSTRAINT UQ_FolderName UNIQUE (FolderName);

ALTER TABLE Emails ADD CONSTRAINT PK_Emails PRIMARY KEY CLUSTERED (EmailID);
ALTER TABLE Attachments ADD CONSTRAINT PK_Attachments PRIMARY KEY CLUSTERED (AttachmentID);

-- 2. Add Foreign Keys
ALTER TABLE Emails 
ADD CONSTRAINT FK_Emails_Folders 
FOREIGN KEY (FolderID) REFERENCES Folders(FolderID);

ALTER TABLE Attachments 
ADD CONSTRAINT FK_Attachments_Emails 
FOREIGN KEY (EmailID) REFERENCES Emails(EmailID) ON DELETE CASCADE;

-- 3. Add Performance Indexes
CREATE NONCLUSTERED INDEX IX_Emails_FolderID ON Emails(FolderID);
CREATE NONCLUSTERED INDEX IX_Emails_EmailDate ON Emails(EmailDate);
CREATE NONCLUSTERED INDEX IX_Attachments_EmailID ON Attachments(EmailID);
GO