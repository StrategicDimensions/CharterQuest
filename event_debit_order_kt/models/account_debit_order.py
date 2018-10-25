# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from datetime import datetime, timedelta,date
# import StringIO
# import cStringIO
import base64
from dateutil.relativedelta import relativedelta
from tempfile import TemporaryFile
import csv
import odoo.addons.decimal_precision as dp

class exported_debit_order_file(models.Model):

    _name = 'exported.debit.order.file'

    name = fields.Char(string="Name",size=56)
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
                             ('auto_fnb_upload','Auto FNB Upload')], string='Type', default='manual_fnb_upload')
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
        pass
#         todaydate = date.today()
# #	todaydate = date(2016,01,context.get('today_date'))
#         action_date = todaydate+timedelta(days=2)
#         Filename = str(action_date)+'-'+'Manual FNB Upload'+'.csv'
#
#         import os
#         dirpath = "/home/acespritech"
#         filepath = os.path.join(dirpath, Filename)
#         fnb = open(filepath, 'wt')
#
#         writer = csv.writer(fnb)
#         writer.writerow(['BinSol – U ver 1.00'] )
#         writer.writerow([action_date] )
#         writer.writerow(['62328257060'] )
#         writer.writerow(('RECIPIENT NAME','RECIPIENT ACCOUNT','RECIPIENT ACCOUNT TYPE','BRANCHCODE','AMOUNT','OWN REFERENCE','RECIPIENT REFERENCE'))
#         do_ids = self.env['debit.order.details'].search([('dbo_date','=',str(action_date)),
#                                                          ('state','=','pending')])
#         count = 0
#         total = 0.0
#         if do_ids:
#             for obj in do_ids:
#                 if obj.invoice_id:
#
#                     date1 = datetime.strptime(obj.dbo_date, '%Y-%m-%d')
#
#                     date2 = date1 and str(date1.strftime('%y'))+''+str(date1.strftime('%m'))+''+str(date1.strftime('%d'))
#
#                     account_type = ''
#                     if obj.bank_acc_type == 'CUR':
#                         account_type = 1
#                     if obj.bank_acc_type == 'SAV':
#                         account_type = 2
#                     ownreference = ''
#                     cqreference = ''
#                     if str(obj.name).find('/') > -1:
#                         reference = str(obj.name).split('/')
#                         cqreference = reference[2] and str(reference[2]).replace('-','').ljust(14,' ')
#                         ownreference = "CHARTERQUE"+''+cqreference+''+date2
#                     count = count + 1
#                     total = total + obj.dbo_amount
#                     writer.writerow( (obj.acc_holder, obj.bank_acc_no, account_type, obj.bank_code, obj.dbo_amount, ownreference, ownreference) )
#         fnb.close()
          # import os
          # dirpath = "/home/charterquest8/public_html"
          # filepath = os.path.join(dirpath, Filename)
          #
          # out = open(filepath, 'rt').read()
          # out = base64.encodestring(out)
          # final_arr_data = {}
          # final_arr_data['file'] = out
          # final_arr_data['date'] = datetime.now()
          # final_arr_data['name'] = Filename
          # final_arr_data['action_date'] = action_date
          # final_arr_data['no_of_transactions'] = count
          # final_arr_data['transactions_amount_total'] = total
          # pl_report_id=self.pool.get('exported.debit.order.file').create(cr, uid, final_arr_data, context={})
          # mail_server_obj = self.pool.get('ir.mail_server')
          # mail_message_obj = self.pool.get('mail.message')
          # mail_mail_obj = self.pool.get('mail.mail')
          # email_cc = 'accounts@charterquest.co.za'+','+'rebecca.tshikadi@charterquest.co.za'+','+'patience.m@charterquest.co.za'
          # from_add = 'debitorders@charterquest.co.za'
          # To = 'vnti@charterquest.co.za'
          # CC = email_cc
          # dic = {
          #        'type':'binary',
          #        'datas' : out,
          #        'name' : Filename,
          #        'datas_fname': Filename,
          #        'res_model': 'exported.debit.order.file',
          #    }
          # document_id = self.pool.get('ir.attachment').create(cr,uid,dic,context=context)
          # subject_name = 'Student Debit Orders for'+ str(action_date)+'to be loaded'+'('+str(count)+'Transactions )'+'-'+'Value'+str(total)
          # body_html=("""<p><br>
          #
          #                           Dear Valentine,<br>
          #                           Please find attached FNB Manual Debit Order csv file for DebitOrders that should go off on %s.<br>
          #                           Please remember to upload this file to FNB.<br>
          #                           Regards,<br>
          #                           CQERP<br>
          #                           Should you encounter any issues please contact Strategic Dimensions on <a href="support@strategicdimensions.co.za">support@strategicdimensions.co.za</a><br>
          #                           </p>"""
          #           ) %(str(action_date))
          # mail_message_id = mail_message_obj.create(cr, uid, {'email_from': from_add, 'model': 'exported.debit.order.file', 'subject': subject_name ,'attachment_ids':[(6,0,[document_id])]}, context=context)
          # mail_server_ids = mail_server_obj.search(cr, uid, [], context=context)
          # mail_mail_id = mail_mail_obj.create(cr, uid, {'mail_message_id': mail_message_id, 'mail_server_id': mail_server_ids[0], 'state': 'outgoing', 'email_from': from_add, 'email_to': To  ,'email_cc':CC,'body_html':body_html,'attachment_ids':[(6,0,[document_id])]}, context=context)
          #
          # if mail_mail_id:
          #     mail_mail_obj.send(cr, uid, [mail_mail_id], context=context)
          #
          # debit_order_data ={}
          # debit_order_data['debit_order_batch'] = out
          # debit_order_data['state'] = 'inprogress'
          # debit_order_data['debit_order_batchname'] = Filename
          # for obj in self.pool.get('debit.order.details').browse(cr,uid,do_ids):
          #   if obj.invoice_id:
          #     debit_orderid = self.pool.get('debit.order.details').write(cr,uid,obj.id,debit_order_data)
          #     template_id = self.pool.get('email.template').search(cr,uid,[('name','=',"Scheduled Debit Order")])
          #     if template_id:
          #         mail_message = self.pool.get('email.template').send_mail(cr,uid,template_id[0],obj.id)
          #         template = self.pool.get('email.template').browse(cr, uid, template_id[0])
          #         body_html = self.pool.get('email.template').render_template(cr,uid,template.body_html,'debit.order.details',obj.id,context=None)
          #         subject = self.pool.get('email.template').render_template(cr,uid,template.subject,'debit.order.details',obj.id,context=None)
          #         message = self.pool.get('mail.message')
          #       #mail_obj = self.pool.get('mail.message').browse(cr,uid,sale_obj.message_ids[0])
          #         message.create(cr, uid, {
          #                          'res_id': obj.id,
          #                          'subject' : subject,
          #                          'model':'debit.order.details',
          #                          'body':body_html
          #                  }, context)

              #template_id1 = self.pool.get('email.template').search(cr,uid,[('name','=',"Debit Order Going of in two days")])
              #if template_id1:
              #   mail_message = self.pool.get('email.template').send_mail(cr,uid,template_id1[0],obj.id)

