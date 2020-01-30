from odoo import fields, models, api, _
import io
import csv
import base64
from odoo.tools import pycompat

class YourWizard(models.TransientModel):
    _name = 'your_wizard'
    # your file will be stored here:
    csv_file = fields.Binary(string='CSV File', required=True)

    @api.multi
    def import_csv(self, options):
        csv_data = self.csv_file

        # TODO: guess encoding with chardet? Or https://github.com/aadsm/jschardet
        encoding = options.get('encoding', 'utf-8')
        if encoding != 'utf-8':
            # csv module expect utf-8, see http://docs.python.org/2/library/csv.html
            csv_data = csv_data.decode(encoding).encode('utf-8')

        csv_iterator = pycompat.csv_reader(io.BytesIO(csv_data))
        print("\n\n\n\n\n\n===============csv_iterator=========",csv_iterator)
        for row, line in csv_iterator:
            if not row:
                continue
            else:
                print("\n\n\n\n\n=========line[0]======", line[0])
                print("\n\n\n\n\n=========line[1]======", line[1])
                print("\n\n\n\n=========line[3]=========", line[3])
                print("\n\n\n\n\n=============line[48]=========", line[48])
                print("\n\n\n\n\n=============line[49]=========", line[49])



                # partner_id = sock.execute_kw(str(db), 2
                #                              , str(password)
                #                              , 'crm.lead'
                #                              , 'search_read',
                #                              [[['old_crm_lead_id', '=', line[20]]]],
                #                              {'fields': ['id'], 'limit': 1})

                # partner_id = sock.execute_kw(str(db), 1
                #                              , str(password)
                #                              , 'res.partner'
                #                              , 'search_read',
                #                              [[['email', '=', line[3]]]])
                # # {'fields': ['id'], 'limit': 1})
                # # line[29] = line[29].strftime('%Y-%m-%d')
                # # line[30] = line[30].strftime('%Y-%m-%d')
                # print("\n\n\n\n\n=============partner_id=====", partner_id)
                # if partner_id:
                #     message = sock.execute_kw(str(db), 1, str(password)
                #                               , 'res.partner'
                #                               , 'update',
                #                               [{'name': line[0],
                #                                 'mobile': line[1],
                #                                 'partner_email': line[2],
                #                                 'email': line[3],
                #                                 'website': line[4],
                #                                 'student_number': line[5],
                #                                 'stu_street2': line[6],
                #                                 'street2': line[7],
                #                                 'emp_street2': line[8],
                #                                 'post_street2': line[9],
                #                                 'stu_street': line[10],
                #                                 'emp_street': line[11],
                #                                 'street': line[12],
                #                                 'post_street': line[13],
                #                                 'stu_state_id': line[14],
                #                                 'emp_state_id': line[15],
                #                                 'state_id': line[16],
                #                                 'post_state_id': line[17],
                #                                 'country_id': line[18],
                #                                 'post_country_id': line[19],
                #                                 'emp_country_id': line[20],
                #                                 'stu_country_id': line[21],
                #                                 'emp_zip': line[22],
                #                                 'zip': line[23],
                #                                 'stu_zip': line[24],
                #                                 'post_zip': line[25],
                #                                 'event_type_id': line[26],
                #                                 'vat_no_comp': line[27],
                #                                 'cq_password': line[28],
                #                                 'date_of_birth': line[29],
                #                                 'dob': line[30],
                #                                 'prof_body_image': line[31],
                #                                 'student_company': line[32],
                #                                 'image': line[33],
                #                                 'lang': line[34],
                #                                 'cfo_user': line[35],
                #                                 'customer': line[36],
                #                                 'user_id': line[37],
                #                                 'property_delivery_carrier': line[38],
                #                                 'property_product_pricelist': line[39],
                #                                 'supplier': line[40],
                #                                 'property_payment_term': line[41],
                #                                 'property_supplier_payment_term': line[42],
                #                                 'property_account_position': line[43],
                #                                 'property_account_payable': line[44],
                #                                 'property_account_receivable': line[45],
                #                                 'student_number_allocated': line[46],
                #                                 'previous_student': line[47],
                #                                 'current_student': line[48],
                #                                 'examwritten': line[49],
                #                                 }])
                # else:
                #     res_partner = sock.execute_kw(str(db), 1
                #                                   , str(password)
                #                                   , 'res.partner'
                #                                   , 'create',
                #                                   [{'name': line[0],
                #                                     'mobile': line[1],
                #                                     'partner_email': line[2],
                #                                     'email': line[3],
                #                                     'website': line[4],
                #                                     'student_number': line[5],
                #                                     'stu_street2': line[6],
                #                                     'street2': line[7],
                #                                     'emp_street2': line[8],
                #                                     'post_street2': line[9],
                #                                     'stu_street': line[10],
                #                                     'emp_street': line[11],
                #                                     'street': line[12],
                #                                     'post_street': line[13],
                #                                     'stu_state_id': line[14],
                #                                     'emp_state_id': line[15],
                #                                     'state_id': line[16],
                #                                     'post_state_id': line[17],
                #                                     'country_id': line[18],
                #                                     'post_country_id': line[19],
                #                                     'emp_country_id': line[20],
                #                                     'stu_country_id': line[21],
                #                                     'emp_zip': line[22],
                #                                     'zip': line[23],
                #                                     'stu_zip': line[24],
                #                                     'post_zip': line[25],
                #                                     'event_type_id': line[26],
                #                                     'vat_no_comp': line[27],
                #                                     'cq_password': line[28],
                #                                     'date_of_birth': line[29],
                #                                     'dob': line[30],
                #                                     'prof_body_image': line[31],
                #                                     'student_company': line[32],
                #                                     'image': line[33],
                #                                     'lang': line[34],
                #                                     'cfo_user': line[35],
                #                                     'customer': line[36],
                #                                     'user_id': line[37],
                #                                     'property_delivery_carrier': line[38],
                #                                     'property_product_pricelist': line[39],
                #                                     'supplier': line[40],
                #                                     'property_payment_term': line[41],
                #                                     'property_supplier_payment_term': line[42],
                #                                     'property_account_position': line[43],
                #                                     'property_account_payable': line[44],
                #                                     'property_account_receivable': line[45],
                #                                     'student_number_allocated': line[46],
                #                                     'previous_student': line[47],
                #                                     'current_student': line[48],
                #                                     'examwritten': line[49],
                #                                     }])
