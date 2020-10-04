#!/usr/bin/env python3

"""
Notes

Read inbox of chosen email account and create .txt from new emails. Use to replace Evernote

@source https://medium.com/@sdoshi579/to-read-emails-and-download-attachments-in-python-6d7d6b60269

log.txt tracks emails in inbox
"""


import imaplib
import base64
import os
import email
import logging
import re


# Configure logging
logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")


def extract_emails(email_user, email_pass, approved_sender_1, approved_sender_2, logged_dates):
    """Extract raw email data for first 20 emails in Inbox. Store in dictionary"""
    # Make connection to host
    port = 993
    mail = imaplib.IMAP4_SSL("imap.gmail.com", port)

    # Log in to email account
    mail.login(email_user, email_pass)

    # Specify mail
    mail.select('Inbox')
    typ, data = mail.search(None, 'ALL')

    # Loop through first 20 emails
    dates = []
    new_dates = []
    date_pattern = r"([\w]{3}, [\d]{1,2} [\w]{3} [\d]{4} [\d]{2}:[\d]{2}:[\d]{2})"
    for num in data[0].split():
        # Break if over 20 emails
        if int(num) > 20:
            break

        # Extract email date for logging
        typ, data = mail.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        # Converts byte literal to string removing b''
        raw_email_string = raw_email.decode('utf-8')
        date_delivered = re.search(date_pattern, raw_email_string)
        dates.append(date_delivered[1])
        email_message = email.message_from_string(raw_email_string)

        # Check log for dates
        if date_delivered[1] in logged_dates:
            continue

        # Compare sender with approved_senders
        unapproved_sender_flag = False
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1].decode('utf-8'))
                email_from = msg['from']
                if email_from == approved_sender_1:
                    logging.info(f"Create .txt from email body, '{date_delivered[1]}'")
                    try:
                        email_body = msg.get_payload(decode=True).decode('utf-8').strip()
                    except (AttributeError, TypeError):
                        email_body = msg.get_payload(decode=True)
                    create_txt(email_body)
                elif email_from == approved_sender_2:
                    logging.info(f"Create .txt from attachment, '{date_delivered[1]}'")
                    for part in email_message.walk():
                        file_name = part.get_filename()
                        if bool(file_name):
                            attachment_text = part.get_payload(decode=True).decode('utf-8').strip()
                            create_txt(attachment_text)
                else:
                    unapproved_sender_flag = True

        # Update log with new email date
        if not unapproved_sender_flag:
            logging.info(f"Update log with '{date_delivered[1]}'")
            new_dates.append(date_delivered[1])

    return new_dates


def create_txt(text: str):
    """Create .txt from string"""
    # Assign name to note
    illegal_char = r"\/:*?\"<>|"
    if len(text) > 20:
        note_name = text.strip()[0:20]
    else:
        note_name = text.strip()
    note_name = remove_char(note_name, illegal_char)

    # Write contents to note
    with open(f"Inbox/{note_name}.txt", 'w') as note:
        note.write(text)


def remove_char(value, delete_chars):
    """Remove delete_chars from value"""
    for ch in delete_chars:
        value = value.replace(ch, '')
    return value


if __name__ == "__main__":
    # Assign email and password
    with open('user_info.txt') as user_info:
        email_user = user_info.readline().strip()
        email_pass = user_info.readline().strip()
        approved_sender_1 = user_info.readline().strip()
        approved_sender_2 = user_info.readline().strip()

    # Extract log
    with open('log.txt', 'r') as log:
        logged_dates = log.readlines()
        logged_dates = [line.strip() for line in logged_dates]

    # Extract dates from emails
    new_dates = extract_emails(email_user, email_pass, approved_sender_1, approved_sender_2, logged_dates)

    # Update log
    # TODO: If Log longer than 100 lines, clear older logs
    with open('log.txt', 'a') as log:
        while new_dates:
            log.write(new_dates.pop() + '\n')



