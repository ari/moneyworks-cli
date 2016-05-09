import unittest
from moneyworks import Moneyworks
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
        for data in [1, 2, 3, 4]:
            l = t.add_line()
            l.add("detail", data)

if __name__ == '__main__':
    unittest.main()
