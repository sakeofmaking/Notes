#!/usr/bin/env python3

"""
Notes

Read inbox of chosen email and create .txt from new emails

@source https://medium.com/@sdoshi579/to-read-emails-and-download-attachments-in-python-6d7d6b60269

log.txt tracks emails in inbox
"""


import imaplib
import base64
import os
import email
import logging


# TODO: Decode message and create note
# TODO: extract attachment for long messages


# Configure logging
logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")

# Assign email and password
with open('user_info.txt') as user_info:
    email_user = user_info.readline().strip()
    email_pass = user_info.readline().strip()
    approved_sender = user_info.readline().strip()

# Make connection to host
port = 993
mail = imaplib.IMAP4_SSL("imap.gmail.com", port)

# Log in to email account
mail.login(email_user, email_pass)

# Specify mail
mail.select('Inbox')
typ, data = mail.search(None, 'ALL')

# Loop through emails
inbox = {}
for num in data[0].split():
    typ, data = mail.fetch(num, '(RFC822)')
    raw_email = data[0][1]
    # converts byte literal to string removing b''
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)

    # From, Subject, Body
    for response_part in data:
        if isinstance(response_part, tuple):
            msg = email.message_from_string(response_part[1].decode('utf-8'))
            email_subject = msg['subject']
            email_from = msg['from']
            try:
                e_message = msg.get_payload(decode=True).decode('utf-8').strip()
            except (AttributeError, TypeError):
                e_message = msg.get_payload(decode=True)

            if email_from == approved_sender:
                inbox[email_subject] = e_message


# Update log if email not logged
with open('log.txt', 'r+') as log:
    # Check if email already logged
    lines = log.readlines()
    lines_filtered = [line.strip() for line in lines]
    # TODO: If Log longer than 100 lines, clear oldest log

    for subject, message in inbox.items():
        if subject not in lines_filtered:
            logging.info(f"Logging: {subject}")
            log.write(subject)

print(lines_filtered)
