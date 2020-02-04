import xmlrpclib
import psycopg2
import csv
from datetime import datetime
# from csv2odoo import Model, Field, Odoo, Session


def main():
    server = 'localhost'
    db = 'charterquest_v11'
    port = '8069'
    user = 'admin'
    password = 'a'

    # odoo = Odoo(host='localhost', port=8069,user='admin', pwd='a', dbname='charterquest_v11')
    #
    # session = Session('file.csv', delimiter=';', quotechar='"', encoding='utf-8',offset=1, limit=10)

    serv_str = 'http://' + str(server) + ':' + str(port) + '/xmlrpc/2/object'
    sock = xmlrpclib.ServerProxy(serv_str)
    res_user_file = open('res.partner_4.csv', "r")
    res_user_reader = csv.reader(res_user_file)
    for row, line in enumerate(res_user_reader):
        if not row:
            continue
        else:
          partner_id
