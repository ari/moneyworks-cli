# Moneyworks CLI

A python API for Cognito's Moneyworks accounting software

A library for python to make it easier to export, import and print data from Moneyworks. Some typical uses include:

* Automatically creating invoices each month, posting them and emailing the pdf
* Importing payroll data from Xero, creating super transactions, payroll and petty cash.
* Importing data from other systems on a regular basis
* Performing data checks on a regular basis

# Requirements

Cognito Moneyworks with an available REST user enabled on a port of your choice. We have only tested this library with Moneyworks Server, but it may work with the standalone version.

You'll need python 3.5 or above.

# Installing

Install with pip.

    pip install moneyworks

Copy the mw.ini file to your local folder and edit to you needs. You'll also need to ensure this user is given appropriate rights inside Moneyworks. Unfortunately due to limitations in Moneyworks, if you try this library with a user who doesn't have sufficient rights, random things happen. For example, printing an unposted invoice from a user without that right results in a blank PDF but no error. In other cases unhelpful 500 errors are returned without any information.

# How to use

    from moneyworks import Moneyworks
    mw = Moneyworks()
    
    # Print the version of Moneyworks we are talking to
    print mw.version()
    
    # Get the email address of the first person in a company, selected by code
    print mw.get_email("ACME")

    # Get a PDF document (which you can save or email) of a transaction
    pdf = mw.print_transaction('sequencenumber=`9999`', 'my_invoice')
    
    # Export some data for all companies with code starting with 'A' and print their names
    my_data = mw.export("name", "left(code, 1)=`A`")
    for contact in my_data:
      print contact['name']

## Advanced usage

Let's see how we might import some data, generate invoices, post them, print an invoice and email that

    from moneyworks import Moneyworks, Transaction, Email

    mw = Moneyworks('/etc/mw.ini')
    e = Email()

    t = Transaction()
    t.add("type", "DI")
    t.add("theirref", "1234")
    t.add("transdate", datetime.date.today().replace(day=1))  # First of the month
    t.add("NameCode", "ACME")
    t.add("description", "Monthly services")
    t.add("tofrom", "Acme Pty Ltd")
    t.add("duedate")
    t.add("duedate")
    t.add("contra")
    t.add("ourref")

    l = t.add_line()
    l.add("detail.account", "4100")
    l.add("detail.net", 1300.35)
    l.add("detail.description", "Services")
    l.add("detail.taxcode")
    l.add("detail.tax")
    l.add("detail.gross")

    invoice_sequence = mw.create_transaction(t.to_xml())
    result = mw.post_transaction(invoice_sequence)
    pdf = mw.print_transaction('sequencenumber=`' + invoice_sequence + "`", 'my_invoice')

    email = mw.get_email("ACME")
    e.send_mail(email, "invoice", "Please send us some money.", pdf, "invoice.pdf")
        
        

# License

This library is licensed under the Apache Public License 2. Contributions and enhancements are welcome.

# For developers

In order to publish a new version of this module, edit setup.py with the new version number then run:

    python3.6 setup.py sdist
    twine upload dist/*
    rm -fr dist/*