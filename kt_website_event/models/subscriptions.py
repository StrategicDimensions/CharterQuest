# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date

## Imports added by Raaj
from openerp.addons.kt_website_event.edi.template import *
from openerp.addons.kt_website_event.edi.reset_password_template import *
import hashlib
# import pyDes
import urllib3
import base64


class event_registration(models.Model):
    _inherit = 'event.registration'

    need_rescheduling = fields.Boolean('Need Rescheduling')
    rescheduling_done = fields.Boolean('Rescheduling Done')


class stock_move(models.Model):
    _inherit = 'stock.move'

    # @api.multi
    # def _get_delivery_order_source(self):
    #     res = {}
    #     for rec in self:
    #         if rec.picking_id:
    #             res[rec.id] = rec.picking_id and rec.picking_id.delivery_order_source or ''
    #     return res

    delivery_order_source = fields.Char(string="Delivery Order Source", store=True)


class res_partner(models.Model):
    _inherit = "res.partner"

    is_subscriber = fields.Boolean("Is Magazine Subscriber?")
    subscriber_country_id = fields.Many2one('res.country', "Country of Residence")
    subscriber_occupation = fields.Selection([('I am a student', 'I am a student'),
                                              ('I am a working professional', 'I am a working professional')],
                                             "Occupation")
    subscriber_future_career_interest = fields.Char("Future Career Interest")
    subscriber_profession_work = fields.Char("Profession Work")
    subscriber_field_study = fields.Char("Field of Study")
    subscriber_level_study = fields.Char("Level of Study")
    subscriber_town = fields.Char('Town')
    magazine_source = fields.Selection([('The Charterquest Institue Website', 'The Charterquest Institue Website'),
                                        ('Social Media', 'Social Media'),
                                        ('Professional Body', 'Professional Body'),
                                        ('CFO SA', 'CFO SA'),
                                        ('My University/School', 'My University/School'),
                                        ('My Mentor/Career Coach', 'My Mentor/Career Coach'),
                                        ('A friend', 'A friend'),
                                        ('Other', 'Other'),
                                        ('Email Campaign', 'Email Campaign')], string="Magazine Source")
    subscription_date = fields.Date('Subscription Date', default=fields.Date.context_today)
    imported_subscribers = fields.Boolean('Imported Subscribers')
    magazine_opt_out = fields.Boolean('Do not send Magazine Invitation')
    password = fields.Char(string="Password")

    # @api.model
    # def create(self, vals):
    #     partner = self.env['res.partner']
    #     res_id = partner.search(['|', ('email', '=ilike', vals.get('email')), ('email_1', '=ilike', vals.get('email'))])
    #     ## Raaj added new
    #     if vals.has_key('email') and (vals['email']) != False:
    #         vals['email'] = str(vals['email']).lower()
    #     if vals.has_key('email_1') and (vals['email_1']) != False:
    #         vals['email_1'] = (vals['email_1']).lower()
    #     ## End
    #     if res_id:
    #         res_id = res_id[0]
    #         res_id.write({'is_subscriber': True})
    #     else:
    #         vals.update({'is_subscriber': True})
    #         res_id = super(res_partner, self).create(vals)
    #         blog = self.env['blog.blog']
    #         blog_id = blog.search([('name', '=', "The Future CFO Magazine")])
    #         res = blog_id.write({'message_follower_ids': (4, res_id)})
    #         record = partner.browse(res_id)
    #         mail_vals = {
    #             'email_from': 'futurecfomagazine@charterquest.co.za',
    #             'email_to': record.email or record.email_1,
    #             'email_cc': 'futurecfomagazine@charterquest.co.za',
    #             'subject': 'Subscription Confirmation Email',
    #             # 'body_html':email_template_1 + email_template_for_activate_regular.format(record.name,res_id),
    #         }
    #
    #         res = self.env['mail.mail'].create(mail_vals)
    #     return res_id

    ## Magazine Unsubscribe
    def subscribe_all_erp_partners_cron(self):
        partner_obj = self.env['res.partner']
        partner_ids = partner_obj.search(
            [('imported_subscribers', '=', False), ('is_subscriber', '=', False), ('magazine_opt_out', '=', False)])
        for rec in partner_ids:
            email = partner_obj.read(['email', 'email_1', 'name'])
            if email['email'] or email['email_1']:
                mail_vals = {
                    'email_from': 'futurecfomagazine@charterquest.co.za',
                    'email_to': email['email'] or email['email_1'],
                    'email_cc': 'futurecfomagazine@charterquest.co.za',
                    'subject': 'Invitation to Subscribe',
                    # 'body_html':email_template_1 + email_template_for_erp_users_cron.format(email['name'],rec).decode('utf-8'),
                }

                res = self.env['mail.mail'].create(mail_vals)
        return True

    def send_2ndold_issue(self):
        partner_obj = self.env['res.partner']
        partner_ids = partner_obj.search([('email', '=', 'raj@strategicdimensions.co.za')])
        template_obj = self.env['email.template']
        template_id = template_obj.search([('name', '=', 'Future CFO February Newsletter')])
        for rec in partner_ids:
            email = partner_obj.read(['email', 'email_1', 'name'])
            if email['email'] or email['email_1']:
                mail_vals = {
                    'email_from': 'thecfo@charterquest.co.za',
                    'email_to': email['email'] or email['email_1'],
                    'email_cc': 'thecfo@charterquest.co.za',
                    'subject': '2nd Issue Release! Download your FREE Copy!',
                    # 'body_html': email_template_unsubscribe + email_template_unsubscribe2.format(rec)
                }
                res = self.env['mail.mail'].create(mail_vals)
        return True

    def send_2nd_issue(self):
        partner_obj = self.env['res.partner']
        partner_ids = partner_obj.search([('is_subscriber', '=', True)])
        for rec in partner_ids:
            email = partner_obj.read(['email', 'email_1'])
            mail_vals = {
                'email_from': 'thefuturecfo@charterquest.co.za',
                'email_to': email['email'] or email['email_1'],
                'email_cc': 'contributors@thefuturecfo.co.za',
                'subject': 'Stand a chance to be featured.',
                # 'body_html': email_template_new_issue,
            }

            res = self.env['mail.mail'].create(mail_vals)
        return True

    def send_new2_issue(self):
        picking_obj = self.env['stock.picking']
        picking_ids = picking_obj.search([('min_date', '<', '01-01-2017')])
        for rec in picking_ids:
            rec.write({'state': 'cancel'})
        return True

    def send_new2_issue_useless(self):
        partner_obj = self.env['res.partner']
        partner_ids = partner_obj.search([('is_subscriber', '=', True)])
        for rec in partner_ids:
            email = rec.read(['email', 'email_1'])
            mail_vals = {
                'email_from': 'thefuturecfo@charterquest.co.za',
                'email_to': email['email'] or email['email_1'],
                'email_cc': 'contributors@thefuturecfo.co.za',
                # 'email_cc':'thefuturecfo@charterquest.co.za',
                'subject': 'Submit Your Quote & Stand A Chance To Be Featured!',
                # 'body_html': email_template_new2_issue,
            }

            res = self.env['mail.mail'].create(mail_vals)
        return True


class ir_ui_view(models.Model):
    _inherit = "ir.ui.view"

    is_magazine = fields.Boolean("Is Magazine")


class subscribe_for_magazine(models.TransientModel):
    _name = 'subscribe.for.magazine'

    def subscribe_customers_magazine(self):
        cfo_obj = self.env['cfo.snr.aspirants']
        partner_obj = self.env['res.partner']
        mail_obj = self.env['mail.mail']
        count = 0
        if self._context and self._context.get('active_model') == 'cfo.aspirants':
            aspirant_ids = self._context.get('active_ids')
            for rec in aspirant_ids:
                cfo_email = cfo_obj.browse(rec).email_1
                count += 1
                if cfo_email:
                    partner_id = cfo_obj.browse(rec).partner_id
                    partner_id.write({'is_subscriber': True, 'email_1': cfo_email})
                    blog = self.env['blog.blog']
                    blog_id = blog.search([('name', '=', "The Future CFO Magazine")])
                    res = blog_id.write({'message_follower_ids': (4, partner_id.id)})
