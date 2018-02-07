#!python3

import configparser
import email
import smtplib
from email.mime.multipart import MIMEMultipart

class Email:

    def __init__(self, path):
        if path is None:
            path = 'mw.ini'

        config = configparser.ConfigParser()
        config_data = config.read(path)
        if len(config_data) == 0:
            raise ValueError("Failed to open mw.ini configuration file.")

        self.mx = config.get('mail', 'MX')
        self.send_from = config.get('mail', 'SEND_FROM')
        assert isinstance(self.mx, str)
        assert isinstance(self.send_from, str)

    def send_mail(self, send_to, subject, text, attachment=None, attachment_name="document.pdf"):
        """
        Send an email, optionally with an attachment. ALthough strictly not part of Moneyworks, this is a useful utility
        method to have here because you very often need to send reports by email
        :param send_to: an array of email addresses to send to, or just a single string for one address
        :param subject: the subject of the email
        :param text: the body of the email. Currently only plain text body is supported.
        :param attachment: an optional bytearray which is the PDF file you want to send
        :param attachment_name: if you pass an attachment, then give it a name
        """
        assert isinstance(subject, str)

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.send_from
        msg["To"] = email.utils.COMMASPACE.join(send_to) if isinstance(send_to, list) else send_to

        msg.attach(email.mime.text.MIMEText(text))

        if attachment:
            assert isinstance(attachment, bytes)
            a = email.mime.application.MIMEApplication(attachment, 'pdf')
            a.add_header('Content-Disposition', 'attachment; filename=\"{0}\"'.format(attachment_name))
            msg.attach(a)

        smtp = smtplib.SMTP(self.mx)
        smtp.sendmail(self.send_from, send_to, msg.as_string())
        smtp.quit()
