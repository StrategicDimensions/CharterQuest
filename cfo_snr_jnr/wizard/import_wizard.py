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
        # encoding = options.get('encoding', 'utf-8')
        # if encoding != 'utf-8':
        #     # csv module expect utf-8, see http://docs.python.org/2/library/csv.html
        #     csv_data = csv_data.decode(encoding).encode('utf-8')

        csv_iterator = pycompat.csv_reader(io.BytesIO(csv_data))
        # csv_iterator = pycompat.csv_reader(csv_data)
        print("\n\n\n\n\n\n===============csv_iterator=========",csv_iterator)
        for line in csv_iterator:
            if not line:
                continue
            else:
                print("\n\n\n\n\n=========line[0]======", line[0])
                print("\n\n\n\n\n=========line[1]======", line[1])
                print("\n\n\n\n=========line[3]=========", line[3])
                print("\n\n\n\n\n=============line[48]=========", line[48])
                print("\n\n\n\n\n=============line[49]=========", line[49])

                # partner_id = self.env['res.partner'].search([('email','=',line[4])])

                # if partner_id:
                #
                #     update_partner = partner_id.write({'name': line[0],
                #                             'phone':line[1],
                #                             'mobile': line[2],
                #                             'email': line[4],
                #                             'website': line[5],
                #                             'student_number': line[6],
                #                             'street2': line[7] or line[8] or line[9] or line[10],
                #                             'street': line[11] or line[12] or line[13] or line[14],
                #                             'city': line[15] or line[16] or line[17] or line[18],
                #                             'state_id': line[19] or line[20] or line[21] or line[22],
                #                             'country_id': line[23] or line[24] or line[25] or line[26],
                #                             'zip': line[27] or line[28] or line[29] or line[30],
                #                             'event_type_id': line[31],
                #                             'vat_no_comp': line[32],
                #                             'cq_password': line[33],
                #                             'prof_password': line[34],
                #                             'title': line[35],
                #                             'dob': line[36] or line[37],
                #                             'prof_body_id': line[38],
                #                             'student_company': line[39],
                #                             'lang': line[40],
                #                             'cfo_user': line[41],
                #                             'customer': line[43],
                #                             'idpassport': line[44],
                #                             'property_stock_customer': line[45],
                #                             'property_stock_supplier': line[46],
                #                             'opt_out': line[47],
                #                             'is_campus': line[54],
                #                             'property_account_payable_id': line[50] or line[51] or line[52],
                #                             'property_account_receivable_id': line[48] or line[49] or line[53],
                #                             'student_number_allocated': line[57],
                #                             'previous_student': line[58],
                #                             'current_student': line[59],
                #                             'examwritten': line[60],
                #                             })



