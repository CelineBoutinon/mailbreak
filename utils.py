from email.header import decode_header
import html
import re

def decode_str(s):
  """Safely decodes an email header string containing potentially MIME-encoded words.

  Parameters:
  ----------
  s : str or bytes or None
      The raw email header string (e.g., Subject, From, To) which may contain
      MIME-encoded components (e.g., '=?utf-8?Q?...?=') or standard plain text.

  Returns:
  -------
  str
      The fully decoded, human-readable Unicode string. Returns an empty string
      if the input is empty, None, or falsy.

  Notes:
  -----
  - Iterates through parts returned by email.header.decode_header().
  - Handles bytes by attempting to decode using the specified header encoding.
  - Falls back to 'utf-8' with error-ignoring if the primary encoding fails or is missing.
  - Safely converts regular strings to ensure clean concatenation.
  """
  if not s:
    return ""
  decoded_parts = decode_header(s)
  result = []
  for text, encoding in decoded_parts:
    if isinstance(text, bytes):
      if encoding:
        try:
          result.append(text.decode(encoding))
        except:
          result.append(text.decode("utf-8", errors="ignore"))
      else:
        result.append(text.decode("utf-8", errors="ignore"))
    else:
      result.append(str(text))
  return "".join(result)


def clean_snippet(text, max_len=500):
  """Safely cleans and formats raw email body text into a readable plain-text snippet.

  Parameters:
  ----------
  text : str or None
      The raw email body text extracted from the message payload.
  max_len : int, optional
      The maximum character length of the returned snippet (default is 500).

  Returns:
  -------
  str
      A cleaned, flattened, and truncated plain-text string. Returns an empty 
      string if the input is empty or None.

  Notes:
  -----
  - Unescapes HTML entities and removes invisible zero-width characters (e.g., &zwnj;).
  - Strips common Markdown formatting symbols (*, _, #, ~) and extracts the display 
    text from Markdown-formatted links.
  - Collapses all line breaks, carriage returns, and excessive whitespace into 
    single spaces for clean UI rendering.
  """
  if not text:
    return ""

  # 1. Unescape HTML entities (e.g., converts &zwnj;, &nbsp;, &amp; to actual characters/spaces)
  text = html.unescape(text)

  # 2. Specifically remove zero-width non-joiners and other invisible spacing characters
  text = text.replace("\u200c", "").replace("\u200b", "").replace("\u00a0", " ")

  # 3. Remove markdown bold/italic markers (*, _, #, ~)
  text = re.sub(r"[\#\*\_\~`]", "", text)

  # 4. Clean up markdown links [Text](URL) -> keep just the [Text]
  text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)

  # 5. Replace multiple newlines and carriage returns with a single space
  text = re.sub(r"[\r\n]+", " ", text)

  # 6. Collapse multiple spaces into a single space and strip edges
  text = re.sub(r"\s+", " ", text).strip()

  # 7. Return truncated snippet to desired length
  return text[:max_len]


def extract_body(msg):
  """Extracts the plain text body from an email message structure.

  Parameters:
  ----------
  msg : email.message.EmailMessage
      The parsed email message object (typically created via
      email.message_from_bytes() with a specific policy).

  Returns:
  -------
  str
      The extracted plain text body of the email. Returns an empty string
      if no plain text section is found or if decoding fails.

  Notes:
  -----
  - Handles multipart emails by walking through message parts, looking for a
    'text/plain' content type that is not marked as an attachment.
  - Handles single-part (non-multipart) emails directly if their content type is
    'text/plain'.
  - Uses UTF-8 decoding with error ignoring to gracefully handle malformed
    or mismatched character sets.
  """
    
  body = ""
  if msg.is_multipart():
    for part in msg.walk():
      content_type = part.get_content_type()
      content_disposition = str(part.get("Content-Disposition"))
      if content_type == "text/plain" and "attachment" not in content_disposition:
        try:
          body = part.get_payload(decode=True).decode(
              "utf-8", errors="ignore"
          )
          break
        except:
          pass
  else:
    if msg.get_content_type() == "text/plain":
      try:
        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
      except:
        pass
  return body.strip()