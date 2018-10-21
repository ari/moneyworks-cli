#!python3

import configparser
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as XML

import requests
from requests.auth import HTTPBasicAuth


class Moneyworks:

    def __init__(self, path):
        if path is None:
            path = 'mw.ini'

        config = configparser.ConfigParser()
        config_data = config.read(path)
        if len(config_data) == 0:
            raise ValueError("Failed to open mw.ini configuration file.")

        self.base_url = "http://" + config.get('mw_server', 'HOST') + ":" + config.get('mw_server', 'PORT') + "/REST/"
        self.url = self.base_url + urllib.parse.quote_plus(config.get('mw_server', 'DATA_FILE')) + "/"
        self.mw_auth = HTTPBasicAuth(config.get('mw_server', 'USERNAME'),
                                     config.get('mw_server', 'PASSWORD'))

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
        seqnum = self.__post("import/return_seq=true", xml).text
        return seqnum

    def get_email(self, company_code):
        """
        Get the email address from Moneyworks for a particular company
        :return email address string
        """
        return self.__get("export/table=name&search=" + urllib.parse.quote_plus("code=`" + company_code + "`") +
                          "&format=[email]").text

    def print_transaction(self, search, form):
        """
        Print the transaction
        :param search: a search string to select the correct record eg. "sequencenumber=`123`"
        :param form: the form to use when printing this record
        :return the pdf file as bytes
        """
        r = self.__get("doform/form=" + form + "&search=" + urllib.parse.quote_plus(search))
        return r.content

    def post_transaction(self, seqnum):
        """
        Post the transaction in Moneyworks
        :param seqnum the invoice's sequence number (this is not the same as the invoice/PO number)
        """
        return self.__post("post/seqnum=" + seqnum, "").text

    def export(self, table, search, format=None, sort=None):
        """
        Extract data from Moneyworks
        :param table: The table from which we want to get data eg. "name"
        :param search: A search string, eg. "DBalance>0". Put string constants between `backticks`
        :param format: a format for the returned data eg. "[code] [email] [DBalance]," or "xml". If nothing is passed then return a dict.
        :param sort: an optional sort expression
        :return A list of records or data formatted as per 'format'
        """

        table = table.lower()
        path = "export/table=" + table + "&search=" + urllib.parse.quote_plus(search)

        if sort:
            path = path + "&sort=" + urllib.parse.quote_plus(sort)

        if format:
            path += "&format=" + format
            return self.__get(path).text

        path += "&format=xml-verbose"
        xml = self.__get(path).text
        result = []

        for record in XML.fromstring(xml).findall(table):
            r = dict()
            result.append(r)
            for e in record:
                r[e.tag] = e.text

        return result

    def export_one(self, table, search, sort=None):
        """
        Extract a single record from Moneyworks. If more than one record is returned, then just get the first
        :param table: The table from which we want to get data eg. "name"
        :param search: A search string, eg. "DBalance>0". Put string constants between `backticks`
        :param sort: an optional sort expression
        :return A single record dict
        """

        data = self.export(table, search, sort=sort)
        if len(data) == 0:
            return None

        return data[0]