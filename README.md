<div align="center">
  <img src="byehoo_logo.jpg" alt="Mailbreak Logo" width="400"/>
</div>

# Mailbreak - A Yahoo Archive Backup & Retrieval solution

A local-first, high-performance desktop application designed to archive, structure, and explore legacy Yahoo Mail data with zero recurring email storage costs and secure cost-efficient offsite cold storage backup.

## Rationale & Project Vision
After dropping its email storage limit from "unlimited" to 1TB in 2013, Yahoo announced at the end of 2025 that it would be further dropping the limit to 15GB for UK and EU customers from May 2026 onwards, blocking accounts over that limit, with no options offered to users other than delete emails and attachments or pay for additional storage (as Yahoo has a 12-month rule on dormant accounts). This move caught many legacy users off-guard after decades of rather generous storage allowances, and sent many scrambling to downsize personal or professional mailboxes with histories starting in the early 2000s (or even before) which amounted to dozens of GBs and 10s of thousands of emails for many, in a (sometimes desperate) attempt at recovering inbox & outbox functionalities (whilst very often moving to a new account elsewhere). **Mailbreak** was built against this background to reclaim complete ownership of a Yahoo email history through a secure, hybrid archiving model. By shifting historical mail off Yahoo's proprietary platforms onto local infrastructure (i.e. your - hopefully trustworthy - desktop or laptop hard drive), backed by optional cost-effective cold storage (S3 Glacier),  guaranteeing privacy, instant offline query performance, thus liberating your email archive from corporate hostage-taking.

## Lean & Cost-Saving Architecture
Designed from the ground up to be lightweight, resource-efficient, and budget-friendly:
* **Zero SaaS Fees**: Eliminates commercial email archiving subscriptions by leveraging existing local hardware and Microsoft SQL Server Express.
* **Low Memory Footprint**: Utilizes chunked data streaming via Pandas to process tens of thousands of `.eml` files without memory bloat.
* **Cloud-Optimized Cold Backup**: Integrates Amazon S3 and Glacier tiers for automated, highly secure offsite disaster recovery at a fraction of a cent per gigabyte.
* **Native Ecosystem Leverage**: Avoids building a heavy custom rich-text rendering engine by delegating deep email inspection directly to Microsoft Outlook via native OS file handling (`os.startfile`).

## Technology Stack
* **Parsing Engine**: Python (`email`, `policy`, `tqdm`) for robust MIME header decoding, HTML entity unescaping, and plain-text snippet generation.
* **Database Layer**: Microsoft SQL Server managed through SQLAlchemy and Pandas, featuring normalized relational schemas with indexed foreign keys for sub-second search capabilities.
* **Storage & Backup**: Local filesystem paired with automated AWS S3 and Glacier lifecycle policies for durable long-term archiving.
* **User Interface**: Streamlit for a clean, reactive, browser-based dashboard with responsive data grids and filter controls.
* **Local Deployment**: Windows batch scripting paired with a custom desktop shortcut for frictionless, one-click execution.

## Key Development Phases
1. **Parsing & Ingestion**: Developed modular helper functions (`utils.py`) to extract clean text bodies, handle multi-part MIME structures, and normalize complex or anomalous timestamps.
2. **Database Optimization**: Structured relational schemas across `Folders`, `Emails`, and `Attachments` tables, implementing `VARCHAR(MAX)` limits and cascading foreign key constraints to prevent truncation errors.
3. **UI & State Management**: Built an interactive Streamlit dashboard featuring multi-parameter text filtering, session-state-driven filter clearing, and checkbox-enabled bulk email management.
4. **Desktop Integration & Backup Automation**: Packaged the application into a local Windows environment with an automated execution script, custom shortcut mapping, and S3/Glacier backup sync scripts for robust disaster recovery.

# Implementation Steps
1. **Generating a Yahoo App Password**
Because Yahoo blocks standard third-party sign-ins for security reasons, you must generate a dedicated App Password to allow local scripts to securely connect to your account via IMAP.