#         return True
#
#     def generate_fnb_integration_csv_test(self,cr,uid,context=None):
# 		new_date = date.today() + timedelta(days = -4)
# 		for x in range(1,4):
#                     todaydate = new_date + timedelta(days=x)
# 		    action_date = todaydate + timedelta(days=2)
# 		    Filename = str(action_date)+'-'+'Manual FNB Upload'+'.csv'
# 		    import os
# 		    dirpath = "/home/charterquest8/public_html"
# 		    filepath = os.path.join(dirpath, Filename)
# 		    fnb = open(filepath, 'wt')
# 		    writer = csv.writer(fnb)
# 		    writer.writerow( ['BinSol – U ver 1.00'] )
# 		    writer.writerow( [action_date] )
# 		    writer.writerow( ['62328257060'] )
# 		    writer.writerow(('RECIPIENT NAME','RECIPIENT ACCOUNT','RECIPIENT ACCOUNT TYPE','BRANCHCODE','AMOUNT','OWN REFERENCE','RECIPIENT REFERENCE'))
# 		    do_ids = self.pool.get('debit.order.details').search(cr,uid,[('dbo_date','=',str(action_date)),('state','=','pending')])
#
# 		    count = 0
# 		    total = 0.0
# 		    if do_ids:
# 		      for obj in self.pool.get('debit.order.details').browse(cr,uid,do_ids):
# 		        if obj.invoice_id:
#
# 		            date1 = datetime.strptime(obj.dbo_date, '%Y-%m-%d')
#
# 		            date2 = date1 and str(date1.strftime('%y'))+''+str(date1.strftime('%m'))+''+str(date1.strftime('%d'))
#
# 		            account_type = ''
# 		            if obj.bank_acc_type == 'CUR':
# 		                account_type = 1
# 		            if obj.bank_acc_type == 'SAV':
# 		                account_type = 2
# 		            ownreference = ''
# 		            cqreference = ''
# 		            if str(obj.name).find('/') > -1:
# 		                reference = str(obj.name).split('/')
# 		                cqreference = reference[2] and str(reference[2]).replace('-','').ljust(14,' ')
# 		                ownreference = "CHARTERQUE"+''+cqreference+''+date2
# 		            count = count + 1
# 		            total = total + obj.dbo_amount
# 		            writer.writerow( (obj.acc_holder, obj.bank_acc_no, account_type, obj.bank_code, obj.dbo_amount, ownreference, ownreference) )
# 		      fnb.close()
#                       import os
#                       dirpath = "/home/charterquest8/public_html"
#                       filepath = os.path.join(dirpath, Filename)
#
# 		      out = open(filepath, 'rt').read()
# 		      out = base64.encodestring(out)
# 		      final_arr_data = {}
# 		      final_arr_data['file'] = out
# 		      final_arr_data['date'] = todaydate
# 		      final_arr_data['name'] = Filename
# 		      final_arr_data['action_date'] = action_date
# 		      final_arr_data['no_of_transactions'] = count
# 		      final_arr_data['transactions_amount_total'] = total
# 		      pl_report_id=self.pool.get('exported.debit.order.file').create(cr, uid, final_arr_data, context={})
# 		      mail_server_obj = self.pool.get('ir.mail_server')
# 		      mail_message_obj = self.pool.get('mail.message')
# 		      mail_mail_obj = self.pool.get('mail.mail')
# 		      email_cc = 'accounts@charterquest.co.za'+','+'rebecca.tshikadi@charterquest.co.za'+','+'patience.m@charterquest.co.za'
# 		      from_add = 'debitorders@charterquest.co.za'
# 		      To = 'vnti@charterquest.co.za'
# 		      CC = email_cc
# 		      dic = {
# 		             'type':'binary',
# 		             'datas' : out,
# 		             'name' : Filename,
# 		             'datas_fname': Filename,
# 		             'res_model': 'exported.debit.order.file',
# 		         }
# 		      document_id = self.pool.get('ir.attachment').create(cr,uid,dic,context=context)
# 		      subject_name = 'Student Debit Orders for'+ str(action_date)+'to be loaded'+'('+str(count)+'Transactions )'+'-'+'Value'+str(total)
# 		      body_html=("""<p><br>
# 		                                Dear Valentine,<br>
# 		                                Please find attached FNB Manual Debit Order csv file for DebitOrders that should go off on %s.<br>
# 		                                Please remember to upload this file to FNB.<br>
# 		                                Regards,<br>
# 		                                CQERP<br>
# 		                                Should you encounter any issues please contact Strategic Dimensions on <a href="support@strategicdimensions.co.za">support@strategicdimensions.co.za</a><br>
# 		                                </p>"""
# 		                ) %(str(action_date))
# 		      mail_message_id = mail_message_obj.create(cr, uid, {'email_from': from_add, 'model': 'exported.debit.order.file', 'subject': subject_name ,'attachment_ids':[(6,0,[document_id])]}, context=context)
# 		      mail_server_ids = mail_server_obj.search(cr, uid, [], context=context)
# 		      mail_mail_id = mail_mail_obj.create(cr, uid, {'mail_message_id': mail_message_id, 'mail_server_id': mail_server_ids[0], 'state': 'outgoing', 'email_from': from_add, 'email_to': To  ,'email_cc':CC,'body_html':body_html,'attachment_ids':[(6,0,[document_id])]}, context=context)
#
# 		      if mail_mail_id:
# 		          mail_mail_obj.send(cr, uid, [mail_mail_id], context=context)
#
# 		      debit_order_data ={}
# 		      debit_order_data['debit_order_batch'] = out
# 		      debit_order_data['state'] = 'inprogress'
# 		      debit_order_data['debit_order_batchname'] = Filename
# 		      for obj in self.pool.get('debit.order.details').browse(cr,uid,do_ids):
# 		        if obj.invoice_id:
# 		          debit_orderid = self.pool.get('debit.order.details').write(cr,uid,obj.id,debit_order_data)
# 		          template_id = self.pool.get('email.template').search(cr,uid,[('name','=',"Scheduled Debit Order")])
# 		          if template_id:
# 		              mail_message = self.pool.get('email.template').send_mail(cr,uid,template_id[0],obj.id)
# 		              template = self.pool.get('email.template').browse(cr, uid, template_id[0])
# 		              body_html = self.pool.get('email.template').render_template(cr,uid,template.body_html,'debit.order.details',obj.id,context=None)
# 		              subject = self.pool.get('email.template').render_template(cr,uid,template.subject,'debit.order.details',obj.id,context=None)
# 		              message = self.pool.get('mail.message')
# 		              message.create(cr, uid, {
# 		                               'res_id': obj.id,
# 		                               'subject' : subject,
# 		                               'model':'debit.order.details',
# 		                               'body':body_html
# 		                       }, context)
# 		          #template_id1 = self.pool.get('email.template').search(cr,uid,[('name','=',"Debit Order Going of in two days")])
# 		          #if template_id1:
# 		          #   mail_message = self.pool.get('email.template').send_mail(cr,uid,template_id1[0],obj.id)
#
#
#         	return True


