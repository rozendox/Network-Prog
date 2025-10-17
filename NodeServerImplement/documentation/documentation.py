
"""
#!/usr/bin/env python3

version = '3.11.7 '
title = '''

 Documentation for my server-node code flow
 Author: Rzdx

 Version:''' + version + '''
 '''

func

admin.super.agent
 |
 -> register new users
           |
           -> at least 1 (one) user.Requester and 1 (one) user.Manager

(important) - The system only work if we have both of these users.

user.request
       |
       -> make the request

user.accountancy
      |
      -> look the request and accept or not if the company has sufficient fund to make the purchase
          |
          -> if the company has:
          |     |
          |     -> the req will get in the user.Manager
          |     (the user.Accountancy accept the purchase)
          |
          -> if the company do not have fund:
               |
               -> the user.Accountancy refuse the purchase and the request will back to the user.request

user.manager
     |
     -> If the request has benn accepted:
        |
        -> the user.Manager will register the items
        |
        -> the user.Manager will label the items and record in the Excel
            -> after the record in the Excel spreadsheet he can register that on the _label.table_

"""