* **Sign in to Yahoo Account Security**: Go to your [Yahoo Account Security page](https://login.yahoo.com/account/security) and log in with your credentials.

* **Navigate to App Passwords**: Scroll down and look for the section labeled **App passwords** or **Generate app password**.

* **Create a Custom App**: Click **Generate app password** (or **Get started**), select **Other App** from the dropdown menu, and give it a recognizable name (e.g., `YahooArchiveExplorer`).

* **Copy the Password**: Yahoo will display a 16-character generated password. Copy this code add it to your local .env configuration file. *(Note: Do not include spaces when entering the password into your script).*

2. **Generating an AWS Access Key**
Optional - skip these steps if using local storage only:
* **Access the AWS Management Console:** Log in to your AWS account and navigate to the IAM (Identity and Access Management) dashboard.

* **Select or Create an IAM User:** Choose an existing IAM user (or create a new one) configured with programmatic access and appropriate permissions to manage your backup buckets in Amazon S3 and Glacier.

* **Generate an Access Key:** Go to the Security credentials tab for that user, scroll down to the Access keys section, and click Create access key. Select Command Line Interface (CLI) or Other as the use case.

* **Save Your Credentials:** Securely copy both the Access Key ID and Secret Access Key. Add them to your local .env configuration file to enable automated cloud cold backups. 

3. **Creating an S3 bucket & lifecycle configuration**
Optional - skip these steps if using local storage only:
* **Access the Amazon S3 Console:** Log in to the AWS Management Console and navigate to the S3 dashboard.

* **Create a New Bucket:** Click Create bucket, enter a globally unique bucket name, select your preferred region, and ensure Block all public access remains enabled to keep your personal email archives strictly private.

* **Configure Lifecycle Rules:** Open your newly created bucket, navigate to the Management tab, and click Create lifecycle rule. Give the rule a descriptive name (e.g., ArchiveToGlacier).

* **Define Transition Actions:** Set the rule scope to apply to all objects in the bucket, and add a transition action to move your files to Amazon S3 Glacier Flexible Archive or Glacier Deep Archive after a specified period (e.g., 0 to 30 days) to minimize long-term cloud storage costs. 

4. **Analyse your archive size**
Run notebooks/EDA.ipynb first in order to map folders by number of emails, attachments and size. If your goal is to archive & backup only the heaviest folders in your Yahoo account in order to regain access to your mailbox, this will help prioritize the biggest folders. This notebook generates a .csv file with all folders by decreasing size order as well as a list of folders. 

5. **Run the extractor**
Once you have decided which folders to prioritise (if any), run notebooks/extractor.ipynb to create your local email archive and optional remote archive in S3. This notebook also includes basic sanity checks to ensure backup completeness before you decide to delete anything.

6. **Generate the metadata**
Run notebooks/metadata.ipynb to generate metadata from the emails collected from Yahoo (folder,	uid, sender, recipient, cc,	bcc, date, subject, has_attachments, attachment_names, attachment_extensions, eml_path and body_snippet).

**Prerequisites: Microsoft SQL Server**
Mailbreak relies on a local SQL database to deliver sub-second search performance. If you do not already have it installed, download and install the free [Microsoft SQL Server Express](https://www.microsoft.com/en-us/sql-server/sql-server-downloads) and [SQL Server Management Studio (SSMS)](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms) before proceeding to Step 7.

7. **Build & populate your local database**
Run in order:
* **YahooArchiveDB_DDL.sql** to create the database and tables
* **notebooks/db_populate.ipynb** to populate the database tables with the metadata generated at step 6
* **YahooArchiveDB_PKDef.sql** to add primary keys, foreign keys and clustered indexes
* **YahooArchiveDB_UploadSanityChecks.sql** to check the database creation & data insertion went ok

8. **🎉 Run the app**
Add a desktop shortcut to wherever you saved run_yahoo_archive.bat, double-click & browse your newly created local email archive by topic, date, sender & more!
