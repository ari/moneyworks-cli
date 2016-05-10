# Moneyworks CLI

A python API for Cognito's Moneyworks accounting software

A library for python 2.7 to make it easier to export, import and print data from Moneyworks. Some typical uses include:

* Automatically creating invoices each month, posting them and emailing the pdf
* Importing payroll data from Xero, creating super transactions, payroll and petty cash.
* Importing data from other systems on a regular basis
* Performing data checks on a regular basis

# Requirements

Cognito Moneyworks with an available REST user enabled on a port of your choice. We have only tested this library with Moneyworks Server, but it may work with the standalone version.

You'll need python 2.7 or above. It hasn't been tested with python 3.x.

# Installing

At the moment, this library isn't distributed with pip. You'll just need to copy moneyworks.py into your project folder.

Edit the mw.ini file to your needs. Set the IP address, password and so on. You'll also need to ensure this user is given appropriate rights inside Moneyworks. Unfortunately due to limitations in Moneyworks, if you try this library with a user who doesn't have sufficient rights, random things happen. For example, printing an unposted invoice from a user without that right results in a blank PDF but no error. In other cases unhelpful 500 errors are returned without any information.

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

    from moneyworks import Moneyworks
    from moneyworks import Email

    mw = Moneyworks()
    e = Email()

    # it is beyond the scope of this example on how to create the following variables
    xml = ...some code to create the invoice structure...
    name_code = ...the contact code in Moneyworks...
    
    invoice_sequence = mw.create_transaction(xml)
    result = mw.post_transaction(invoice_sequence)
    pdf = mw.print_transaction('sequencenumber=`' + invoice_sequence + "`", 'my_invoice')

    email = mw.get_email(name_code)
    e.send_mail(email, "invoice", "Please send us some money.", pdf, "invoice.pdf")
        
        

# License

This library is licensed under the Apache Public License 2. Contributions and enhancements are welcome.