class debit_order_details(models.Model):

    _name="debit.order.details"

    _description = "Debit Order"
    _inherit = ['mail.thread']

    # def _bank_type_get(self):
    #     bank_type_obj = self.env['res.partner.bank.type']
    #     result = []
    #     type_ids = bank_type_obj.search([])
    #     bank_types = bank_type_obj.browse(type_ids)
    #     for bank_type in bank_types:
    #         result.append((bank_type.code, bank_type.name))
    #     5/0
    #     return result

    name = fields.Char(string='Order Reference', size=64, readonly=1, default='/')
    partner_id = fields.Many2one('res.partner', string="Student Name")
    dbo_amount = fields.Float(string='Debit Order Amount', digits_compute=dp.get_precision('Account'))
    course_fee = fields.Float(string='Fee (Less Interest)')
    interest = fields.Float(string='Interest')
    dbo_date = fields.Date(string='Debit Order Date')
    acc_holder = fields.Char(string='Account Holder Name')
    bank_name = fields.Many2one('res.bank',string='Bank Name')
    bank_acc_no = fields.Char(string='Bank Account No', size=54)
    bank_code = fields.Char(string='Bank Code',size=54)
    bank_type_id = fields.Many2one('res.bank.type', string="Bank Type")
    # bank_acc_type = fields.Selection([('')], string='Bank Account Type')
    sale_id = fields.Many2one('sale.order', string="Sale order")
    invoice_id = fields.Many2one('account.invoice', string='Invoice No')
    state = fields.Selection([('pending', 'Pending'),
                              ('inprogress','In Process'),
                              ('done','Successful'),
                              ('failed','Failed'),
                              ('cancelled',"Cancelled"),
                              ('under_review','Under Review')], string='Debit Order Status')
    debit_order_batch = fields.Binary(string="Debit Order Batch File")
    debit_order_batchname = fields.Char( string="Batch File Name",size=64)
    student_number = fields.Char(string='Student No', size=64)


    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Debit Order Reference must be unique!'),
    ]

    # @api.multi
    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     if self.partner_id:
    #         self.update({'student_number': self.partner_id.student_number})

    @api.model
    def get_debit_order_status_successful(self):
          todaydate = date.today()
          action_date = todaydate-timedelta(days=7)
          do_ids = self.env['debit.order.details'].search([('dbo_date', '=', str(action_date)),
                                                           ('state', '=', 'inprogress')])
          for do_id in do_ids:
              # do_obj = self.pool.get('debit.order.details').browse(cr,uid,do_id)
              do_write = do_id.write({'state': 'done'})
              if do_id.invoice_id:
                  account_invoice   = self.env['account.invoice'].browse(do_id.invoice_id.id)
                  if account_invoice.state != 'paid':
                     journal_ids = self.env['account.journal'].search([('code', '=', 'EFT')])
                     journal = self.env['account.journal'].browse(journal_ids[0].id)
                     account_voucher={
                         'partner_id': do_id.partner_id.id,
                         'company_id': do_id.partner_id.company_id.id,
                         'type':'receipt',
                         'journal_id': journal_ids.id,
                         'reference': do_id.name,
                         'name':do_id.name,
                         'account_id': journal.default_credit_account_id.id,
                         'payment_method': journal_ids[0],
                         'amount': do_id.dbo_amount,
                     }
                     account_voucher_id = self.env['account.voucher'].create(account_voucher)
                     account_voucher_line = {
                        'partner_id': do_id.partner_id.id,
                        'company_id': do_id.partner_id.company_id.id,
                        'type': 'dr',
                        'voucher_id': account_voucher_id,
                        'amount': do_id.dbo_amount,
                        'name': do_id.name,
                        'account_id': journal.default_credit_account_id.id,
                      }
                     self.env['account.voucher.line'].create(account_voucher_line)
                     self.env['account.voucher'].button_proforma_voucher([account_voucher_id],
                                                                         {'active_model': 'account.invoice',
                                                                          'invoice_id':do_id.invoice_id.id})
                     account_voucher = self.env['account.voucher'].browse(account_voucher_id.id)
                     self.env['account.invoice'].pay_and_reconcile([do_id.invoice_id.id],
                                                                   do_id.dbo_amount,
                                                                   journal.default_credit_account_id.id,
                                                                   account_voucher.period_id.id,
                                                                   account_voucher.journal_id.id, False, False, False)
                     template_id = self.env['mail.template'].search([('name', '=', "Sending Enrolment Statement to Student")])
                     if template_id:
                        mail_message = self.env['mail.template'].send_mail(template_id[0], do_id)
          return True

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

    def export_debit_orders(self):
         todaydate = date.today()
         action_date = todaydate+timedelta(days=2)

         first_action_date = last_action_date = ("%02d"%action_date.year)[2:]+"%02d"%action_date.month+"%02d"%action_date.day
         #nextmonth = todaydate+relativedelta(months=+1)
         mm = todaydate.month
         dd = todaydate.day
         yy = todaydate.year
         yy = int(str(yy)[2:])
         yymmdd=str(yy)+("%02d" %(mm,))+("%02d"%(dd,))
         purge_date = last_action_date
         user_code = "4055"

         previous_file_ids = self.env['exported.debit.order.file'].search([])

         if previous_file_ids:
               generation_number = int(self.pool.get('exported.debit.order.file').browse(max(previous_file_ids)).generation_number)+1
         else:
              generation_number = '0001'
         generation_number = "%04d"%generation_number
         do_ids = self.search([('dbo_date','=',str(action_date))])
         # dates = self.read(cr,uid,do_ids,['dbo_date'])
         myfile = TemporaryFile('w+')

         hashfile = TemporaryFile('w+')
         ##1.1 BANKSERV IMPORT - INSTALLATION HEADER RECORD.
         myfile.write("021001DEMOCUST"+user_code+"0021"+yymmdd+purge_date+generation_number+"18000180MAGTAPE   "+' '*124)

         acc_type = {'SAV':'2','CUR':'1',"Transmission":'3',"Bond":'4','Normal Bank Account':'0','bank':'0'}
         transaction_history=""
         user_seq_no = 0
         total_debit = 0
         hash_total = 0
         records = 0
