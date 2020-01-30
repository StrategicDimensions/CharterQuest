import xmlrpclib
import psycopg2
import csv
from datetime import datetime


def main():
    server = 'localhost'
    db = 'charterquest_v11'
    port = '8069'
    user = 'admin'
    password = 'a'

    serv_str = 'http://' + str(server) + ':' + str(port) + '/xmlrpc/2/object'
    sock = xmlrpclib.ServerProxy(serv_str)
    res_user_file = open('res.partner_1.csv', "r")
    res_user_reader = csv.reader(res_user_file)
    for row, line in enumerate(res_user_reader):
        if not row:
            continue
        else:
            # print("\n\n\n\n\n=========line[0]======", line[0])
            # print("\n\n\n\n\n=========line[1]======", line[1])
            print("\n\n\n\n=========line[3]=========",line[3])
            # print("\n\n\n\n\n=============line[48]=========", line[48])
            # print("\n\n\n\n\n=============line[49]=========", line[49])

            partner_id = sock.execute_kw(str(db), 1
                                         , str(password)
                                         , 'res.partner'
                                         , 'search_read',
                                         [[['email', '=', line[3]]]],{'fields': ['id']})



if __name__ == '__main__':
    main()
