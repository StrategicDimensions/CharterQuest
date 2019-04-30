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

from odoo import models, fields
from odoo import SUPERUSER_ID, api
import odoo.addons.decimal_precision as dp
from odoo import netsvc
import odoo
import base64


class stock_move(models.Model):
    _inherit = "stock.move"

    state = fields.Selection([('draft', 'New'),
                              ('cancel', 'Cancelled'),
                              ('waiting', 'Waiting Another Move'),
                              ('confirmed', 'Waiting Availability'),
                              ('assigned', 'Available'),
                              ('completed', 'Delivered at Campus'),
                              ('done', 'Delivered to Student/Customer'),
                              ('collected', 'Collected by Driver/Courier'),
                              ], 'Status', readonly=True, select=True, copy=False,
                             help="* New: When the stock move is created and not yet confirmed.\n" \
                                  "* Waiting Another Move: This state can be seen when a move is waiting for another one, for example in a chained flow.\n" \
                                  "* Waiting Availability: This state is reached when the procurement resolution is not straight forward. It may need the scheduler to run, a component to me manufactured...\n" \
                                  "* Available: When products are reserved, it is set to \'Available\'.\n" \
                                  "* Done: When the shipment is processed, the state is \'Done\'.")


class stock_picking(models.Model):
    _inherit = "stock.picking"

    def collected_by_driver(self):
        for pick in self:
            ids2 = [move.id for move in pick.move_lines]

            location_id = self.env['stock.location'].search([('name', 'ilike', 'Driver (Ruddy)'),('usage', '=', 'internal')])
            if location_id:
                pick.move_lines.write({'location_id': location_id.id, 'state': 'collected'})
                # self.pool.get('stock.move').write(cr,uid,ids2,{'state':'collected'})
        return True

    def collected_by_courier(self):
        curr_obj = self
        sale_id = self.env['sale.order'].search([('name', '=', curr_obj.origin)])
        if sale_id:
            sale_obj = self.env['sale.order'].browse(sale_id.id)
        for pick in self:
            ids2 = [move.id for move in pick.move_lines]
            location_id = self.env['stock.location'].search([('name', 'ilike', 'Driver (Courier)')])
            if location_id:
                pick.move_lines.write({'location_id': location_id.id, 'state': 'collected'})
                # self.pool.get('stock.move').write(cr,uid,ids2,{'state':'collected'})
            if (pick.delivery_order_source == 'CharterBooks' or pick.delivery_order_source == 'Enrolments') and (
                    sale_id.pc_exam == False):
                pass
                template_id = self.env['mail.template'].search([('name', '=', 'Delivery Order Collected by Courier')])
                if template_id:
                    email_data = template_id.generate_email(self.id)
                    mail_values = {
                        'email_from': email_data.get('email_from'),
                        'email_cc': email_data.get('email_cc'),
                        'reply_to': email_data.get('reply_to'),
                        'email_to': email_data.get('email_to'),
                        'subject': email_data.get('subject'),
                        'body_html': email_data.get('body_html'),
                        'notification': False,
                        'auto_delete': False,
                        'model': 'stock.picking',
                        'res_id': self.id
                    }
                    mail_obj = self.env['mail.mail'].sudo()
                    msg_id = mail_obj.create(mail_values)
                    msg_id.mail_message_id.body= msg_id.body_html
                    msg_id.send()
                    # mail_message = self.env['mail.template'].send_mail(template_id.id)
        self.write({'state': 'collected'})
        return True


    def delivered_at_campus(self):
        curr_obj = self
        sale_id = self.env['sale.order'].search([('name', '=', curr_obj.origin)])
        if sale_id:
        #     sale_obj = self.pool.get('sale.order').browse(sale_id.id)
            for pick in self:
                ids2 = [move.id for move in pick.move_lines]
                template_id = False
                location_id = self.env['stock.location'].search([('name', 'ilike', 'Campus')])
                if location_id:
                    pick.move_lines.write({'location_id': location_id.id, 'state': 'completed'})
                    # self.pool.get('stock.move').write(cr, uid, ids2, {'location_id': location_id[0], 'state': 'completed'})
                if pick.delivery_order_source == 'CharterBooks' and sale_id.pc_exam == False:
                    template_id = self.env['mail.template'].search([('name', '=', 'Delivered at Campus')])
                elif pick.delivery_order_source == 'Enrolments' and sale_id.pc_exam == False:
                    template_id = self.env['mail.template'].search([('name', '=', 'Enrolments Delivered at Campus')])
                if template_id:
                    email_data = template_id.generate_email(self.id)
                    mail_values = {
                        'email_from': email_data.get('email_from'),
                        'email_cc': email_data.get('email_cc'),
                        'reply_to': email_data.get('reply_to'),
                        'email_to': email_data.get('email_to'),
                        'subject': email_data.get('subject'),
                        'body_html': email_data.get('body_html'),
                        'notification': False,
                        'auto_delete': False,
                        'model': 'stock.picking',
                        'res_id': self.id
                    }
                    mail_obj = self.env['mail.mail'].sudo()
                    msg_id = mail_obj.create(mail_values)
                    msg_id.mail_message_id.body = msg_id.body_html
                    msg_id.send()
                    # mail_message = self.env['mail.mail'].send_mail(template_id.id)
            result = self.write({'state': 'completed'})
            return result


    campus_id = fields.Many2one('res.partner', "Campus", store=True)
    semester = fields.Selection([('1', '1st Semester'), ('2', '2nd Semester'), ('3', '3rd Semester')],
                                 string='Semester', store=True)
    prof_body_id = fields.Many2one('event.type', "Professional Body", store=True)
    sale_order_id =  fields.Many2one('sale.order', 'Sale Order Link', store=True)
    student_number =  fields.Char('Student No', size=64, store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting Availability'),
        ('partially_available', 'Partially Available'),
        ('assigned', 'Ready to Transfer'),
        ('completed', 'Delivered at Campus'),
        ('done', 'Delivered to Student/Customer'),
        ('collected', 'Collected by Driver/Courier'),
    ], string='Status',
        copy=False, index=True, readonly=True, store=True,
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
            " * Cancelled: has been cancelled, can't be confirmed anymore""")
    delivery_order_source =  fields.Selection([('CharterBooks', 'CharterBooks'), ('Enrolments', 'Enrolments')],
                                              'Delivery Order Source')

    def onchange_partner_in(self,partner_id=None):
        if not partner_id:
            return {'value': {'student_number': False}}

        part = self.env['res.partner'].browse(partner_id)
        val = {
            'student_number': part.student_number,

        }
        return {'value': val}


    def create(self, vals):
        if vals.get('origin', False):
            sale_id = self.env['sale.order'].search([('name', '=', vals['origin'])])
            if sale_id:
                if sale_id.quote_type not in ['freequote', 'enrolment'] and not sale_id.pc_exam:
                    vals['delivery_order_source'] = 'CharterBooks'
                else:
                    vals['delivery_order_source'] = 'Enrolments'

        if vals.get('partner_id', False):
            onchangeResult = self.onchange_partner_in(vals['partner_id'])
            vals.update(onchangeResult['value'])
        res = super(stock_picking, self).create(vals)
        return res


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'
    _description = 'Immediate Transfer'

    pick_ids = fields.Many2many('stock.picking', 'stock_picking_transfer_rel')

    def process(self):
        pick_to_backorder = self.env['stock.picking']
        pick_to_do = self.env['stock.picking']

        for picking in self.pick_ids:
            # If still in draft => confirm and assign
            if picking.state == 'draft':
                picking.action_confirm()
                if picking.state != 'assigned':
                    if picking.delivery_order_source == 'CharterBooks':
                        pass
                    else:
                        picking.action_assign()
                        if picking.state != 'assigned':
                            raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
                    if picking.delivery_order_source == 'CharterBooks':
                        move.state = 'done'
            if picking._check_backorder():
                pick_to_backorder |= picking
                continue
            pick_to_do |= picking
        # Process every picking that do not require a backorder, then return a single backorder wizard for every other ones.
        if pick_to_do:
            if pick_to_do.delivery_order_source == 'CharterBooks':
                pick_to_do.state = 'done'
                template_id = self.env['mail.template'].search([('name', '=', 'Delivered to Student')])
                if template_id:
                    email_data = template_id.generate_email(pick_to_do.id)
                    mail_values = {
                        'email_from': email_data.get('email_from'),
                        'email_cc': email_data.get('email_cc'),
                        'reply_to': email_data.get('reply_to'),
                        'email_to': email_data.get('email_to'),
                        'subject': email_data.get('subject'),
                        'body_html': email_data.get('body_html'),
                        'notification': False,
                        'auto_delete': False,
                        'model': 'stock.picking',
                        'res_id': pick_to_do.id
                    }
                    mail_obj = self.env['mail.mail'].sudo()
                    msg_id = mail_obj.create(mail_values)
                    msg_id.mail_message_id.body = msg_id.body_html
                    msg_id.send()
            else:
                pick_to_do.action_done()
        if pick_to_backorder:
            return pick_to_backorder.action_generate_backorder_wizard()
        return False
