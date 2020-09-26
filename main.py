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


# Configure logging
logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")

# Assign email and password
with open('user_info.txt') as user_info:
    email_user = user_info.readline().strip()
    email_pass = user_info.readline().strip()

# Make connection to host
port = 993
mail = imaplib.IMAP4_SSL("imap.gmail.com", port)

# Log in to email account
mail.login(email_user, email_pass)

# Specify mail
mail.select('Inbox')
typ, data = mail.search(None, 'ALL')
# mail_ids = data[0]
# id_list = mail_ids.split()

for num in data[0].split():
    typ, data = mail.fetch(num, '(RFC822)' )
    raw_email = data[0][1]
    # converts byte literal to string removing b''
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)

# Print From, Subject, Body
for response_part in data:
    if isinstance(response_part, tuple):
        msg = email.message_from_string(response_part[1].decode('utf-8'))
        email_subject = msg['subject']
        email_from = msg['from']
        print('From : ' + email_from + '\n')
        print('Subject : ' + email_subject + '\n')
        print(msg.get_payload(decode=True))

