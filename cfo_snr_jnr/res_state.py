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
    res_user_file = open('res.country.state.csv', "r")
    res_user_reader = csv.reader(res_user_file)
    for row, line in enumerate(res_user_reader):
        if not row:
            continue
        else:
           print("\n\n\n\n==============line 1====",line[1])
           print("\n\n\n\n==============line 2====", line[2])
           print("\n\n\n\n==============line 3====", line[3])
           print("\n\n\n\n==============line 4====", line[4])
           state_id = sock.execute_kw(str(db), 1
                                         , str(password)
                                         , 'res.country.state'
                                         , 'search_read',
                                         [[['name', '=', line[4]]]], {'fields': ['id']})
           print("\n\n\n\n\=============state id=======",state_id)

           if state_id:
               continue
                # cntry = sock.execute_kw(str(db), 1, str(password)
                #                           , 'res.partner'
                #                           , 'write',
                #                           [[country_id[0].get('id')],
                #                            {'name': line[1],
                #                             'code':line[2]}])
           else:
               country = sock.execute_kw(str(db), 1
                                         , str(password)
                                         , 'res.country'
                                         , 'search_read',
                                         [[['name', '=', line[2]]]], {'fields': ['id']})
               country_id = country[0].get('id')
               print("\n\n\n\n==========country_id======",country_id)
               state = sock.execute_kw(str(db), 1, str(password)
                                       , 'res.country.state'
                                       , 'create',
                                       [{'name': line[4],
                                         'code': line[3],
                                         'country_id':country_id
                                         }])

if __name__ == '__main__':
    main()