#
         for obj in do_ids:
                records = records+1
                homing_branch =  obj.bank_code
                homing_acc_no =  (obj.bank_acc_no).rjust(11,"0")
                hash_total += int(homing_acc_no)
                type_of_account = obj.bank_type_id
                acctype = acc_type[type_of_account]
                amount = obj.dbo_amount
                total_debit += amount
                amount = "%011d"%int(amount*100)
#                action_date = obj.dbo_date.split('-')
#                action_date= action_date[0][2:]+action_date[1]+action_date[2]
#                if len(transaction_history) == 0:
#                      first_action_date = action_date
#                last_action_date = action_date
                user_name = "CharterQue"  #User Abbreviated name.
                reference = obj.name

                #user_name = (user_name.ljust(10))[:10]
                reference = (reference.ljust(20))[:20]
                home_account_name = obj.acc_holder and ((obj.acc_holder)[:30]).ljust(30)  or " "*30
                #bank_name = bank_name
                user_seq_no += 1
                userseq = "%06d" % (user_seq_no,)
                transaction_history += "\n5025065562328257060"+user_code+userseq+homing_branch+homing_acc_no+acctype+amount+first_action_date+"320000"+user_name+reference+home_account_name+"00000000000000000000"+" "*16+"21"+" "*12
#
         ## BANKSERV IMPORT FILE - USER HEADER RECORD
         myfile.write("\n04"+user_code+yymmdd+purge_date+first_action_date+last_action_date+"000001"+generation_number+"TWO DAY   "+" "*130)

         ## BANKSERV IMPORT FILE - STANDARD TRANSACTION RECORD
         myfile.write(transaction_history)

         ## BANKSERV IMPORT FILE - CONTRA RECORD
         userseq = "%06d" % (user_seq_no + 1,)
         amount_contra = "%011d" % (total_debit*100,)
         contra_record = "\n5225065562328257060"+user_code+userseq+"250655623282570601"+amount_contra+last_action_date+"10"+"0000"+"CharterQueCONTRA-"+last_action_date+"-"+generation_number+"  "+"CharterQuestTraining Institute"+" "*50
         myfile.write(contra_record)
