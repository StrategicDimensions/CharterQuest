import hashlib

from odoo import models,fields, api, _
import re
import datetime
from datetime import timedelta
from datetime import date,datetime,timedelta
from dateutil.relativedelta import relativedelta
import random
import base64
import urllib
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import netsvc
# from openerp.report import render_report


class mail_mail(models.Model):
    _inherit = "mail.mail"
    
    @api.model
    def create(self, val):
        if val.get('body_html', False):
            match = re.search("<span>Invoice validated.*", val['body_html'])
            if match:
                val['recipient_ids'] = []
            match1 = re.search("<span>Invoice paid</span>.*", val['body_html'])
            if match1:
                val['recipient_ids'] = []
        res = super(mail_mail,self).create(val)
        return res

class pcexams_voucher(models.Model):
    _inherit = 'pcexams.voucher'
    _description = 'PCExams Vocuher'
    _order = 'id desc'

    invoice_id = fields.Many2one('account.invoice', string='Invoice')

    
class account_invoice(models.Model):
    _inherit = "account.invoice"

    debit_order_entry = fields.One2many('debit.order.details', 'invoice_id',string="Debit Order Entry")
    debit_order_mandate = fields.Boolean('Debit Order Mandate Submitted')
    student_number = fields.Char(string='Student No', size=64)
    to_review = fields.Boolean(string='To Review')
    pcexam_voucher_ids = fields.One2many('pcexams.voucher', 'invoice_id', string='PC Exam Vouchers')
    redeemed_voucher_ids = fields.One2many('pcexams.voucher','redeemed_invoice',string='Redeemed Vouchers')
    is_recent = fields.Boolean("Is Recent")
    voucher_send = fields.Boolean("Voucher Send")
    additional_payment = fields.Boolean("Additional Payment")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.update({'student_number': self.partner_id.student_number})

    @api.model
    def create(self, vals):
        if vals.get('partner_id', False):
            partner_obj = self.env['res.partner'].browse(vals['partner_id'])
            stud_no = partner_obj.student_number
            vals['student_number'] = stud_no
            vals.update({'is_recent': True,
                         'voucher_send':False,
                         'additional_payment':False})
        return super(account_invoice, self).create(vals)

    @api.multi
    def write(self, vals):
        # result =  super(account_invoice, self).write(cr, uid, ids, vals, context=context)
        if vals.get('state') == 'paid' and self.quote_type == 'PC Exam':
            attachment_list = []
            online_registration = []
            event_list = []
            sale_order_id = self.env['sale.order'].sudo().search([('name','=',self.sale_order_id.name)])
            if sale_order_id:



                for exam in sale_order_id.order_line:
                    exam_dict = {}
                    event = self.env['event.event'].search([('id','=',exam.event_id.id),('name','=',exam.event_id.name),('type_pc_exam','=',sale_order_id.pc_exam_type.id)])
                    if event:
                        online_registration.append([0, 0, {'event_id': exam.event_id.name,
                                                           'partner_id': self.partner_id.id,
                                                           'email': self.partner_id.email
                                                           }])
                        quote_name = "SO{0}WEB".format(str(sale_order_id.id).zfill(3))

                        m = hashlib.md5(quote_name.encode())
                        decoded_quote_name = m.hexdigest()
                        config_para = self.env['ir.config_parameter'].sudo().search(
                            [('key', 'ilike', 'web.base.url')])
                        if config_para:
                            link = config_para.value + "/reschedulePB/" + decoded_quote_name
                            sale_order_id.write({'debit_link': decoded_quote_name})
                        print("\n\n\n\n\n\n========link======",link,exam.event_id,type(exam.event_id.date_begin))
                        start_date = datetime.strptime(exam.event_id.date_begin,
                                                               DEFAULT_SERVER_DATETIME_FORMAT)
                        exam_start_date = (start_date + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
                        end_date = datetime.strptime(exam.event_id.date_end,
                                                                DEFAULT_SERVER_DATETIME_FORMAT)
                        exam_end_date = (end_date + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
                        print("\n\n\n\n\n\n========start_date======", start_date)
                        exam.event_id.write({'online_registration_ids': online_registration})
                        exam_dict['subject_name'] = exam.event_id.name
                        exam_dict['start_time'] = exam_start_date
                        exam_dict['end_time'] = exam_end_date
                        exam_dict['campus'] = sale_order_id.campus.name
                        link += '&%s' % (exam.event_id.id)
                        exam_dict['link'] = link
                        event_list.append(exam_dict)
                        print("\n\n\n\n\n\n========event_list======", event_list)
            template_id = self.env.ref('cfo_snr_jnr.email_template_payvia_credit_card',
                                          raise_if_not_found=False)
            if template_id:
                template_id.sudo().with_context(
                    # email_to=each_request.get('email'),
                    event_list=event_list,
                    email_cc='pcexams@charterquest.co.za',
                    # reschedule_link=link,
                    prof_body=self.prof_body.name,
                ).send_mail(sale_order_id.id, force_send=True)

            template_invoice_id = self.env.ref('cfo_snr_jnr.email_template_pcexam_confirm',
                                                  raise_if_not_found=False)
            if template_invoice_id:
                    pdf_data_order = self.env.ref(
                        'event_price_kt.report_invoice_pcexam').sudo().render_qweb_pdf(self.id)
                    if pdf_data_order:
                        pdfvals = {'name': 'Invoice Report',
                                   'db_datas': base64.b64encode(pdf_data_order[0]),
                                   'datas': base64.b64encode(pdf_data_order[0]),
                                   'datas_fname': 'Invoice Report.pdf',
                                   'res_model': 'account.invoice',
                                   'type': 'binary'}
                        pdf_create = self.env['ir.attachment'].sudo().create(pdfvals)
                        attachment_list.append(pdf_create)
                    agreement_id = self.env.ref('cfo_snr_jnr.pc_exam_data_pdf')
                    if agreement_id:
                        attachment_list.append(agreement_id)

            template_invoice_id.sudo().write(
                {'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])]})
            template_invoice_id.sudo().with_context(
                # email_to=each_request.get('email'),
                # event_list=event_list,
                email_cc= 'pcexams@charterquest.co.za;accounts@charterquest.co.za',
                # prof_body=invoice_id.prof_body.name,
            ).send_mail(self.id, force_send=True)

        if vals.get('state', False) and vals['state'] == 'paid':
             for invoice_line in self.invoice_line_ids:
                 if invoice_line.pcexam_voucher_id:
                     voucher_values = {'status': 'Redeemed', 'redeemed_invoice': self.id}
                     invoice_line.pcexam_voucher_id.write(voucher_values)
        #template_id = self.pool.get('email.template').search(cr,uid,[('name','=',"Sending Tax Invoice to Student")])
             #if template_id:
             #	mail_message = self.pool.get('email.template').send_mail(cr,uid,template_id[0],ids[0])
        if self.payment_ids and not self.pcexam_voucher_ids:

            mail_mail_obj = self.env['mail.mail']
            mail_vals = {}
            for invoice_line in self.invoice_line_ids:
                if invoice_line.product_id and invoice_line.product_id.event_feetype_rem and invoice_line.product_id.event_feetype_rem.name =='Exam Fees' and invoice_line.product_id.pcexam_voucher == True:
                    mail_server_obj = self.env['ir.mail_server']
                    mail_message_obj = self.env['mail.message']
                    mail_mail_obj = self.env['mail.mail']
                    from_add = 'accounts@charterquest.co.za'
                    To = self.partner_id.email
                    document_ids = []
                    voucher_lis = []
                    print("\n\n\n\n\n\n=======voucher no====",invoice_line.product_id.no_vouchers,invoice_line.product_id.name)
                    for i in range(0, invoice_line.product_id.no_vouchers):
                        pcexam_voucher = {
                                           'voucher_no':'CHQ'+str(random.randint(10000,99999)),
                                           'student_id':self.partner_id and self.partner_id.id,
                                           'invoice_id':self.id,
                                           'create_date':self.date_invoice,
                                           'expiry_date':datetime.now()+relativedelta(days=182),
                                           'voucher_value':invoice_line.product_id.voucher_value,
                                           'prof_body':self.prof_body and self.prof_body.id,
                                           'qualification_id':invoice_line.product_id.event_qual_rem and invoice_line.product_id.event_qual_rem.id,
                                           'campus_id':self.campus and self.campus.id,
                                           'status':'Issued',
                                        }
                        voucher_lis.append(pcexam_voucher)
                        print("\n\n\n\n\n\n=============voucher_lis===========",voucher_lis)
                    if self.payment_ids and self.is_recent:
                        # voucher_lis.append(pcexam_voucher)
                        for i in voucher_lis:
                            voucher_id = self.env['pcexams.voucher'].create(i)
                    else:
                        voucher_lis = []
                        voucher_id = []
                        if voucher_id:
                                # report = self.env.ref('sale.action_report_quote')
                                report_name = 'event_price_kt.pcexam_voucher_report'
                                ret_file_name = 'pcexam_voucher_'+str(pcexam_voucher['voucher_no'])+'.pdf'
                                result, format = report_name.with_context([voucher_id], report_name, {}, context=None)
                                result = base64.b64encode(result)
                                dic4 = {
                                    'type': 'binary',
                                    'datas': result,
                                    'name': ret_file_name,
                                    'datas_fname': ret_file_name,
                                    'res_model': 'pcexams.voucher',
                                    }
                                document_id = self.env['ir.attachment'].create(dic4)
                                document_ids.append(document_id)

            # if self.payment_ids and not self.debit_order_entry:
            #     print("\n\n\n\n\n\n\n\=======dbfebfjsdbfjwebfkjewfjwebfj=============")
            #     if self.sale_order_id and self.sale_order_id.debit_order_mandat:
            #         debitorder = self.sale_order_id.debit_order_mandat
            #         debitorder_date = debitorder.dbo_date
            #         for i in range(0, int(debitorder.months)):
            #             debit_order = {
            #                 'partner_id': self.partner_id and self.partner_id.id,
            #                 'dbo_amount': float(debitorder.dbo_amount) / int(debitorder.months),
            #                 'course_fee': float(debitorder.course_fee) / int(debitorder.months),
            #                 'interest': float(debitorder.interest) / int(debitorder.months),
            #                 'dbo_date': debitorder_date,
            #                 'acc_holder': debitorder.acc_holder,
            #                 'bank_name': debitorder.bank_name and debitorder.bank_name.id,
            #                 'bank_acc_no': debitorder.bank_acc_no,
            #                 'bank_code': debitorder.bank_code,
            #                 'bank_acc_type': debitorder.bank_type_id.name,
            #                 'state': 'pending',
            #                 'sale_id': self.sale_order_id.id,
            #                 'invoice_id': self.id
            #             }
            #             debitorder_date = datetime.strptime(str(debitorder_date), "%Y-%m-%d").date() + relativedelta(
            #                 months=1)
            #             self.env['debit.order.details'].create(debit_order)

        voucher_body = ""
        if self.pcexam_voucher_ids and vals.get('state') == 'paid' and self.voucher_send == False:
            mail_mail_obj = self.env['mail.mail']
            mail_vals = {}
            voucher_lst=[]

            print("\n\n\n\n\n\n\n===========mail===============", vals.get('state'))
            # table_head = (u"""<table cellspacing="0" cellpadding="0" border="0" style="border-collapse:collapse;text-align:center;" class="MsoNormalTable">
            #                     <tbody>
            #                     <tr>
            #                     <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt;font-weight:bold;">Voucher No</td>
            #                     <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt;font-weight:bold;">Expiry Date</td>
            #                     <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt;font-weight:bold;">Voucher Value</td>
            #                     <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt;font-weight:bold;">Invoice No</td>
            #                     <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt;font-weight:bold;">Prof Body</td>
            #                     <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt;font-weight:bold;">Level</td>
            #                     <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt;font-weight:bold;">Status</td>
            #                     </tr>""")
            for voucher in self.pcexam_voucher_ids:
                voucher_vals = {}
                voucher_vals['voucher_no'] = voucher.voucher_no
                voucher_vals['expiry_date'] = voucher.expiry_date
                voucher_vals['voucher_value'] = "R" + str(voucher.voucher_value)
                voucher_vals['profes_body'] = voucher.prof_body.name
                voucher_vals['qual'] = voucher.qualification_id.name
                voucher_vals['status'] = voucher.status
                voucher_vals['invoice'] = str(self.number)
                voucher_lst.append(voucher_vals)
                # profes_body = voucher.prof_body.name
                # qual = voucher.qualification_id.name
                # table_body = (u"""<tr>
                #                 <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">%s</td>
                #                 <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">%s</td>
                #                 <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">%s</td>
                #                 <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">%s</td>
                #                 <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">%s</td>
                #                 <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">%s</td>
                #                 <td width="302" valign="top" style="width:226.4pt;border:solid windowtext 1.0pt;padding:0cm 5.4pt 0cm 5.4pt">%s</td>
                #                 </tr>
                #                 """) % (
                # voucher.voucher_no, voucher.expiry_date, "R" + str(voucher.voucher_value), str(self.number),
                # str(profes_body), str(qual), voucher['status'])

            #     voucher_body += table_body
            # voucher_body = voucher_body + (u"""</tbody></table>""")
            # result_body = table_head + voucher_body
            # email_to = self.partner_id.email
            # mail_vals = {
            #     'email_from': 'accounts@charterquest.co.za',
            #     'email_to': email_to,
            #     'email_cc': 'enquiries@charterquest.co.za;accounts@charterquest.co.za',
            #     'subject': 'PC Exam Voucher',
            #     'body_html': u'''Dear %s,<br/><br/>Thank you for registering with CharterQuest.This email contains PC Exams Vouchers to book your exams when you are ready to write.<br/><br/>%s<br/>
            #                 Keep your vouchers safe as they are non-refundable, non exchangeable and non-replaceable.<br/><br/>
            #                 Here is the booking link : <a href = "http://pcexams.charterquest.co.za">http://pcexams.charterquest.co.za</a><br/><br/>
            #                 Please contact email : <b>pcexams@charterquest.co.za</b> for any further assistance.<br/><br/>
            #                 Thanking You<br/>
            #                 Patience Mukondwa<br/>
            #                 Head of Operations<br/>
            #                 The CharterQuest Institute<br/>
            #                 <br/><br/>
            #                 CENTRAL CONTACT INFORMATION:<br/>
            #                 Tel : +27 (0)11 234 9223[SA &amp; Intl]<br/>
            #                                         Tel : +27 (0)11 234 9238[SA &amp; Intl]<br/>
            #                                         Tel : 0861 131 137[SA ONLY]<br/>
            #                 Tel : 086 218 8713[SA ONLY]<br/>
            #                 Email:enquiries@charterquest.co.za
            #             ''' % (self.partner_id.name, result_body)
            # }
            # rest = mail_mail_obj.create(mail_vals)
            template_id = self.env.ref('cfo_snr_jnr.email_template_pcexam_voucher',raise_if_not_found=False)
            if template_id:
                template_id.sudo().with_context(
                    # email_to=each_request.get('email'),
                    voucher_list=voucher_lst,
                    email_cc='thecfo@charterquest.co.za',
                ).send_mail(self.id, force_send=True)

            # rest.send()

        result = super(account_invoice, self).write(vals)
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for record in self:
            #if vals.get('state') == 'paid' and not record.to_review:
            if not record.to_review and record.state =='paid':
                url_list = []
            if record.payment_ids:
                for line in record.sale_order_id.order_line:
                    if line.event_id.subject.has_pdf and line.event_id.pc_exam == False:
                        qid = base64.b64encode(str(line.id))
                        qid = urllib.quote(qid)
                        url_list.append({'subject':line.event_id.name.split('-')[0],'url':'%s/control_access_pdf/%s'%(base_url,qid)})
                # temp = self.mail_pdf_links({'url_list':url_list,'active_record':record})
        return result

    def send_pdf_email(self, value):
        template_pool = self.env['mail.template']
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        url_list = []
        if value.state == 'paid':
            for line in value.sale_order_id.order_line:
                if line.event_id.subject.has_pdf:
                    qid = base64.b64encode(str(line.id))
                    qid = urllib.quote(qid)
                    url_list.append({'subject': line.event_id.name.split('-')[0],
                                     'url': '%s/control_access_pdf/%s'%(base_url, qid)})
            template_id = template_pool.search([('name', '=ilike', 'PDF Resources')])
            if template_id:
                 body = template_id.body_html
                 body_old = body
                 count = 0
                 for url in url_list:
                     if  body.find(url['subject']) == -1:
                         body += "<p> For <b> %s Study Notes PDF </b>  <a href='%s'>Click here</a> </p>"%(url['subject'],url['url'])
                 if url_list:
                     template_id.write({'body_html':body})
                     template_id.send_mail(value)
                     template_id.write({'body_html': body_old})
        return True

class account_voucher(models.Model):

    _inherit = "account.voucher"

    student_number = fields.Char(string='Student No', size=64)
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    quote_type = fields.Selection([('freequote', 'Free Quote'),
                                   ('enrolment', 'Enrolment'),
                                   ('PC Exam', 'PC Exam'),
                                   ('CharterBooks', 'CharterBooks')], string='Quote Type')
    campus_id = fields.Many2one('res.partner', string='Campus')

    @api.multi
    def write(self,vals):
        if 'audit' in vals.keys():
            if self.invoice_id:
                self.invoice_id.write({'to_review':vals['audit']})
        if not vals.get('audit'):
             self.pool.get('account.invoice').send_pdf_email({'record':self.invoice_id})
             self.button_proforma_voucher({'active_model': 'account.invoice',
                                           'invoice_id': self.invoice_id.id})
        return super(account_voucher, self).write(vals)
