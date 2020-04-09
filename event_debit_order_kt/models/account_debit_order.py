# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
import base64
import csv
import odoo.addons.decimal_precision as dp
import os


class exported_debit_order_file(models.Model):
    _name = 'exported.debit.order.file'

    name = fields.Char(string="Name", size=56)
    date = fields.Date(string="Date")
    file = fields.Binary(string="FNB Upload File")
    hash_file_name = fields.Char(string="Hash file", size=56)
    hash_file = fields.Binary(string="Hash file")
    generation_number = fields.Integer(string="File Generation Number")
    action_date = fields.Date(string="Action Date")
    no_of_transactions = fields.Integer(string="No. of Transactions")
    transactions_amount_total = fields.Float(string="Transactions Total Amount")
    installation_generation_number = fields.Char(string="Installation Generation Number")
    user_generation_number = fields.Char(string="User Generation Number")
    hash_total = fields.Float(string="Hash Total")
    type = fields.Selection([('manual_fnb_upload', 'Manual FNB Upload'),
                             ('auto_fnb_upload', 'Auto FNB Upload')], string='Type', default='manual_fnb_upload')
    loaded_to_fnb = fields.Boolean(string='Loaded To FNB?')

    @api.multi
    def get_debit_orders(self):
        action_date_record = self.env['debit.order.details'].search([('dbo_date', '=', self.action_date)]).ids
        return {
            'name': 'Debit Orders',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'debit.order.details',
            'target': 'new',
            'domain': [('id', 'in', action_date_record)]
        }

    @api.model
    def generate_fnb_integration_csv(self):
        todaydate = date.today()
        action_date = todaydate + timedelta(days=2)
        Filename = str(action_date) + '-' + 'Manual FNB Upload' + '.csv'
        dirpath = os.getcwd()
        filepath = os.path.join(dirpath, Filename)
        fnb = open(filepath, 'wt')
        writer = csv.writer(fnb)
        writer.writerow(['BinSol – U ver 1.00'])
        writer.writerow([action_date])
        writer.writerow(['62328257060'])
        writer.writerow(('RECIPIENT NAME', 'RECIPIENT ACCOUNT', 'RECIPIENT ACCOUNT TYPE', 'BRANCHCODE', 'AMOUNT',
                         'OWN REFERENCE', 'RECIPIENT REFERENCE'))
        do_ids = self.env['debit.order.details'].search([('dbo_date', '=', str(action_date)),
                                                         ('state', '=', 'pending')])
        count = 0
        total = 0.0
        for obj in do_ids:
            if obj.invoice_id:
                date1 = datetime.strptime(obj.dbo_date, '%Y-%m-%d')
                date2 = date1 and str(date1.strftime('%y')) + '' + str(date1.strftime('%m')) + '' + str(
                    date1.strftime('%d'))
                account_type = ''
                if obj.bank_acc_type == 'Cheque':
                    account_type = 1
                if obj.bank_acc_type == 'Savings':
                    account_type = 2
                ownreference = ''
                if str(obj.name).find('/') > -1:
                    reference = str(obj.name).split('/')
                    cqreference = reference[2] and str(reference[2]).replace('-', '').ljust(14, ' ')
                    ownreference = "CHARTERQUE" + '' + cqreference + '' + date2
                count += 1
                total = total + obj.dbo_amount
                writer.writerow((obj.acc_holder, obj.bank_acc_no, account_type, obj.bank_code, obj.dbo_amount,
                                 ownreference, ownreference))
                obj.write({
                    'state': 'inprogress'
                })
        fnb.close()
        out = open(filepath, 'rt').read()
        out = base64.encodestring(out.encode())
        final_arr_data = {}
        final_arr_data['file'] = out
        final_arr_data['date'] = datetime.now()
        final_arr_data['name'] = Filename
        final_arr_data['action_date'] = action_date
        final_arr_data['no_of_transactions'] = count
        final_arr_data['transactions_amount_total'] = total
        pl_report_id = self.env['exported.debit.order.file'].create(final_arr_data)
        mail_mail_obj = self.env['mail.mail']
        email_cc = 'accounts@charterquest.co.za' + ',' + 'desmond.f@charterquest.co.za' + ',' + 'patience.m@charterquest.co.za'
        from_add = 'debitorders@charterquest.co.za'
        To = 'vnti@charterquest.co.za'
        CC = email_cc
        dic = {
            'type': 'binary',
            'datas': out,
            'name': Filename,
            'datas_fname': Filename,
            'res_model': 'exported.debit.order.file',
        }
        document_id = self.env['ir.attachment'].create(dic)
        subject_name = 'Student Debit Orders for ' + str(action_date) + ' to be loaded' + '(' + str(
            count) + 'Transactions )' + '-' + 'Value' + str(total)
        body_html = ("""<p><br>
                        Dear Valentine,<br>
                        Please find attached FNB Manual Debit Order csv file for DebitOrders that should go off on %s.<br>
                        Please remember to upload this file to FNB.<br>
                        Regards,<br>
                        CQERP<br>
                        Should you encounter any issues please contact Strategic Dimensions on <a href="support@strategicdimensions.co.za">support@strategicdimensions.co.za</a><br>                                    
                        </p>
                    """) % (str(action_date))
        mail_mail_id = mail_mail_obj.create({
            'subject': subject_name,
            'email_from': from_add,
            'email_to': To,
            'email_cc': CC,
            'body_html': body_html,
            'attachment_ids': [(6, 0, [document_id.id])]
        })
        if mail_mail_id:
            mail_mail_id.send()
        do_ids.write({
            'debit_order_batchname': Filename,
            'debit_order_batch': out
        })
        email = self.env.ref('event_debit_order_kt.email_template_edi_debit_order_scheduled')
        for each in do_ids:
            email.send_mail(each.id)
        try:
            if os.path.isfile(filepath):
                os.unlink(filepath)
        except Exception as e:
            pass