#
         ## BANKSERV IMPORT FILE - USER TRAILER RECORD
         hash_total = "%12d" % (hash_total,)
         no_of_debit_rec = userseq
         total_debit = total_credit ="%012d"%(total_debit*100)
         myfile.write("\n92"+user_code+"000001"+userseq+first_action_date+last_action_date+no_of_debit_rec+"000001"+"000001"+"000001"+total_debit+total_credit+hash_total+" "*96)
#
#          ## BANKSERV IMPORT FILE - INSTALLATION TRAILER RECORD
         no_of_records = "%06d" % (user_seq_no+3,)
         block_count = (user_seq_no+3)/10
         if block_count > int(block_count):
                block_count = block_count+1
         block_count = "%06d"%block_count
         myfile.write("\n941001"+"DEMOCUST"+user_code+"0021"+str(yymmdd)+purge_date+generation_number+"18000180MAGTAPE   "+block_count+no_of_records+"000002"+" "*106)
         myfile.seek(0)
         out = myfile.read()
         out = base64.encodestring(out)
         final_arr_data = {}
         final_arr_data['file'] = out
         final_arr_data['date'] = datetime.now()
         final_arr_data['name'] ="FTPTCPIP.ACBFILE1"
         pl_report_id=self.env['exported.debit.order.file'].create(final_arr_data)

