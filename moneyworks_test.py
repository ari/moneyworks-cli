import unittest
from moneyworks import Moneyworks, Transaction
from pprint import pprint


class TestMoneyworks(unittest.TestCase):

    def setUp(self):
        self.mw = Moneyworks()

    def test_version(self):
        self.assertGreater(self.mw.version(), 6)

    def test_get_forms(self):
        self.assertGreater(len(self.mw.get_forms()), 200)

    def test_get_email(self):
        self.assertEquals(self.mw.get_email("ISHTEST"), "accounts@acme.com.au")

    def test_print_transaction(self):
        pdf = self.mw.print_transaction('sequencenumber=`20680`', 'my_invoice')
        self.assertGreater(pdf, 1000)  # at least 1000 bytes of PDF
        self.assertIsInstance(pdf, bytes)

    def test_export(self):
        l = self.mw.export("name", "left(code, 3)=`ISH`")
        self.assertIsInstance(l, list)
        self.assertEquals(len(l), 2)

        l = self.mw.export("name", "code=`ISHTEST`")
        self.assertEquals(len(l), 1)
        pprint(l)
        self.assertEquals(l[0]['email'], "accounts@acme.com.au")
        self.assertEquals(l[0]['name'], "ish")

    def test_transaction(self):
        t = Transaction()
        t.add("type", "CP")
        t.add("type_num", 99.2)
        t.add("d", date(2006, 6, 14))
        t.add("w")
        for data in [1, 2]:
            l = t.add_line()
            l.add("detail.something", "value1")
            l.add("detail.something2", 2)

        self.assertEquals('<?xml version="1.0"?><table count="1" found="1" name="Transaction" start="0"><transaction><type_num>99.2</type_num><type>CP</type><d>20060614</d><w work-it-out="true" /><subfile name="Detail"><detail><detail.something2>2</detail.something2><detail.something>value1</detail.something></detail><detail><detail.something2>2</detail.something2><detail.something>value1</detail.something></detail></subfile></transaction></table>' \
            , t.to_xml())


if __name__ == '__main__':
    unittest.main()