class debit_order_details(models.Model):
    _name = "debit.order.details"

    _description = "Debit Order"
    _inherit = ['mail.thread']

    name = fields.Char(string='Order Reference', size=64, readonly=1, default='/')
    partner_id = fields.Many2one('res.partner', string="Student Name")
    dbo_amount = fields.Float(string='Debit Order Amount', digits=dp.get_precision('Account'))
    course_fee = fields.Float(string='Fee (Less Interest)')
    interest = fields.Float(string='Interest')
    dbo_date = fields.Date(string='Debit Order Date')
    acc_holder = fields.Char(string='Account Holder Name')
    bank_name = fields.Many2one('res.bank', string='Bank Name')
    bank_acc_no = fields.Char(string='Bank Account No', size=54)
    bank_code = fields.Char(string='Bank Code', size=54)
    bank_type_id = fields.Many2one('res.bank.type', string="Bank Type")
    bank_acc_type = fields.Selection([('Cheque', 'Cheque'), ('Bank', 'Bank'), ('Savings', 'Savings'),('Cash','Cash')],
                                     string='Bank Account Type')
    sale_id = fields.Many2one('sale.order', string="Sale order")
    invoice_id = fields.Many2one('account.invoice', string='Invoice No')
    state = fields.Selection([('pending', 'Pending'),
                              ('inprogress', 'In Process'),
                              ('done', 'Successful'),
                              ('failed', 'Failed'),
                              ('cancelled', "Cancelled"),
                              ('under_review', 'Under Review')], string='Debit Order Status')
    debit_order_batch = fields.Binary(string="Debit Order Batch File")
    debit_order_batchname = fields.Char(string="Batch File Name", size=64)
    student_number = fields.Char(string='Student No', size=64)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Debit Order Reference must be unique!'),
    ]

    @api.model
    def get_debit_order_status_successful(self):
        todaydate = date.today()
        action_date = todaydate - timedelta(days=7)
        do_ids = self.env['debit.order.details'].search([('dbo_date', '=', str(action_date)),
                                                         ('state', '=', 'inprogress')])
        for do_id in do_ids:
            do_id.write({'state': 'done'})
        return True

    def register_payment_debit(self):
        if self.invoice_id:
            account_invoice = self.invoice_id
            if account_invoice.state != 'paid':
                journal_id = self.env['account.journal'].search([('code', '=', 'CSH1')], limit=1)
                payment_methods = journal_id.inbound_payment_method_ids or journal_id.outbound_payment_method_ids
                payment_id = self.env['account.payment'].sudo().create({
                    'partner_id': self.partner_id.id,
                    'amount': self.dbo_amount,
                    'payment_type': 'inbound',
                    'partner_type': 'customer',
                    'invoice_ids': [(6, 0, account_invoice.ids)],
                    'payment_date': datetime.today(),
                    'journal_id': journal_id.id,
                    'payment_method_id': payment_methods[0].id if payment_methods else False
                })
                # payment_id.action_validate_invoice_payment()
                payment_id.post()
                pdf_data = self.env.ref(
                    'event_price_kt.report_statement_enrollment').sudo().render_qweb_pdf(
                    self.invoice_id.id)
                strname = 'Debit Order Statement'
                pdfname = 'debit_order_statement.pdf'
                if pdf_data:
                    pdfvals = {'name': strname,
                               'db_datas': base64.b64encode(pdf_data[0]),
                               'datas': base64.b64encode(pdf_data[0]),
                               'datas_fname': pdfname,
                               'res_model': self._name,
                               'type': 'binary'}
                attachment = self.env['ir.attachment'].create(pdfvals)
                email = self.env.ref('event_debit_order_kt.email_template_edi_enrolement_statement_student')
                mail_compose_id = self.env['mail.compose.message'].sudo().generate_email_for_composer(
                    email.id, self.id)
                mail_compose_id.update({'email_to': self.partner_id.email})
                mail_values = {
                    'email_from': mail_compose_id.get('email_from'),
                    'email_to': mail_compose_id.get('email_to'),
                    'email_cc': email.email_cc,
                    'subject': mail_compose_id.get('subject'),
                    'body_html': mail_compose_id.get('body'),
                    'attachment_ids': [(6, 0, [attachment.id])],
                    'auto_delete': True,
                }
                msg_id = self.env['mail.mail'].create(mail_values)
                msg_id.send()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        ids = []
        if context and context.get('search_default_dbo_date', False):
            args.append(['dbo_date', '=', context['search_default_dbo_date']])
        res = super(debit_order_details, self).search(args=args, offset=offset, limit=limit, order=order,
                                                      count=count)
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('debit.order.details') or _('New')
        inv_ref = False
        if 'invoice_id' in vals.keys():
            invoice_id = vals['invoice_id']
            inv_ref = self.env['account.invoice'].browse(invoice_id)
        if inv_ref:
            if inv_ref.number:
                vals['name'] = inv_ref.number + "-" + vals['name']
        return super(debit_order_details, self).create(vals)

    @api.model
    def send_debit_order_emails(self):
        today = date.today()
        debit_order_ids = self.search([('state', '=', 'pending')])
        for record in debit_order_ids:
            if record.dbo_date and record.invoice_id:
                dbo_date = (record.dbo_date).split('-')
                two_days_before = date(day=int(dbo_date[2]), month=int(dbo_date[1]), year=int(dbo_date[0])) + timedelta(
                    days=-2)
                if today == two_days_before:
                    email = self.env.ref('event_debit_order_kt.email_template_edi_invoice')
                    email.send_mail(record.id.id)
            return True

    @api.model
    def failed_debit_order_notification(self):
        mail_obj = self.env['mail.mail']
        for partner in self.env['res.partner'].search([]):
            debit_order_ids = self.search([('partner_id', '=', partner.id),
                                           ('state', '=', 'failed')])
            if debit_order_ids:
                header_body = ('''
                             Dear %s <br>
                             Your debit order signed with CharterQuest returned as follows: <br>
                             <br>
                             <br>
                            ''') % (partner.name)

                body_html = '''
                        <table  padding:30px; border='1' font-color='white' >
                            <tr bgcolor='black' border='1' font-color='white'>
                                <td>
                                Action Date/Month
                                </td>
                                <td>
                                D/O reference no.
                                </td>
                                <td>
                                Amount
                                </td>
                                <td>
                                Penalty Charge
                                </td>
                                <td>
                                Cumulative balance owing
                                </td>
                                <td>
                                Return status
                                </td>
                                <td>
                                Action required
                                </td>
                            </tr>

                    '''
                for debit in debit_order_ids:
                    body_html += ("""
                                    <tr>
                                        <td>
                                                %s
                                        </td>
                                        <td>
                                                %s
                                        </td>
                                        <td>
                                                %s
                                        </td>
                                        <td>
                                        Penalty Charge
                                        </td>
                                        <td>
                                        Cumulative balance owing
                                        </td>
                                        <td>
                                        Return status
                                        </td>
                                        <td>
                                        Action required
                                        </td>
                                    </tr>

                               """) % (debit.dbo_date, debit.name, debit.dbo_amount)
                rest_of_body = (u"""
                        </table>
                        <br>
                        <br>
                        Please kindly effect an immediate deposit/EFT/transfer for amount/s shown in the cumulative balance owing column, as above, using the assigned D/O reference number/s and send proof of payment to accounts@charterquest.co.za.
                        Should we not hear from you in 3 days, we will rerun the debit order for the cumulative balance amount. A second failure may lead to some or all of the following steps:<br>
                        1.            Curtailment of our services to you<br>
                        2.            Update our monthly submissions about your payment behavior/pattern to your professional body<br>
                        3.            Update our credit bureau backlist with your personal payment records<br>
                        4.            Forward this to our legal department to secure a default judgment against you <br>
                        <br>
                        As you are aware, credit checks and your standing with your professional body have become vital background check requirements for future jobs you may apply for, let alone future credit applications with credit institutions.
                        It is for this reason we are extremely reluctant to pursue any of the above steps as we know the implications for your future career could be far reaching. Furthermore, we will like to see you return to CharterQuest where your best chance of achieving your chartered designation lies.
                        For any queries or further assistance, please contact us immediately. <br>
                        Desmond B. Fosang <br>
                        <br>
                        Student Accounting Services <br>
                        CHARTERQUEST FINANCIAL TRAINING INSTITUTE <br>
                        Email: accounts@charterquest.co.za | desmond.f@charterquest.co.za <br>
                        Tel.: +27 (0)11 791 3014 <br>
                        <br>
                        <br>
                        SANDTON CAMPUS: <br>
                        <br>
                        CHARTERQUEST FINANCIAL TRAINING INSTITUTE <br>
                        @ CHARTERQUEST HOUSE, <br>
                        Metropolitan Park <br>
                        374 Rivonia Boulevard <br>
                        Rivonia, SANDTON <br>
                        South Africa <br>
                        <br>
                        CONTACT INFORMATION: <br>
                        Tel: +27 (0)11 234 9223 [SA & Intl] <br>
                        Tel: +27 (0)11 234 9238 [SA & Intl] <br>
                        Tel: 0861 131 137 [SA ONLY] <br>
                        Fax: 086 218 8713 [SA ONLY] <br>
                        Email:enquiries@charterquest.co.za <br>
                        <br>
                        <br>
                        BRAAMFONTEIN CAMPUS:<br>
                         <br>
                        CHARTERQUEST FINANCIAL TRAINING INSTITUTE <br>
                        @ ORION HOUSE, <br>
                        [13th floor] 49 Jorissen Street <br>
                        Cnr Biccard and Jorissen Street <br>
                        BRAAMFONTEIN <br>
                        South Africa <br>
                         <br>
                        CONTACT INFORMATION: <br>
                        Tel: +27 [0]11 403 0656 [A & Intl] <br>
                        Tel: +27 [0]11 403 0642 [SA & Intl] <br>
                        Fax: 086 218 8713 [SA ONLY] <br>
                        Fax: +27 [0]11 791 7703 [SA & Intl] <br>
                        Email:enquiries@charterquest.co.za <br>
                        PRETORIA CAMPUS: <br>
                        <br>
                        CHARTERQUEST FINANCIAL TRAINING INSTITUTE <br>
                        367 Hilda Street <br>
                        Hatfield Rendez Vous Building <br>
                        Hatfield, PRETORIA <br>
                        South Africa <br>
                        <br>
                        CONTACT INFORMATION: <br>
                        Tel: +27 [0]12 751 7608 [SA & Intl] <br>
                        Email: enquiries@charterquest.co.za <br>
                        <br> """)
                body = header_body + body_html + rest_of_body
                mail_mail_id = mail_obj.create({
                    'subject': "Failed Debit order Notification",
                    'email_from': 'debitorders@charterquest.co.za',
                    'email_to': partner.email,
                    'body_html': body,
                })
                if mail_mail_id:
                    mail_mail_id.send()
            return True

    @api.multi
    def write(self, vals):
        result = super(debit_order_details, self).write(vals)
        print("\n\n\\n\n\n\n============vals=======",vals)
        if vals.get('state', False):
            if vals['state'] == 'failed':
                for each in self:
                    each.failed_debit_order_notification()
        if vals.get('state') and vals.get('state') == 'done':
            for each in self:
                print("\n\n\n\n============each=====",each)
                each.register_payment_debit()
        return result


class debit_order_mandate(models.Model):
    _name = 'debit.order.mandate'

    partner_id = fields.Many2one('res.partner', "Student Name")
    dbo_amount = fields.Float('Debit Order Amount')
    course_fee = fields.Float('Fee (Less Interest)')
    interest = fields.Float('Interest')
    dbo_date = fields.Date('Debit Order Date')
    acc_holder = fields.Char('Account Holder Name')
    bank_name = fields.Many2one('res.bank', 'Bank Name')
    bank_acc_no = fields.Char('Bank Account No', size=54)
    bank_code = fields.Char('Bank Code', size=54)
    bank_type_id = fields.Many2one('res.bank.type', size=54)
    sale_id = fields.Many2one('sale.order', "Sale Order")
    months = fields.Integer('Months')


class ResBankType(models.Model):
    _name = "res.bank.type"

    name = fields.Char(string="Account Type")
