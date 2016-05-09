#!/usr/local/bin/python2.7
from datetime import date
from requests.auth import HTTPBasicAuth
import requests
import urllib
import logging

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE
import smtplib

from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

import ConfigParser
config = ConfigParser.ConfigParser()
config.read("mw.ini")

logging.basicConfig(format='%(message)s', level=logging.WARNING)


class Moneyworks:

    def __init__(self):
        self.base_url = "http://" + config.get('mw_server', 'HOST') + ":" + config.get('mw_server', 'PORT') + "/REST/"
        self.url = self.base_url + urllib.quote_plus(config.get('mw_server', 'DATA_FILE')) + "/"
        self.mw_auth = HTTPBasicAuth(config.get('mw_server', 'USERNAME'), config.get('mw_server', 'PASSWORD'))

    def __get(self, path):
        r = requests.get(self.url + path, auth=self.mw_auth)
        r.raise_for_status()
        return r

    def __post(self, path, data):
        r = requests.post(self.url + path, data=data, auth=self.mw_auth)
        r.raise_for_status()
        return r

    def version(self):
        """
        :return the version of the Moneyworks Server
        """
        r = requests.get(self.base_url + "/version", auth=self.mw_auth)
        r.raise_for_status()
        return r.text

    def get_forms(self):
        """
        Get a list of all the forms in the system.
        """
        return self.__get("list/folder=forms").text

    def create_transaction(self, xml):
        """
        Create an invoice, purchase order or other transaction
        :param xml: the XML data fragment for this transaction
        :return sequence number of the record created
        """
        logging.info(xml)
        seqnum = self.__post("import/return_seq=true", xml).text
        logging.warn("Transaction created with id " + seqnum)
        return seqnum

    def get_email(self, company_code):
        """
        Get the email address from Moneyworks for a particular company
        :return email address string
        """
        return self.__get("export/table=name&search=" + urllib.quote_plus("code=`" + company_code + "`") + "&format=[email]").text

    def print_transaction(self, search, form):
        """
        Print the transaction
        :param search: a search string to select the correct record eg. "sequencenumber=`123`"
        :param form: the form to use when printing this record
        :return the pdf file as bytes
        """
        r = self.__get("doform/form=" + form + "&search=" + urllib.quote_plus(search))
        logging.debug(r.headers)
        return r.content

    def post_transaction(self, seqnum):
        """
        Post the transaction in Moneyworks
        :param seqnum the invoice's sequence number (this is not the same as the invoice/PO number)
        """
        logging.warn("Posting transaction " + seqnum)
        return self.__post("post/seqnum=" + seqnum, "").text

    def export(self, table, search):
        """
        Extract data from Moneyworks
        :param table: The table from which we want to get data eg. "name"
        :param search: A search string, eg. "DBalance>0"
        :return A list of records, each as a dict of record attributes
        """
        path = "export/table=" + table + "&search=" + urllib.quote_plus(search) + "&format=xml-verbose"
        xml = self.__get(path).text
        logging.debug("XML retrieved " + xml)

        result = []
        for record in fromstring(xml).findall(table):
            r = dict()
            result.append(r)
            for e in record:
                r[e.tag] = e.text

        return result

    def export_with_format(self, table, search, format_string, sort=None):
        """
        Extract data from Moneyworks
        :param table: The table from which we want to get data eg. "name"
        :param search: A search string, eg. "DBalance>0"
        :param format_string: a format for the returned data eg. "[code] [email] [DBalance]," or "xml"
        :param sort: an optional sort expression
        """
        path = "export/table=" + table + "&search=" + urllib.quote_plus(search)
        if format_string:
            path = path + "&format=" + urllib.quote_plus(format_string)

        if sort:
            path = path + "&sort=" + urllib.quote_plus(sort)

        return self.__get(path).text


class Transaction:

    def __init__(self):
        self.properties = {}
        self.lines = []

    def add(self, key, value=None):
        if value is None:
            self.properties[key] = None
        elif isinstance(value, date):
            self.properties[key] = value.strftime("%Y%m%d")
        else:
            self.properties[key] = str(value)

    def add_line(self):
        l = TransactionLine()
        self.lines.append(l)
        return l

    def to_xml(self):
        xml = Element("table", {"name": "Transaction", "count": "1", "start": "0", "found": "1"})
        transaction = SubElement(xml, "transaction")
        for key, value in self.properties.iteritems():
            SubElement(transaction, key).text = value

        if len(self.lines) > 0:
            subfile = SubElement(transaction, "subfile", {"name": "Detail"})
            for line in self.lines:
                detail = SubElement(subfile, "detail")
                for key, value in line.properties.iteritems():
                    SubElement(detail, key).text = value

        output = '<?xml version="1.0"?>' + tostring(xml)
        logging.info(output)
        return output


class TransactionLine:
    def __init__(self):
        self.properties = {}

    def add(self, key, value):
        if value is None:
            self.properties[key] = None
        elif isinstance(value, date):
            self.properties[key] = value.strftime("%Y%m%d")
        else:
            self.properties[key] = str(value)


class Email:

    def __init__(self):
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
        msg["To"] = COMMASPACE.join(send_to) if isinstance(send_to, list) else send_to

        msg.attach(MIMEText(text))

        if attachment:
            assert isinstance(attachment, bytes)
            a = MIMEApplication(attachment, 'pdf')
            a.add_header('Content-Disposition', 'attachment; filename=\"{0}\"'.format(attachment_name))
            msg.attach(a)

        smtp = smtplib.SMTP(self.mx)
        smtp.sendmail(self.send_from, send_to, msg.as_string())
        smtp.quit()
