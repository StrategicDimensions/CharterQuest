from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo import netsvc
import urllib
from odoo.http import request
import hashlib
from datetime import date, datetime
from urllib.parse import urljoin



class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        # super(sale_order, self).action_confirm()
        if not self.pc_exam and self.affiliation == '1':
            if not self:
                return []
            dummy, view_id = self.env['ir.model.data'].get_object_reference('event_debit_order_kt',
                                                                            'view_payment_confirmation_form')
            return {
                'name': _("Payment Confirmation"),
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'payment.confirmation',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'domain': '[]',
                'context': {
                    'default_payment_amount': self.amount_total,
                    'default_payment_ref': self.name,
                    'default_order_id': self.id,
                }
            }
        else:
            self._action_confirm()
            if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
                self.action_done()
        return True

    decoded_quote_name = fields.Char(string="decoded quote name", size=256)
    remittance_amount = fields.Float(string='Remittance Amount')
    debit_order_mandat = fields.One2many('debit.order.mandate', 'sale_id', string="Debit Order Mandate")
    diposit_selected = fields.Integer(string="Selected Deposit %")
    due_amount = fields.Float(string='Total Due')
    months = fields.Integer(string="Months required to pay")
    out_standing_balance_incl_vat = fields.Float(string="Outstanding Balance (inclusive of VAT & Interest)")
    monthly_amount = fields.Float(string="Monthly Amount")
    payment_amount = fields.Float(string='Payment Amount')
    payment_ref = fields.Char(string='Payment Reference')
    payment_method = fields.Many2one('account.journal', string='Payment Method')
    debit_order_mandate = fields.Boolean(string='Debit Order Mandate Submitted')
    debit_order_mandate_link = fields.Char(string="Debit Order Mandate Link")

    @api.model
    def get_debit_order_mandate_reminder(self):
        sale_ids = self.search([('debit_order_mandate', '=', False),
                                ('state', '=', 'manual'),
                                ('pc_exam', '=', False),
                                ('create_date', '>=', '2014-05-01')])

        for sale_id in sale_ids:
            if sale_id.debit_order_mandate_link:
                template_id = self.env['mail.template'].search([('name', '=', "Debit Order Mandate Reminder Email")])
                if template_id:
                    mail_message = template_id.send_mail(sale_id.id)
        return True

    @api.model
    def debit_order_mandate_sms(self):
        pass
        # """This function is used to send sms """
        # gateway = self.pool.get('sms.smsclient').search(cr,uid,[])
        # if not gateway:
        #     raise orm.except_orm(_('Warning !'), _('You have to be Configured sms gateway first %s '))
        # gateway = self.pool.get('sms.smsclient').browse(cr,uid,gateway[0])
        # sale_ids = self.search(cr,uid,[('debit_order_mandate','=',False),('state','=','manual'),('pc_exam','=',False)])
        # for sale_id in sale_ids:
        #     sale_obj = self.browse(cr,uid,sale_id)
        #     if not sale_obj.partner_id.mobile:
        #         return
        #     if gateway:
        #         if not self.pool.get('sms.smsclient')._check_permissions(cr, uid, gateway.id, context=context):
        #             raise orm.except_orm(_('Permission Error!'), _('You have no permission to access %s ') % (gateway.name,))
        #         url = gateway.url
        #         name = url
        #         if gateway.method == 'http':
        #             prms = {}
        #             for p in gateway.property_ids:
        #                 if p.type == 'user':
        #                     prms[p.name] = p.value
        #                 elif p.type == 'password':
        #                      prms[p.name] = p.value
        #                 elif p.type == 'to':
        #                      prms[p.name] = sale_obj.partner_id.mobile
        #                 elif p.type == 'sender':
        #                      prms[p.name]= p.value
        #                 elif p.type == 'sms':
        #                      prms[p.name] = """<p>Hi %s,\nReminder to complete the Debit Order Mandate form<a href = "%s">Link</a>.CharterQuest</p>"""%(sale_obj.partner_id.name,sale_obj.debit_order_mandate_link)
        #                 elif p.type == 'extra':
        #                     prms[p.name] = p.value
        #             params = urllib.urlencode(prms)
        #             name = url + "?" + params
        #         queue_obj = self.pool.get('sms.smsclient.queue')
        #         vals = {
        #           'name': name,
        #           'gateway_id': gateway.id,
        #           'state': 'draft',
        #           'mobile': sale_obj.partner_id.mobile,
        #           'msg': ("""<p>Hi %s,\nReminder to complete the Debit Order Mandate form \n <a href = "%s">Link</a>.CharterQuest</p>""")%(sale_obj.partner_id.name,sale_obj.debit_order_mandate_link)
        #          }
        #         queue_obj.create(cr, uid, vals, context=context)


