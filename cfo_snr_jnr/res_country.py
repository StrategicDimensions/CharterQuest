#     -*- encoding: utf-8 -*-
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
    res_user_file = open('res.country.csv', "r")
    res_user_reader = csv.reader(res_user_file)
    for row, line in enumerate(res_user_reader):
        if not row:
            continue
        else:
           print("\n\n\n\n==============line 1====",line[1])
           print("\n\n\n\n==============line 2====", line[2])
           country_id = sock.execute_kw(str(db), 1
                                         , str(password)
                                         , 'res.country'
                                         , 'search_read',
                                         [[['code', '=', line[2]]]], {'fields': ['id']})
           print("\n\n\n\n\=============country id=======",country_id)

           if country_id:
               continue
                # cntry = sock.execute_kw(str(db), 1, str(password)
                #                           , 'res.partner'
                #                           , 'write',
                #                           [[country_id[0].get('id')],
                #                            {'name': line[1],
                #                             'code':line[2]}])
           else:
               contry = sock.execute_kw(str(db), 1, str(password)
                                       , 'res.country'
                                       , 'create',
                                       [{'name': line[1],
                                         'code': line[2]}])

if __name__ == '__main__':
    main()