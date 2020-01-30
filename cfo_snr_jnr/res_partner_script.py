#     -*- encoding: utf-8 -*-
import xmlrpclib
import psycopg2
import csv
from datetime import datetime


def main():
    server = 'localhost'
    db = 'test_script_db'
    port = '9090'
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
            print("\n\n\n\n\n=============line[20]=========", line[20])
            # print("\n\n\n\n\n=============line[49]=========", line[49])

            partner_id = sock.execute_kw(str(db), 1
                                         , str(password)
                                         , 'res.partner'
                                         , 'search_read',
                                         [[['email', '=', line[3]]]],{'fields': ['id']})
                                         # {'fields': ['id']})


            # line[29] = line[29].strftime('%Y-%m-%d')
            # line[30] = line[30].strftime('%Y-%m-%d')
            print("\n\n\n\n\n=============partner_id=====",partner_id)
            # print("\n\n\n\n\n\n\=id========",partner_id[0].get('id'))
            # partner = list(partner_id[0].values())[0]
            # if new_user_id:
            #     sock.execute_kw(str(db), 2
            #                     , str(password)
            #                     , 'res.groups'
            #                     , 'write',
            #                     [[groups[0].get('id')],
            #                      {'users': [(4, new_user_id[0].get('id'))]}]
            #                     )
            if partner_id:
                print("\n\n\n\n\n=========line===========",line)
                msg = sock.execute_kw(str(db), 1, str(password)
                                          , 'res.partner'
                                          , 'write',
                                          [[partner_id[0].get('id')],
                                           {'name': line[0],
                                            'mobile': line[1],
                                            'partner_email': line[2],
                                            'email': line[3],
                                            'website': line[4],
                                            'student_number': line[5],
                                            'stu_street2': line[6],
                                            'street2': line[7],
                                            'emp_street2': line[8],
                                            'post_street2': line[9],
                                            'stu_street': line[10],
                                            'emp_street': line[11],
                                            'street': line[12],
                                            'post_street': line[13],
                                            'stu_state_id': line[14],
                                            'emp_state_id': line[15],
                                            'state_id': line[16],
                                            'post_state_id': line[17],
                                            'country_id': line[18],
                                            'post_country_id': line[19],
                                            'emp_country_id': line[20],
                                            'stu_country_id': line[21],
                                            'emp_zip': line[22],
                                            'zip': line[23],
                                            'stu_zip': line[24],
                                            'post_zip': line[25],
                                            'event_type_id': line[26],
                                            'vat_no_comp': line[27],
                                            'cq_password': line[28],
                                            'date_of_birth': line[29],
                                            'dob': line[30],
                                            'prof_body_image': line[31],
                                            'student_company': line[32],
                                            # 'image': line[33],
                                            'lang': line[34],
                                            'cfo_user': line[35],
                                            'customer': line[36],
                                            'user_id': line[37],
                                            'property_delivery_carrier': line[38],
                                            # 'property_product_pricelist': line[39],
                                            'supplier': line[40],
                                            'property_payment_term': line[41],
                                            'property_supplier_payment_term': line[42],
                                            'property_account_position': line[43],
                                            'property_account_payable': line[44],
                                            'property_account_receivable': line[45],
                                            'student_number_allocated': line[46],
                                            'previous_student': line[47],
                                            'current_student': line[48],
                                            'examwritten': line[49],
                                            }])
            else:
                print("\n\n\n\n\n=========line===========", line)
                res_partner = sock.execute_kw(str(db), 1
                                              , str(password)
                                              , 'res.partner'
                                              , 'create',
                                              [{'name': line[0],
                                                'mobile': line[1],
                                                'partner_email': line[2],
                                                'email': line[3],
                                                'website': line[4],
                                                'student_number': line[5],
                                                'stu_street2': line[6],
                                                'street2': line[7],
                                                'emp_street2': line[8],
                                                'post_street2': line[9],
                                                'stu_street': line[10],
                                                'emp_street': line[11],
                                                'street': line[12],
                                                'post_street': line[13],
                                                'stu_state_id': line[14],
                                                'emp_state_id': line[15],
                                                'state_id': line[16],
                                                'post_state_id': line[17],
                                                'country_id': line[18],
                                                'post_country_id': line[19],
                                                'emp_country_id': line[20],
                                                'stu_country_id': line[21],
                                                'emp_zip': line[22],
                                                'zip': line[23],
                                                'stu_zip': line[24],
                                                'post_zip': line[25],
                                                'event_type_id': line[26],
                                                'vat_no_comp': line[27],
                                                'cq_password': line[28],
                                                'date_of_birth': line[29],
                                                'dob': line[30],
                                                'prof_body_image': line[31],
                                                'student_company': line[32],
                                                # 'image': line[33],
                                                'lang': line[34],
                                                'cfo_user': line[35],
                                                'customer': line[36],
                                                'user_id': line[37],
                                                'property_delivery_carrier': line[38],
                                                'property_product_pricelist': line[39],
                                                'supplier': line[40],
                                                'property_payment_term': line[41],
                                                'property_supplier_payment_term': line[42],
                                                'property_account_position': line[43],
                                                'property_account_payable': line[44],
                                                'property_account_receivable': line[45],
                                                'student_number_allocated': line[46],
                                                'previous_student': line[47],
                                                'current_student': line[48],
                                                'examwritten': line[49],
                                                }])


if __name__ == '__main__':
    main()

#     # -*- encoding: utf-8 -*-
# import xmlrpclib
# import psycopg2
# import csv
# from datetime import datetime
#
#
# def main():
#     server = '127.0.0.1'
#     db = 'new_elsner_db'
#     port = '8069'
#     user = 'acespritech'
#     db_password = 'a'
#
#     serv_str = 'http://' + str(server) + ':' + str(port) + '/xmlrpc/object'
#     sock = xmlrpclib.ServerProxy(serv_str)
#
#     res_user_file = open('final_users.csv', "r")
#     res_user_reader = csv.reader(res_user_file)
#
#     conn = psycopg2.connect(dbname=db,user=user, password='123456', host=server)
#     cur = conn.cursor()
#
#     for row, line in enumerate(res_user_reader):
#         if not row:
#             continue
#         else:
#             old_user_id = line[1]
#             name = str(line[3])
#             login = str(line[2])
#             password = 'a'
#             cur.execute(''' INSERT INTO res_users(old_user_id,login,company_id,
#                             password)
#                             VALUES(%s,'%s',1,'a') '''%(old_user_id,login))
#             conn.commit()
#
#     cur.close()
#     conn.close()
#
# if __name__ == '__main__':
#     main()