class payment_confirmation(models.Model):
    _name = 'payment.confirmation'

    payment_amount = fields.Float(string='Payment Amount')
    payment_ref = fields.Char(string='Payment Reference')
    payment_method = fields.Many2one('account.journal', string='Payment Method')
    order_id = fields.Many2one('sale.order', string='Sale Order')

    @api.multi
    def button_create_saleorder(self):
        invoice_line=[]
        invoice_obj = request.env['account.invoice'].sudo()
        sale_obj = self.env['sale.order'].browse(self.order_id.id)
        dic = {
            'payment_amount': self.payment_amount,
            'payment_ref': self.payment_ref,
            'payment_method': self.payment_method.id
        }
        quote_name = "SO{0}WEB".format(str(sale_obj.id).zfill(3))
        m = hashlib.md5(quote_name.encode())
        decoded_quote_name = m.hexdigest()
        config_para = request.env['ir.config_parameter'].sudo().search(
            [('key', 'ilike', 'web.base.url')])
        # self.order_id.write(dic)
        # self.order_id._action_confirm()
        if self.payment_amount == sale_obj.amount_total:
            sale_adv_payment = {
                'advance_payment_method': 'all',
            }
            advanc_pay_id = self.env['sale.advance.payment.inv'].create(sale_adv_payment)
            # advanc_pay_id.create_invoices()
            for each_order_line in sale_obj.order_line:
                invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                                            'name': each_order_line.name,
                                            'quantity': 1.0,
                                            'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
                                            'invoice_line_tax_ids': [
                                                (6, 0, [each_tax.id for each_tax in each_order_line.tax_id])],
                                            'price_unit': each_order_line.price_unit,
                                            'discount': each_order_line.discount}])
            invoice_id = invoice_obj.sudo().create({'partner_id': sale_obj.partner_id.id,
                                                    'campus': sale_obj.campus.id,
                                                    'prof_body': sale_obj.prof_body.id,
                                                    'sale_order_id': sale_obj.id,
                                                    'semester_id': sale_obj.semester_id.id,
                                                    'invoice_line_ids': invoice_line,
                                                    'residual': sale_obj.out_standing_balance_incl_vat,
                                                    })
            sale_obj._action_confirm()
            # currency = request.env['res.currency'].sudo().search([('name', '=', 'ZAR')], limit=1)
            invoice_id = request.env['account.invoice'].sudo().search([('sale_order_id','=',sale_obj.name)])
            ctx = {'default_type': 'out_invoice', 'type': 'out_invoice', 'journal_type': 'sale',
                              'company_id': self.order_id.company_id.id,'currency_id': sale_obj.pricelist_id.currency_id.id,}
            inv_default_vals = request.env['account.invoice'].with_context(ctx).sudo().default_get(['journal_id'])
            ctx.update({'journal_id': inv_default_vals.get('journal_id')})
            invoice_id = sale_obj.with_context(ctx).sudo().action_invoice_create()
            invoice_id = request.env['account.invoice'].sudo().browse(invoice_id[0])
            journal_id = request.env['account.journal'].sudo().browse(inv_default_vals.get('journal_id'))
            payment_methods = journal_id.inbound_payment_method_ids or journal_id.outbound_payment_method_ids
            # invoice_id.reconcile = True
            print("\n\n\n\n==============sale_obj======",sale_obj,sale_obj.amount_total)
            payment_id = request.env['account.payment'].sudo().create({
                'payment_difference':-sale_obj.amount_total,
                'partner_id': self.order_id.partner_id.id,
                'amount': sale_obj.amount_total,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'invoice_ids': [(6, 0, invoice_id.ids)],
                'payment_date': datetime.today(),
                'journal_id': journal_id.id,
                'payment_method_id': payment_methods[0].id,
                'amount':self.payment_amount,
            })
            invoice_id.action_invoice_open()
            print("\n\n\n\n========payment_id==========",payment_id,payment_id.amount)
            payment_id.action_validate_invoice_payment()

        if config_para:
            link = config_para.value + "/payment/" + decoded_quote_name + '/' + decoded_quote_name
            if sale_obj.amount_total != self.payment_amount:
                sale_obj.write({'debit_order_mandate_link': link,'debitorder_link':True})
                template_id = self.env['mail.template'].search([('name', '=', "Debit Order Mandate Email")])
                if template_id:
                    mail_message = template_id.send_mail(self.order_id.id, force_send=True)
                    message = self.env['mail.message']
                    if sale_obj.message_ids:
                        message.create({
                            'res_id': sale_obj.message_ids[0].res_id,
                            'parent_id': sale_obj.message_ids[0].id,
                            'subject': template_id.subject,
                            'model': 'sale.order',
                            'body': template_id.body_html
                        })
        self.order_id.write(dic)
        self.order_id._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()

            #     invoice_obj = self.env['sale.order'].read(self._context.get('active_id'),['invoice_ids'])
            # 
            #     self.pool.get('account.invoice').signal_workflow(cr, uid, invoice_obj['invoice_ids'], 'invoice_open')
            #
            #     account_invoice = self.pool.get('account.invoice').browse(cr,uid,invoice_obj['invoice_ids'][0])
            #     move_line_id = self.pool.get('account.move.line').search(cr, uid, [('name','=ilike','/'),('move_id','=',account_invoice.move_id.id)])
            #     if account_invoice.state != 'paid':
            #         journal_ids = self.pool.get('account.journal').search(cr,uid,[('type','=','bank'),('name','=','Bank')])
            #         journal = self.pool.get('account.journal').browse(cr,uid,journal_ids[0])
            #         account_voucher = {
            #              'partner_id': sale_obj.partner_id.id,
            #              'company_id': sale_obj.company_id.id,
            #              'type': 'receipt',
            #              'journal_id': journal_ids[0],
            #              'reference': sale_obj.name,
            #              'name': sale_obj.campus.name,
            #              'account_id': journal.default_credit_account_id.id,
            #              'payment_method': sale_obj.payment_method,
            #              'amount': sale_obj.payment_amount,
            #           }
            #         account_voucher_id = self.env['account.voucher'].create(account_voucher)
            #         account_voucher_line = {
            #             'partner_id': sale_obj.partner_id.id,
            #             'company_id': sale_obj.company_id.id,
            #             'type': 'cr',
            #             'voucher_id': account_voucher_id,
            #             'amount': sale_obj.payment_amount,
            #             'name': sale_obj.campus.name,
            #             'account_id': account_invoice.account_id and account_invoice.account_id.id,
            #             'move_line_id': move_line_id and move_line_id[0]
            #           }
            #         self.env['account.voucher.line'].create(account_voucher_line)
            #         self.env.get('account.voucher').button_proforma_voucher([account_voucher_id],{'active_model':'account.invoice','invoice_id':invoice_obj['invoice_ids'][0]})
            #         account_voucher = self.env['account.voucher'].browse(account_voucher_id)
            # self.pool.get('account.invoice').pay_and_reconcile(cr,uid,invoice_obj['invoice_ids'][0],sale_obj.payment_amount,journal.default_credit_account_id.id,account_voucher.period_id.id,account_voucher.journal_id.id,False,False,'/')
            template_id = self.env['mail.template'].sudo().search([('name','=',"Sending Tax Invoice to Student")])
            if template_id:
                mail_message = template_id.send_mail(self.order_id.invoice_ids[0].id)
        # else:
        #     template_id = self.env['mail.template'].search([('name', '=', "Debit Order Mandate Email")])
        #     if template_id:
        #         mail_message = template_id.send_mail(self.order_id.id,force_send=True)
        #         message = self.env['mail.message']
        #         if sale_obj.message_ids:
        #             message.create({
        #                 'res_id': sale_obj.message_ids[0].res_id,
        #                 'parent_id': sale_obj.message_ids[0].id,
        #                 'subject': template_id.subject,
        #                 'model': 'sale.order',
        #                 'body': template_id.body_html
        #             })
        return True

