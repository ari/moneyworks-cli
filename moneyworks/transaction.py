#!python3

from datetime import date
from xml.etree.ElementTree import Element, SubElement, tostring

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
        line = TransactionLine()
        self.lines.append(line)
        return line

    def to_xml(self):
        xml = Element("table", {"name": "Transaction", "count": "1", "start": "0", "found": "1"})
        transaction = SubElement(xml, "transaction")
        for key, value in self.__sort_properties(self.properties):
            if value is None:
                SubElement(transaction, key, {"work-it-out": "true"})
            else:
                SubElement(transaction, key).text = value

        if len(self.lines) > 0:
            subfile = SubElement(transaction, "subfile", {"name": "Detail"})
            for line in self.lines:
                detail = SubElement(subfile, "detail")
                for key, value in self.__sort_properties(line.properties):
                    if value is None:
                        SubElement(detail, key, {"work-it-out": "true"})
                    else:
                        SubElement(detail, key).text = value

        # hardcode in gross to appear at the end since MW requires it
        SubElement(transaction, "gross", {"work-it-out": "true"})
        output = '<?xml version="1.0"?>' + tostring(xml, encoding="unicode")
        return output

    @staticmethod
    def __sort_properties(properties):
        """
        This constructs a tuple for each element in the list, if the value is None the tuple with be (True, None),
        if the value is anything else it will be (False, x) (where x is the value). Since tuples are sorted item by
        item, this means that all non-None elements will come first (since False < True), and then be sorted by value.
        """
        return sorted(list(properties.items()), key=lambda x: (x[1] is None, x[1]))


class TransactionLine:
    def __init__(self):
        self.properties = {}

    def add(self, key, value=None):
        if value is None:
            self.properties[key] = None
        elif isinstance(value, date):
            self.properties[key] = value.strftime("%Y%m%d")
        else:
            self.properties[key] = str(value)
