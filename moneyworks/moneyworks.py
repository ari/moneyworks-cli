#!python3

import configparser
from datetime import datetime
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as XML

import requests
from requests.auth import HTTPBasicAuth


class Moneyworks:

    def __init__(self, path=None):
        if path is None:
            path = 'mw.ini'

        config = configparser.ConfigParser()
        config_data = config.read(path)
        if len(config_data) == 0:
            raise ValueError("Failed to open mw.ini configuration file at %s." % path)

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

    def export(self, table, search, format=None, sort=None, direction='ascending'):
        """
        Extract data from Moneyworks
        :param table: The table from which we want to get data eg. "name"
        :param search: A search string, eg. "DBalance>0". Put string constants between `backticks`
        :param format: a format for the returned data eg. "[code] [email] [DBalance]," or "xml". If nothing is passed then return a dict.
        :param sort: an optional sort expression
        :return A list of records or data formatted as per 'format'
        """

        table = table.lower()
        if direction != 'ascending':
            direction = 'descending'
        path = "export/table=" + table + "&search=" + urllib.parse.quote_plus(search) + "&direction=" + direction

        if sort:
            path = path + "&sort=" + urllib.parse.quote_plus(sort)

        if format:
            path += "&format=" + format
            return self.__get(path).text

        path += "&format=xml-verbose"
        xml = self.__get(path).text
        result = []
        for record in XML.fromstring(xml).findall(table):
            result.append(self._build_dict(record))

        return result

    def _build_dict(self, record):
        r = {}
        for e in record:
            if e.tag == "subfile":
                subfile = []
                r[e.attrib['name'] + 's'] = subfile
                for sub in e:
                    subfile.append(self._build_dict(sub))

            elif e.tag.endswith('date'):
                r[e.tag] = datetime.strptime(e.text, '%Y%m%d').date()
            elif e.tag.endswith('time'):
                r[e.tag] = datetime.strptime(e.text, '%Y%m%d%H%M%S')
            else:
                try:
                    r[e.tag] = int(e.text)
                except:
                    try:
                        r[e.tag] = float(e.text)
                    except:
                        r[e.tag] = e.text
        return r

    def export_one(self, table, search, sort=None, direction='ascending'):
        """
        Extract a single record from Moneyworks. If more than one record is returned, then just get the first
        :param table: The table from which we want to get data eg. "name"
        :param search: A search string, eg. "DBalance>0". Put string constants between `backticks`
        :param sort: an optional sort expression
        :return A single record dict
        """

        data = self.export(table, search, sort=sort, direction=direction)
        if len(data) == 0:
            return None

        return data[0]