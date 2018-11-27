# -*- coding: utf-8 -*-

from odoo import fields, models, api,  _
from datetime import date, datetime, timedelta


class event_discounts(models.Model):
    _name = "event.discount"

    name = fields.Char("Name", size=56)
    discount = fields.Float("Discount %")
    event_type_id = fields.Many2one('event.type', "Event Type")
    description = fields.Text("Description")
    discount_type = fields.Selection([('1', 'Returning Student'),
                                      ('combo_2', 'COMBO 2'),
                                      ('combo_3', 'COMBO 3'),
                                      ('combo_4', 'COMBO 4')])
    # order_id = fields.Many2one('sale.order', 'Order Reference', required=True, ondelete='cascade', select=True, readonly=True, states={'draft':[('readonly', False)]})
    condition = fields.Text("Conditions")


class event_max_discount(models.Model):
    _name = "event.max.discount"

    date = fields.Date(string='Date', default=fields.Date.context_today)
    max_discount = fields.Float("Max Discount %",help="Maximum discount allowed on event registration in Portal")
    prof_body = fields.Many2one('event.type', string="Professional Body")


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.model
    def send_early_bird_discount_email(self):
        """ This Function is used to send the Early Bird Discount
        Expiry Notification to Student."""
        today = datetime.today()
        this_first = date(today.year, today.month, 1)
        prev_end = this_first - timedelta(days=3)
        prev_first = date(prev_end.year, prev_end.month, 1)
        month = today.strftime('%m')
        sale_ids = self.search([('state', '=', 'draft'),
                                ('create_date', '>=', str(prev_first)),
                                ('create_date', '<=', str(prev_end)),
                                ('affiliation', '=', '1')])
        for sale_id in sale_ids:
            list = []
            if sale_id.discount_type_ids:
                discount = 0.0
                for event_obj in sale_id.discount_type_ids:
                    max_disc = self.env['event.discount'].search([('name', '=', 'Early Bird Discount')])
                    max_discount_id = max_disc and max_disc[0] or False
                    if event_obj.id == max_discount_id.id:
                        template_id = self.env['mail.template'].search([('name', '=', "Early Bird DISCOUNT EXPIRY NOTICE")])
                        if template_id:
                            mail_message = template_id.send_mail(sale_id)
        return True

    @api.model
    def get_early_bird_discount(self):
          today = datetime.today()
          this_first = date(today.year, today.month, 1)
          prev_end = this_first - timedelta(days=1)
          prev_first = date(prev_end.year, prev_end.month, 1)
          month = today.strftime('%m')
          sale_ids = self.search([('state','=','draft'),('create_date','>=',str(prev_first)),('create_date','<=',str(prev_end)),('affiliation','=','1')])

          for sale_id in sale_ids:
              sale_obj = self.browse(sale_id.id)
              list = []
              if sale_obj.discount_type_ids:
                 discount = 0.0
                 for event_obj in sale_obj.discount_type_ids:
                     max_disc = self.env['event.discount'].search([('name', '=', 'Early Bird Discount'),
                                                                   ('event_type_id', '=', sale_obj.prof_body.id)])
                     max_discount_id = max_disc and max_disc[0] or False
                     if event_obj.id != max_discount_id:
                         list.append(event_obj.id)
                         discount += event_obj.discount
                 sale_id.write({'discount_type_ids':[(6,0,list)],'discount':discount})
                 message = self.env['mail.message']
                 if sale_obj.message_ids[0]:
                    message.create({
                                  'res_id': sale_obj.message_ids[0].res_id,
                                   'parent_id':sale_obj.message_ids[0].id,
                                   'subject' : 'Early Bird Discount Removed from Quote',
                                   'model':'sale.order',
                                   'body':'Early Bird Discount Removed from Quote'
                           })
          return True

    @api.model
    def send_early_settlement_discount_email(self):
        today = date.today()
        sale_ids = self.search([('state', '=', 'draft'), ('affiliation', '=', '1')])
        #  sale_ids = [1937]
        for sale_id in sale_ids:
            list = []
            createdate = datetime.strptime(sale_id.create_date, "%Y-%m-%d %H:%M:%S")
            after7_days = today - createdate.date()
            if after7_days.days == 5:
                if sale_id.discount_type_ids:
                    discount = 0.0
                    for event_obj in sale_id.discount_type_ids:
                        max_disc = self.env['event.discount'].search([('name', '=', 'Early Settlement Discount'), ('event_type_id','=', sale_id.prof_body.id)])
                        max_discount_id = max_disc and max_disc[0] or False
                        if event_obj.id == max_discount_id:
                            template_id = self.env['mail.template'].search([('name', '=', "Early Settelement DISCOUNT EXPIRY NOTICE")])
                            if template_id:
                                mail_message = template_id.send_mail(sale_id)
        return True

    @api.model
    def get_early_settlement_discount(self):
          today = date.today()
          sale_ids = self.search([('state', '=', 'draft'), ('affiliation', '=', '1')])
          for sale_id in sale_ids:
              list = []
              createdate = datetime.strptime(sale_id.create_date,"%Y-%m-%d %H:%M:%S")
              after7_days = today - createdate.date()
              if after7_days.days > 7:
                 if sale_id.discount_type_ids:
                     discount = 0.0
                     for event_obj in sale_id.discount_type_ids:
                         max_disc = self.env['event.discount'].search([('name', '=', 'Early Settlement Discount'),
                                                                            ('event_type_id', '=', sale_id.prof_body.id)])
                         max_discount_id = max_disc and max_disc[0] or False
                         if event_obj.id != max_discount_id:
                             list.append(event_obj.id)
                             discount += event_obj.discount
                     sale_id.write({'discount_type_ids': [(6, 0, list)], 'discount': discount})
                     message = self.env['mail.message']
                     if sale_id.message_ids[0]:
                          message.create({
                            'res_id': sale_id.message_ids[0].res_id,
                            'parent_id': sale_id.message_ids[0].id,
                            'subject': 'Early Settlement Discount Removed from Quote',
                            'model': 'sale.order',
                            'body': 'Early Settlement Discount Removed from Quote'
                           }, self._context)
          return True

    # @api.multi
    # def _get_default_discount(self):
    #     max_disc = self.env['event.discount'].search([('name', '=', 'Early Bird Discount')])
    #     max_discount_id = max_disc and max_disc.id or False
    #     result = [(6, 0, [max_discount_id])]
    #     return result

        # max_disc_obj = self.env['event.max.discount'].browse(max_disc)
        # discount = max_disc_obj.max_discount

    discount_type_ids = fields.Many2many('event.discount', string="Discount Types")
    discount = fields.Float("Discount %")

    # @api.onchange('discount_type_ids')
    # def onchange_discount_type(self):
    #       if not self.discount_type_ids:
    #             return {'values': {'discount': 0.0}}
    #       event_discount = self.env['event.discount']
    #       if self.discount_type_ids:
    #             discount = 0.0
    #             for obj in self.discount_type_ids:
    #                  discount += obj.discount
    #       max_disc = False
    #       today = str(date.today())
    #       event_max_discount_ids = self.env['event.max.discount'].search([('date','<=',today)])
    #       if len(event_max_discount_ids) >= 2:
    #             event_max_discount_ids = [max(event_max_discount_ids)]
    #             if event_max_discount_ids.max_discount and discount > max_disc:
    #                 discount = max_disc
    #       return {'value': {'discount': discount}}

    @api.multi
    def write(self, vals):
        if vals.get('discount', False) and vals.get('discount') >= 0.0:
            order_id = self.id
            if isinstance(self.id,int):
                order_id = [self.id]
            order_line_ids = self.env['sale.order.line'].search([('order_id', '=', order_id)])
            line_ids = []
            for obj in self.env['sale.order.line'].browse(order_line_ids):
                if not obj.product_id.fee_ok:
                    line_ids.append(obj.id)
            self.env['sale.order.line'].write(line_ids, {'discount': vals['discount']})
        return super(sale_order, self).write(vals)


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def create(self, vals, context=None):
        if vals.get('product_id', False):
            if not self.env['product.product'].browse(vals['product_id']).fee_ok:
                discount = self.env['sale.order'].browse(vals['order_id']).discount
                vals['discount'] = discount
                return super(sale_order_line, self).create(vals)
        return super(sale_order_line, self).create(vals)



class product_product(models.Model):
    _inherit = 'product.product'

    does_not_apply = fields.Selection([('return_student','Returning Student'),('new_student','New Student')],'Does not apply to')
    pcexam_voucher = fields.Boolean('PC Exam Voucher')
    no_vouchers = fields.Integer('No of Vouchers')
    voucher_value = fields.Float('Voucher Value')
