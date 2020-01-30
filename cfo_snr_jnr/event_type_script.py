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
    res_user_file = open('event.type.csv', "r")
    res_user_reader = csv.reader(res_user_file)
    for row, line in enumerate(res_user_reader):
        if not row:
            continue
        else:
           print("\n\n\n\n==============line 1====",line[1])
           print("\n\n\n\n==============line 2====", line[2])
           event_id = sock.execute_kw(str(db), 1
                                         , str(password)
                                         , 'event.type'
                                         , 'search_read',
                                         [[['name', '=', line[1]]]], {'fields': ['id']})
           print("\n\n\n\n\=============country id=======",event_id)

           if event_id:
               continue
                # cntry = sock.execute_kw(str(db), 1, str(password)
                #                           , 'res.partner'
                #                           , 'write',
                #                           [[country_id[0].get('id')],
                #                            {'name': line[1],
                #                             'code':line[2]}])
           else:
               event = sock.execute_kw(str(db), 1, str(password)
                                       , 'event.type'
                                       , 'create',
                                       [{'name': line[1],
                                         'discount': line[4],
                                         # 'order': line[3],
                                         'publish_on_portal': line[5],
                                         'publish_on_website': line[6],
                                         'professional_body_code': line[7]}])

if __name__ == '__main__':
    main()