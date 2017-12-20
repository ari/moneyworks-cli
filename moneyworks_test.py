#!/usr/local/bin/python3

import unittest
from datetime import date
import moneyworks
from pprint import pprint


class TestMoneyworks(unittest.TestCase):

    def setUp(self):
        self.mw = moneyworks.Moneyworks()

    def test_version(self):
        self.assertGreater(self.mw.version(), 6)

    def test_get_forms(self):
        self.assertGreater(len(self.mw.get_forms()), 200)

    def test_get_email(self):
        self.assertEqual(self.mw.get_email("ISHTEST"), "accounts@acme.com.au")

    def test_print_transaction(self):
        pdf = self.mw.print_transaction('sequencenumber=`20680`', 'my_invoice')
        self.assertGreater(pdf, 1000)  # at least 1000 bytes of PDF
        self.assertIsInstance(pdf, bytes)

    def test_export(self):
        data = self.mw.export("name", "left(code, 3)=`ISH`")
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

        data = self.mw.export("name", "code=`ISHTEST`")
        self.assertEqual(len(data), 1)
        pprint(data)
        self.assertEqual(data[0]['email'], "accounts@acme.com.au")
        self.assertEqual(data[0]['name'], "ish")

    def test_transaction(self):
        t = moneyworks.Transaction()
        t.add("w")
        t.add("type", "CP")
        t.add("type_num", 99.2)
        t.add("d", date(2006, 6, 14))
        for _ in [1, 2]:
            data = t.add_line()
            data.add("empty")
            data.add("detail.something", "value1")
            data.add("detail.something2", 2)

        self.assertEqual(
            '<?xml version="1.0"?><table count="1" found="1" name="Transaction" start="0"><transaction><d>20060614' +
            '</d><type_num>99.2</type_num><type>CP</type><w work-it-out="true" /><subfile name="Detail"><detail>' +
            '<detail.something2>2</detail.something2><detail.something>value1</detail.something>' +
            '<empty work-it-out="true" /></detail><detail><detail.something2>2</detail.something2>' +
            '<detail.something>value1</detail.something><empty work-it-out="true" /></detail></subfile>' +
            '<gross work-it-out="true" /></transaction></table>',
            t.to_xml())


if __name__ == '__main__':
    unittest.main()
