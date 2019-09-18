# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2012 - Present Acespritech Solutions Pvt. Ltd. All Rights Reserved
#    Author: <info@acespritech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
import base64
from odoo.http import request



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price = fields.Float(string='Price',
                         digits_compute=dp.get_precision('Product Price'))
    author_id = fields.Many2one('res.partner', 'Author')
    format = fields.Char('Format')
    publisher = fields.Char('Publisher')
    country_id = fields.Many2one('res.country', 'Country of Publication')
    date_of_publish = fields.Date('Date of Publish')
    course_code = fields.Char('Course Code')
    book_edition = fields.Char('Book Edition')


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_link = fields.Char(string="Sale Order Link")
    sale_link = fields.Char(string="Sale Link")

    @api.multi
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()

        res.update({'sale_order_reference_link': self.sale_order_link})

        return res

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_order_reference_link = fields.Char(string="Sale Order Reference Link")


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_validate_invoice_payment(self):
        res =  super(AccountPayment, self).action_validate_invoice_payment()
        email_obj = self.env['mail.template']
        mail_obj = self.env['mail.mail'].sudo()
        if res:
            if self.payment_difference > 0:
                 partial_template_id = email_obj.sudo().search([('name', '=', "Partly invoice payment")])
                 if partial_template_id:
                     email_data = partial_template_id.generate_email(self.invoice_ids[0].id)
                     mail_values = {
                        'email_from': email_data.get('email_from'),
                        'email_cc': email_data.get('email_cc'),
                        'reply_to': email_data.get('reply_to'),
                        'email_to': self.invoice_ids[0].partner_id.email,
                        'subject':  'CharterQuest Enrolment: Debit Order Mandate',
                        'body_html': email_data.get('body_html'),
                        'notification': True,
                        'auto_delete': False,
                        'model': 'account.invoice',
                        'res_id': self.invoice_ids[0].id
                        }
                     msg_id = mail_obj.create(mail_values)
                     msg_id.send()
            if self.payment_difference < 0:
                 full_template_id = email_obj.sudo().search([('name', '=', "Full invoice payment")])
                 if full_template_id:
                     attachment_list=[]
                     agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                     if agreement_id:
                         attachment_list.append(agreement_id)
                     pdf_data = request.env.ref('event_price_kt.report_enrollment_invoice').sudo().render_qweb_pdf(
                         self.invoice_ids[0].id)
                     if pdf_data:
                         pdfvals = {'name': 'Invoice',
                                    'db_datas': base64.b64encode(pdf_data[0]),
                                    'datas': base64.b64encode(pdf_data[0]),
                                    'datas_fname': 'Invoice.pdf',
                                    'res_model': 'account.invoice',
                                    'type': 'binary'}
                         pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                         attachment_list.append(pdf_create)
                     print ("\n\n\n\n\n========attachment=====",attachment_list)
                     email_data = full_template_id.generate_email(self.invoice_ids[0].id)
                     mail_values = {
                        'email_from': email_data.get('email_from'),
                        'email_cc': email_data.get('email_cc'),
                        'reply_to': email_data.get('reply_to'),
                        'email_to': self.invoice_ids[0].partner_id.email,
                        'subject':  'CharterQuest Tax Invoice',
                        'body_html': email_data.get('body_html'),
                        'notification': True,
                        'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])],
                        'auto_delete': False,
                        'model': 'account.invoice',
                        'res_id': self.invoice_ids[0].id
                        }
                     msg_id = mail_obj.create(mail_values)
                     msg_id.send()
            attchment_list = []
            template_id = email_obj.sudo().search([('name', '=', "Invoice Payment")])
            if template_id and self.invoice_ids[0].quote_type == 'CharterBooks':
                pdf_data_order = self.env.ref(
                    'event_price_kt.report_invoice_book').sudo().render_qweb_pdf(self.invoice_ids[0].id)
                if pdf_data_order:
                    pdfvals = {'name': 'Invoice Report',
                               'db_datas': base64.b64encode(pdf_data_order[0]),
                               'datas': base64.b64encode(pdf_data_order[0]),
                               'datas_fname': 'Invoice Report.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = self.env['ir.attachment'].sudo().create(pdfvals)
                    attchment_list.append(pdf_create)

                agreement_id = self.env.ref('cfo_snr_jnr.charterbook_term_and_condition_pdf')

                if agreement_id:
                    attchment_list.append(agreement_id)
                email_data = template_id.generate_email(self.invoice_ids[0].id)

                mail_values = {
                    'email_from': email_data.get('email_from'),
                    'email_cc': email_data.get('email_cc'),
                    'reply_to': email_data.get('reply_to'),
                    'email_to': self.invoice_ids[0].partner_id.email,
                    'subject':  (self.invoice_ids[0].sale_order_id.carrier_id.warehouse_id.name or 'false') + ' - CharterBooks: Order Confirmation',
                    'body_html': email_data.get('body_html'),
                    'notification': True,
                    'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                    'auto_delete': False,
                    'model': 'account.invoice',
                    'res_id': self.invoice_ids[0].id
                }
                msg_id = mail_obj.create(mail_values)
                msg_id.send()
                
                
                
        return res

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)

        res.write({'sale_order_reference_link': order.sale_order_link})

        return res


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse")


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
