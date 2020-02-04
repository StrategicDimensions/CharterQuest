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
    res_user_file = open('res.partner_4.csv', "r")
    res_user_reader = csv.reader(res_user_file)
    for row, line in enumerate(res_user_reader):
        if not row:
            continue
        else:
            # print("\n\n\n\n\n=========line[0]======", line[0])
            # print("\n\n\n\n\n=========line[1]======", line[1])
            print("\n\n\n\n=========line[4]=========",line[4])
            print("\n\n\n\n\n=============line[31]=========", line[31])
            # print("\n\n\n\n\n=============line[49]=========", line[49])

            partner_id = sock.execute_kw(str(db), 1
                                         , str(password)
                                         , 'res.partner'
                                         , 'search_read',
                                         [[['email', '=', line[4]]]],{'fields': ['id']})
                                         # {'fields': ['id']})

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
                                            'phone':line[1],
                                            'mobile': line[2],
                                            'email': line[4],
                                            'website': line[5],
                                            'student_number': line[6],
                                            # 'stu_street2': line[6],
                                            'street2': line[7] or line[8] or line[9] or line[10],
                                            # 'emp_street2': line[8],
                                            # 'post_street2': line[9],
                                            # 'stu_street': line[10],
                                            # 'emp_street': line[11],
                                            'street': line[11] or line[12] or line[13] or line[14],
                                            # 'post_street': line[13],
                                            # 'stu_state_id': line[14],
                                            # 'emp_state_id': line[15],
                                            'city': line[15] or line[16] or line[17] or line[18],
                                            'state_id': line[19] or line[20] or line[21] or line[22],
                                            # 'post_state_id': line[17],
                                            'country_id': line[23] or line[24] or line[25] or line[26],
                                            # 'post_country_id': line[19],
                                            # 'emp_country_id': line[20],
                                            # 'stu_country_id': line[21],
                                            # 'emp_zip': line[22],
                                            'zip': line[27] or line[28] or line[29] or line[30],
                                            # 'stu_zip': line[24],
                                            # 'post_zip': line[25],
                                            # 'event_type_id': line[31],
                                            # 'vat_no_comp': line[32],
                                            # 'cq_password': line[33],
                                            # 'prof_password': line[34],
                                            # 'title': line[35],
                                            # 'dob': line[36] or line[37],
                                            # 'prof_body_id': line[38],
                                            # 'student_company': line[39],
                                            # # 'image': line[33],
                                            # 'lang': line[40],
                                            # 'cfo_user': line[41],
                                            # 'customer': line[43],
                                            # 'idpassport': line[44],
                                            # 'property_stock_customer': line[45],
                                            # 'property_stock_supplier': line[46],
                                            # 'opt_out': line[47],
                                            # # 'user_id': line[37],
                                            # # 'property_delivery_carrier': line[38],
                                            # # 'property_product_pricelist': line[39],
                                            # # 'supplier': line[40],
                                            # # 'property_payment_term': line[41],
                                            # # 'property_supplier_payment_term': line[42],
                                            # # 'property_account_position': line[43],
                                            # 'is_campus': line[54],
                                            # 'property_account_payable_id': line[50] or line[51] or line[52],
                                            # 'property_account_receivable_id': line[48] or line[49] or line[53],
                                            # 'student_number_allocated': line[57],
                                            # 'previous_student': line[58],
                                            # 'current_student': line[59],
                                            # 'examwritten': line[60],
                                            }])
            else:
                print("\n\n\n\n\n=========line===========", line)
                res_partner = sock.execute_kw(str(db), 1
                                              , str(password)
                                              , 'res.partner'
                                              , 'create',
                                              [{'name': line[0],
                                            'phone':line[1],
                                            'mobile': line[2],
                                            'email': line[4],
                                            'website': line[5],
                                            'student_number': line[6],
                                            # 'stu_street2': line[6],
                                            'street2': line[7] or line[8] or line[9] or line[10],
                                            # 'emp_street2': line[8],
                                            # 'post_street2': line[9],
                                            # 'stu_street': line[10],
                                            # 'emp_street': line[11],
                                            'street': line[11] or line[12] or line[13] or line[14],
                                            # 'post_street': line[13],
                                            # 'stu_state_id': line[14],
                                            # 'emp_state_id': line[15],
                                            'city': line[15] or line[16] or line[17] or line[18],
                                            'state_id': line[19] or line[20] or line[21] or line[22],
                                            # 'post_state_id': line[17],
                                            'country_id': line[23] or line[24] or line[25] or line[26],
                                            # 'post_country_id': line[19],
                                            # 'emp_country_id': line[20],
                                            # 'stu_country_id': line[21],
                                            # 'emp_zip': line[22],
                                            'zip': line[27] or line[28] or line[29] or line[30],
                                            # 'stu_zip': line[24],
                                            # 'post_zip': line[25],
                                            'event_type_id': line[31],
                                            'vat_no_comp': line[32],
                                            'cq_password': line[33],
                                            'prof_password': line[34],
                                            'title': line[35],
                                            'dob': line[36] or line[37],
                                            'prof_body_id': line[38],
                                            'student_company': line[39],
                                            # 'image': line[33],
                                            'lang': line[40],
                                            'cfo_user': line[41],
                                            'customer': line[43],
                                            'idpassport': line[44],
                                            'property_stock_customer': line[45],
                                            'property_stock_supplier': line[46],
                                            'opt_out': line[47],
                                            # 'user_id': line[37],
                                            # 'property_delivery_carrier': line[38],
                                            # 'property_product_pricelist': line[39],
                                            # 'supplier': line[40],
                                            # 'property_payment_term': line[41],
                                            # 'property_supplier_payment_term': line[42],
                                            # 'property_account_position': line[43],
                                            'is_campus': line[54],
                                            'property_account_payable_id': line[50] or line[51] or line[52],
                                            'property_account_receivable_id': line[48] or line[49] or line[53],
                                            'student_number_allocated': line[57],
                                            'previous_student': line[58],
                                            'current_student': line[59],
                                            'examwritten': line[60],
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
