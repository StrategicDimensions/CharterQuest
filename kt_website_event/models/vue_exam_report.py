from odoo.addons.l10n_eu_service.wizard import wizard
from odoo import models, fields
import re
from odoo.tools.translate import _
from io import StringIO
import base64
import xlrd
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from datetime import datetime, timedelta, date
import xlwt
# import xlsxwriter
from xlwt import *
from datetime import datetime, date
import calendar

try:
    import xlwt
    from xlwt import *
except Exception as e:
    raise wizard.except_wizard(
        _('User Error'), _('Please Install xlwt Library.!'))


class event(models.Model):
    _inherit = 'event.event'

    def send_vue_exam_report(self):
        event_obj = self.env['event.event']
        # partner_ids = partner_obj.search(cr,uid,[('imported_subscribers','=',False),('is_subscriber','=',False)])
        # event_ids = event_obj.search(cr,uid,[('date_begin', '>=', '2017-06-27 00:00:00'), 'state','=','confirm'),('pc_exam', '=', True), ('registration_ids', '!=', False)])
        event_ids = event_obj.search([('date_begin', '>=', time.strftime('%Y-%m-%d 00:00:00')), ('pc_exam', '=', True),
                                      ('registration_ids', '!=', False)])

        fp = StringIO()
        wb = xlwt.Workbook(encoding='utf-8')
        header_style2 = xlwt.easyxf(
            "font: bold on;align: horiz center; pattern: pattern solid, fore_colour white;")
        header_style3 = xlwt.easyxf(
            "font: bold on,height 260;align: horiz center; pattern: pattern solid, fore_colour white;")
        header_style4 = xlwt.easyxf(
            "font: bold on,height 200;align: horiz center; pattern: pattern solid, fore_colour ice_blue;")
        header_style5 = xlwt.easyxf(
            "font: bold off;align: horiz center; pattern: pattern solid, fore_colour white;")
        header_style6 = xlwt.easyxf(
            "font: bold on,height 260;align: horiz center; pattern: pattern solid, fore_colour gray25;")
        header_style7 = xlwt.easyxf(
            "font: bold off;align: horiz center; pattern: pattern solid, fore_colour light_green;")
        header_style8 = xlwt.easyxf(
            "font: bold off;align: horiz center; pattern: pattern solid, fore_colour orange;")

        final_arr_data = {}
        filename = 'Pearson-Vue Exam Reports.xls'
        lead_obj = self.env["crm.lead"]
        worksheet = wb.add_sheet("VUE-EXAM-REPORT" + ".xls")
        for i in range(0, 50):
            column = worksheet.col(i)
            column.width = 300 * 45

        worksheet.write(0, 0, "Event Name", header_style4)
        worksheet.write(0, 1, "Registrations/Name", header_style4)
        worksheet.write(0, 2, "Location/Name", header_style4)
        worksheet.write(0, 3, "Registrations/Event Start Date", header_style4)
        worksheet.write(0, 4, "Registrations/Status", header_style4)
        worksheet.write(0, 5, "Paid Prof Body", header_style4)
        worksheet.write(0, 6, "Invoice Number", header_style4)
        worksheet.write(0, 7, "Prof Body Student ID", header_style4)
        worksheet.write(0, 8, "Prof Body Login Password", header_style4)
        worksheet.write(0, 9, "Email", header_style4)
        worksheet.write(0, 10, "Mobile", header_style4)

        line = 1
        i = 1
        data = {}

        for item in event_ids:
            event_data = event_obj.browse(item)

            # if lead_data.type == "lead":
            worksheet.write(line, 0, event_data.name or '', header_style5)
            for rec in event_data.registration_ids:
                # if rec.state == 'open':
                worksheet.write(line, 1, rec.name or '', header_style5)
                worksheet.write(line, 4, rec.state or '', header_style5)
                inv_id = self.env['account.invoice'].search([('origin', '=', rec.origin)])
                if inv_id:
                    inv_data = self.env['account.invoice'].browse(inv_id)
                    paid_body = inv_data.paid_body
                    if paid_body:
                        worksheet.write(line, 5, 'Yes' or '', header_style5)
                        worksheet.write(line, 6, inv_data.number or '', header_style5)
                    else:
                        worksheet.write(line, 5, 'No' or '', header_style5)
                        worksheet.write(line, 6, inv_data.number or '', header_style5)
                worksheet.write(line, 7, rec.partner_id.prof_body_id or '', header_style5)
                worksheet.write(line, 8, rec.partner_id.prof_password or '', header_style5)
                worksheet.write(line, 9, rec.email or '', header_style5)
                worksheet.write(line, 10, rec.phone or '', header_style5)
                line += 1
            worksheet.write(line, 2, event_data.address_id and event_data.address_id.name or '', header_style5)
            worksheet.write(line, 3, event_data.date_begin or '', header_style5)
            """for rec in event_data.registration_ids:
                worksheet.write(line, 4, rec.state or '', header_style5)
                line+=1

            for rec in event_data.registration_ids:
                        worksheet.write(line, 5, rec.partner_id.prof_body_id or '', header_style5)
                        line+=1

            for rec in event_data.registration_ids:
                        worksheet.write(line, 6, rec.partner_id.prof_password or '', header_style5)
                        line+=1

                for rec in event_data.registration_ids:
                        worksheet.write(line, 7, rec.email or '', header_style5)
                        line+=1

                for rec in event_data.registration_ids:
                        worksheet.write(line, 8, rec.phone or '', header_style5)
                        line+=1"""

            line += 1
            i += 1

        wb.save(fp)
        out = base64.b64encode(fp.getvalue())
        data.update(
            {'name': 'VUE EXAM REPORT', 'res_model': 'event.event', 'datas': out, 'datas_fname': 'Vue Exam Report.xls'})
        attachment_id = self.env['ir.attachment'].create(data)

        email_to = 'pcexams@charterquest.co.za'  # partner_obj.read(cr,uid,rec,['email','email_1','name'])
        email_from = 'cqerp@charterquest.co.za'
        mail_vals = {
            'email_from': email_from,
            'email_to': email_to,
            'email_cc': 'patience.m@charterquest.co.za',
            'subject': 'PearsonVUE Exams Reports',
            'attachment_ids': [(6, 0, [attachment_id])],
            'body_html': '<p>Dear User, please find the attached report for VUE Exam.</p>',
        }

        res = self.env['mail.mail'].create(mail_vals)
        return True


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    def send_remittence_report(self):
        now = datetime.now()
        curr_month = now.month
        actual_invoices = []
        inv_obj = self.env['account.invoice']
        inv_ids = inv_obj.search([('fee_on_invoice', '=', True), ('paid_body', '=', False)])
        for rec in inv_ids:
            inv_obj_data = inv_obj.browse(rec)
            if inv_obj_data.payment_ids:
                for payments in inv_obj_data.payment_ids:
                    if datetime.strptime(str(payments.date_created),
                                         "%Y-%m-%d").month == curr_month and datetime.strptime(
                        str(payments.date_created), "%Y-%m-%d").year == now.year:
                        actual_invoices.append(rec)
        fp = StringIO()
        wb = xlwt.Workbook(encoding='utf-8')
        header_style2 = xlwt.easyxf(
            "font: bold on;align: horiz center; pattern: pattern solid, fore_colour white;")
        header_style3 = xlwt.easyxf(
            "font: bold on,height 260;align: horiz center; pattern: pattern solid, fore_colour white;")
        header_style4 = xlwt.easyxf(
            "font: bold on,height 200;align: horiz center; pattern: pattern solid, fore_colour ice_blue;")
        header_style5 = xlwt.easyxf(
            "font: bold off;align: horiz center; pattern: pattern solid, fore_colour white;")
        header_style6 = xlwt.easyxf(
            "font: bold on,height 260;align: horiz center; pattern: pattern solid, fore_colour gray25;")
        header_style7 = xlwt.easyxf(
            "font: bold off;align: horiz center; pattern: pattern solid, fore_colour light_green;")
        header_style8 = xlwt.easyxf(
            "font: bold off;align: horiz center; pattern: pattern solid, fore_colour orange;")

        final_arr_data = {}
        filename = 'Remittenece Report.xls'
        worksheet = wb.add_sheet("Remittence-Report" + ".xls")
        for i in range(0, 50):
            column = worksheet.col(i)
            column.width = 225 * 35

        worksheet.write(0, 0, "Partner Name", header_style4)
        worksheet.write(0, 1, "Invoice Date", header_style4)
        worksheet.write(0, 2, "Number", header_style4)
        worksheet.write(0, 3, "Balance", header_style4)
        worksheet.write(0, 4, "Total", header_style4)
        worksheet.write(0, 5, "Status", header_style4)
        worksheet.write(0, 6, "Paid Body", header_style4)
        worksheet.write(0, 7, "Prof. Body Login Password", header_style4)
        worksheet.write(0, 8, "Prof. Body Login Id", header_style4)
        worksheet.write(0, 9, "Payment Reference", header_style4)

        line = 1
        i = 1
        data = {}

        for item in actual_invoices:
            inv_data = inv_obj.browse(item)
            # if lead_data.type == "lead":
            worksheet.write(line, 0, inv_data.partner_id.name or '', header_style5)
            worksheet.write(line, 1, inv_data.date_invoice or '', header_style5)
            worksheet.write(line, 2, inv_data.number or '', header_style5)
            worksheet.write(line, 3, inv_data.residual or 0.0, header_style5)
            worksheet.write(line, 4, inv_data.amount_total or 0.0, header_style5)
            worksheet.write(line, 5, inv_data.state or '', header_style5)
            if inv_data.paid_body:
                worksheet.write(line, 6, 'Yes', header_style5)
            else:
                worksheet.write(line, 6, 'No', header_style5)
            worksheet.write(line, 7, inv_data.partner_id.prof_password or '', header_style5)
            worksheet.write(line, 8, inv_data.partner_id.prof_body_id or '', header_style5)
            worksheet.write(line, 9, inv_data.reference_type or '', header_style5)
            line += 1
        i += 1

        wb.save(fp)
        out = base64.b64encode(fp.getvalue())
        # print kk
        data.update({'name': 'Remittence Report', 'res_model': 'account.invoice', 'datas': out,
                     'datas_fname': 'Remittenece Report.xls'})
        attachment_id = self.env['ir.attachment'].create(data)

        email_to = 'accounts@charterquest.co.za'  # partner_obj.read(cr,uid,rec,['email','email_1','name'])
        email_from = 'cqerp@charterquest.co.za'
        mail_vals = {
            'email_from': email_from,
            'email_to': email_to,
            'email_cc': 'patience.m@charterquest.co.za',
            'subject': 'Remittence Reports',
            'attachment_ids': [(6, 0, [attachment_id])],
            'body_html': '<p>Dear User, please find the attached report for Remittence.</p>',
        }

        res = self.env['mail.mail'].create(mail_vals)
        return True