#          ##HASH File

         hashfile.write(user_code+"0008"+"92"+user_code+"000001"+userseq+first_action_date+last_action_date+"000000"+no_of_debit_rec+"000000"+total_debit+"000000000000"+hash_total+hash_total.rjust(18,'0'))

         hashfile.seek(0)
         out = hashfile.read()
         out = base64.encodestring(out)
         final_arr_data = {}
         final_arr_data['hash_file'] = out
         final_arr_data['hash_file_name'] = "FTPTCPIP.FNBHASH"
    #     previous_file_ids = self.pool.get('exported.debit.order.file').search(cr,uid,[])
    #     if previous_file_ids:
    #           generation_number = int(self.pool.get('exported.debit.order.file').browse(cr,uid,max(previous_file_ids)).generation_number)+1
    #     else:
    #          generation_number = '0001'
         final_arr_data['generation_number'] = generation_number
         final_arr_data['action_date'] = action_date
         final_arr_data['no_of_transactions'] = records
         final_arr_data['transactions_amount_total'] = total_debit
         final_arr_data['installation_generation_number'] = generation_number
         final_arr_data['user_generation_number'] = generation_number
         final_arr_data['hash_total'] = hash_total
         pl_report_id.write(final_arr_data)

    @api.model
    def send_debit_order_emails(self):
        today = date.today()
        debit_order_ids = self.search([('state', '=', 'pending')])
        for record in debit_order_ids:
             if record.dbo_date and record.invoice_id:
                dbo_date = (record.dbo_date).split('-')
                two_days_before = date(day=int(dbo_date[2]), month=int(dbo_date[1]),year= int(dbo_date[0])) + timedelta(days=-2)
                if today == two_days_before:
                    template_id = self.env['mail.template'].search([('name','=',"Debit Order Going of in two days")])
                    if template_id:
                        mail_message = self.env['mail.template'].send_mail(template_id[0],record.id)
             return True

    def failed_debit_order_notification(self):
        mail_message = self.env['mail.message']
        mail_obj = self.env['mail.mail']
        mail_server = self.env['ir.mail_server'].search([], limit=1)
        partner_ids = self.env['res.partner'].search([])

        for partner in partner_ids:
            debit_order_ids = self.search([('partner_id', '=', partner.id),
                                           ('state', '=', 'failed')])
            if debit_order_ids:
                header_body = ('''
                             Dear %s <br>
                             Your debit order signed with CharterQuest returned as follows: <br>
                             <br>
                             <br>
                            ''')%(partner.name)

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

                               """)%(debit.dbo_date,debit.name,debit.dbo_amount)
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
                mail_dict = {'subject':"Failed Debit order Notification",
                             'email_from': 'thirupathi@strategicdimensions.co.za',
                             'email_to': 'shravan@strategicdimensions.co.za',
                             'body_html': body,
                             'res_id': '',
                             'model': 'debit.order.details',
                            }
                mail_dict['mail_server_id'] = mail_server.id
                mail_id = [mail_obj.create(mail_dict)]
                res = mail_obj.send(mail_id)
            return True

    @api.multi
    def write(self,vals):
        result = super(debit_order_details, self).write(vals)
        if vals.get('state', False):
            if vals['state'] == 'failed':
                self.failed_debit_order_notification()
        return result


class debit_order_mandate(models.Model):

    _name = 'debit.order.mandate'

    partner_id = fields.Many2one('res.partner',"Student Name")
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