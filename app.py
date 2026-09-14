import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
import os
import platform
import subprocess
import dotenv

# Page configuration
st.set_page_config(
    page_title="Yahoo Archive Explorer", page_icon="📧", layout="wide"
)


# Database connection configuration
@st.cache_resource
def get_connection():
  dotenv.load_dotenv()
  conn_str = os.getenv("CONN_STR")
  return create_engine(conn_str)


try:
  engine = get_connection()
except Exception as e:
  st.error(f"Database connection failed: {e}")
  st.stop()


# Initialize session state defaults for clearing filters cleanly
if "clear_triggered" not in st.session_state:
  st.session_state.clear_triggered = False


def clear_filters():
  st.session_state.selected_folder = "All Folders"
  st.session_state.subject_query = ""
  st.session_state.sender_query = ""
  st.session_state.recipient_query = ""
  st.session_state.date_query = ""
  st.session_state.snippet_query = ""
  st.session_state.body_query = ""


# App Header
st.image("byehoo_logo.jpg", width=150)
st.title(" Yahoo eMail Archive Explorer")
st.markdown("Explore imported emails, folders & attachments.")

# Sidebar Filters
st.sidebar.header("Filter Options")

# Clear Filters Button
st.sidebar.button("🗑️ Clear All Filters", on_click=clear_filters)
st.sidebar.divider()

# Fetch folders for dropdown
folders_df = pd.read_sql(
    "SELECT FolderID, FolderName FROM Folders ORDER BY FolderName", engine
)
folder_options = ["All Folders"] + list(folders_df["FolderName"])

selected_folder = st.sidebar.selectbox(
    "Select Folder",
    options=folder_options,
    key="selected_folder",
)

subject_query = st.sidebar.text_input(
    "Search Subject", placeholder="e.g. invoice...", key="subject_query"
)
sender_query = st.sidebar.text_input(
    "Search Sender",
    placeholder="e.g. jane.doe@fawnmail.com",
    key="sender_query",
)
recipient_query = st.sidebar.text_input(
    "Search Recipient",
    placeholder="e.g. john.smith@fawnmail.com",
    key="recipient_query",
)
date_query = st.sidebar.text_input(
    "Search Date",
    placeholder="e.g. 2021, 06/2021, or 2021-06-15",
    key="date_query",
)
snippet_query = st.sidebar.text_input(
    "Search Snippet", placeholder="e.g. meeting...", key="snippet_query"
)
body_query = st.sidebar.text_input(
    "Search Body", placeholder="e.g. meeting notes...", key="body_query"
)

# Main Query Construction
query = """SELECT e.EmailID, f.FolderName, e.EmailUID, e.Sender, e.Recipient, e.EmailDate, e.EmailSubject, e.HasAttachments,
e.BodySnippet, e.LocalEmlPath
    FROM Emails e
    JOIN Folders f ON e.FolderID = f.FolderID
    WHERE 1=1"""

params = {}

if selected_folder != "All Folders":
  query += " AND f.FolderName = :folder_name"
  params["folder_name"] = selected_folder

if subject_query:
  query += " AND (e.EmailSubject LIKE :subject OR e.Sender LIKE :subject OR e.Recipient LIKE :subject OR e.Cc LIKE :subject OR e.Bcc LIKE :subject OR e.BodySnippet LIKE :subject)"
  params["subject"] = f"%{subject_query}%"

if sender_query:
  query += " AND e.Sender LIKE :sender"
  params["sender"] = f"%{sender_query}%"

if recipient_query:
  query += " AND e.Recipient LIKE :recipient"
  params["recipient"] = f"%{recipient_query}%"

if date_query:
  query += " AND CAST(e.EmailDate AS VARCHAR) LIKE :date_val"
  params["date_val"] = f"%{date_query}%"

if snippet_query:
  query += " AND e.BodySnippet LIKE :snippet"
  params["snippet"] = f"%{snippet_query}%"

if body_query:
  query += " AND e.BodySnippet LIKE :body"
  params["body"] = f"%{body_query}%"

query += " ORDER BY e.EmailDate DESC OFFSET 0 ROWS FETCH NEXT 100 ROWS ONLY;"

# Load Data safely using text() and conditional params
with engine.connect() as connection:
  if params:
    df_emails = pd.read_sql(text(query), connection, params=params)
  else:
    df_emails = pd.read_sql(text(query), connection)

# Display Metrics
col1, col2 = st.columns(2)
with col1:
  st.metric(
      label="Emails Matching Filters (Showing Top 100)",
      value=len(df_emails),
  )
with col2:
  total_db_emails = pd.read_sql("SELECT COUNT(*) FROM Emails", engine).iloc[
      0, 0
  ]
  st.metric(label="📧 Total Database Emails", value=total_db_emails)

st.divider()

# Display Table with Checkboxes
if not df_emails.empty:
  # Add a selection boolean column for the data editor
  display_df = df_emails[[
      "FolderName",
      "EmailDate",
      "Sender",
      "EmailSubject",
      "HasAttachments",
      "BodySnippet",
      "LocalEmlPath",
  ]].copy()
  display_df.insert(0, "Select", False)

  # Render interactive table with checkboxes
  edited_df = st.data_editor(
      display_df,
      column_config={
          "Select": st.column_config.CheckboxColumn(
              "Select", required=True
          ),
          "LocalEmlPath": None,  # Hide the raw path column from the main view
      },
      use_container_width=True,
      hide_index=True,
  )

  # Button to open ticked emails in default mail client
  if st.button("📥 Open Ticked Emails in Default Mail App"):
    # Filter rows where 'Select' is True
    selected_rows = edited_df[edited_df["Select"] == True]

    if not selected_rows.empty:
      opened_count = 0
      system_name = platform.system()
      
      for _, row in selected_rows.iterrows():
        eml_path = row["LocalEmlPath"]
        abs_path = os.path.abspath(eml_path)
        
        try:
          if system_name == "Windows":
              os.startfile(abs_path) 
          elif system_name == "Darwin":  
              subprocess.run(["open", abs_path], check=True)
          else: 
              subprocess.run(["xdg-open", abs_path], check=True)
          opened_count += 1
        except Exception as e:
          st.error(f"Could not open {eml_path}: {e}")
          
      st.success(f"Successfully opened {opened_count} email(s)!")
    else:
      st.warning("Please tick at least one email checkbox first.")

  st.divider()

  # Email Inspector expansion (retains single selection below)
  selected_id = st.selectbox(
      "Select an Email ID to view details", options=df_emails["EmailID"]
  )
  if selected_id:
    selected_row = df_emails[df_emails["EmailID"] == selected_id].iloc[0]
    st.subheader(f"Subject: {selected_row['EmailSubject']}")
    st.write(
        f"**From:** {selected_row['Sender']} | **Date:**"
        f" {selected_row['EmailDate']}"
    )
    # Normalized clean path display
    normalized_path = os.path.normpath(selected_row["LocalEmlPath"])
    st.write(f"**Path:** `{normalized_path}`")
    st.info(selected_row["BodySnippet"])

    # Fetch attachments for this email
    attachments_df = pd.read_sql(
        "SELECT OriginalFileName, FileExtension FROM Attachments WHERE EmailID ="
        f" {selected_id}",
        engine,
    )
    if not attachments_df.empty:
      st.write("**Attachments:**")
      st.dataframe(attachments_df, use_container_width=True)
    else:
      st.write("*No attachments for this email.*")
else:
  st.warning("No emails found matching your filters.")