class stock_quant(models.Model):
    _inherit = 'stock.quant'


def send_monthly_stock_report(self):
    all_locations = []

    quant_obj = self.env['stock.quant']
    bc_stock_id = self.env['stock.location'].search([
        ('complete_name', '=', 'Physical Locations / BC / Stock')])
    if bc_stock_id:
        all_locations.append(bc_stock_id)
    pc_stock_id = self.env['stock.location'].search([('complete_name', '=', 'Physical Locations / Stock')])
    if pc_stock_id:
        all_locations.append(pc_stock_id)
    sc_stock_id = self.env['stock.location'].search([
        ('complete_name', '=', 'Physical Locations / SC / Stock')])
    if sc_stock_id:
        all_locations.append(sc_stock_id)
    wh_stock_id = self.env['stock.location'].search([
        ('complete_name', '=', 'Physical Locations / CharterQuest / Stock')])
    if wh_stock_id:
        all_locations.append(wh_stock_id)
    attachments = []

    for data in all_locations:
        quant_ids = quant_obj.search([('location_id', 'in', data)])
        # print quant_ids,'quant idssssssssssssssss'
        location_data = self.env['stock.location'].browse(data)
        fp = StringIO()
        wb = xlwt.Workbook(encoding='utf-8')
        header_style2 = xlwt.easyxf(
            "font: bold on;align: horiz center; pattern: pattern solid, fore_colour white;")
        header_style3 = xlwt.easyxf(
            "font: bold on,height 260;align: horiz center; pattern: pattern solid, fore_colour white;")
        header_style4 = xlwt.easyxf(
            "font: bold on,height 200;align: horiz center; pattern: pattern solid, fore_colour ice_blue;")
        header_style5 = xlwt.easyxf(
            "font: bold off;align: horiz center; pattern: pattern solid, fore_colour white;")
        header_style6 = xlwt.easyxf(
            "font: bold on,height 260;align: horiz center; pattern: pattern solid, fore_colour gray25;")
        header_style7 = xlwt.easyxf(
            "font: bold off;align: horiz center; pattern: pattern solid, fore_colour light_green;")
        header_style8 = xlwt.easyxf(
            "font: bold off;align: horiz center; pattern: pattern solid, fore_colour orange;")

        final_arr_data = {}
        r = location_data.complete_name.split('/')
        file_name = [''.join(r[0:-1])][0].rstrip()

        if file_name == 'Physical Locations  BC':
            file_name = 'Parktown Campus'
        elif file_name == 'Physical Locations  SC':
            file_name = 'Sandton Campus'
        elif file_name == 'Physical Locations':
            file_name = 'Pretoria Campus'
        elif file_name == 'Physical Locations  CharterQuest':
            file_name = 'CharterQuest (Randburg)'
        # file_name = file_name.rstrip()
        filename = file_name + '-' + 'Report.xls'
        worksheet = wb.add_sheet(str(filename))
        for i in range(0, 50):
            column = worksheet.col(i)
            column.width = 225 * 35

        worksheet.write(0, 0, "Product Name", header_style4)
        worksheet.write(0, 1, "Quantity", header_style4)
        worksheet.write(0, 2, "Public Category", header_style4)

        line = 1
        i = 1
        data = {}

        for item in quant_ids:
            quant_data = quant_obj.browse(item)
            # if lead_data.type == "lead":
            worksheet.write(line, 0, quant_data.product_id.name or '', header_style5)
            worksheet.write(line, 1, quant_data.qty or '', header_style5)
            if quant_data.product_id.public_categ_ids:
                for rec in quant_data.product_id.public_categ_ids:
                    worksheet.write(line, 2, rec.name or '', header_style5)
                    line += 1
            line += 1
        i += 1
        wb.save(fp)
        out = base64.b64encode(fp.getvalue())
        # print kk
        data.update({'name': str(file_name), 'res_model': 'stock.quant', 'datas': out,
                     'datas_fname': str(file_name) + '-' + '.xls'})
        attachment_id = self.env['ir.attachment'].create(data)
        attachments.append(attachment_id)

    email_to = 'bookstores@charterquest.co.za'  # partner_obj.read(cr,uid,rec,['email','email_1','name'])
    email_from = 'cqerp@charterquest.co.za'
    mail_vals = {
        'email_from': email_from,
        'email_to': email_to,
        'email_cc': 'patience.m@charterquest.co.za',
        'subject': 'Monthly Stock Report',
        'attachment_ids': [(6, 0, attachments)],
        'body_html': '<p>Dear User, please find the attached report for Monthly Stock.</p>',
    }

    res = self.env['mail.mail'].create(mail_vals)
    return True
