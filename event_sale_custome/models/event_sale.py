# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, api, _
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp


class product_template(models.Model):
    _inherit = 'product.template'

    event_type_id = fields.Many2one('event.type', string='Type of Event', help='Select event types so when we use this product in sales order lines, it will filter events of this type only.')


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    event_type_id = fields.Many2one('event.type',string="Event Type")

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(sale_order_line, self).product_id_change()
        if self.product_id:
            product_res = self.env['product.product'].browse(self.product_id.id)
            if product_res.event_ok:
                self.event_type_id = product_res.event_type_id.id
                self.event_ok = product_res.event_ok
            else:
                self.event_type_id = False
                self.event_ok = False
        return res

    # @api.one
    # def button_confirm(self):
    #     '''
    #     create registration with sales order
    #     '''
    #     5/0
        # registration_obj = self.env['event.registration']
        # for order_line in self.browse(1):
        #     if order_line.event_id:
        #         dic = {
        #             'name': order_line.order_id.partner_invoice_id.name,
        #             'partner_id': order_line.order_id.partner_id.id,
        #             'nb_register': int(order_line.product_uom_qty),
        #             'email': order_line.order_id.partner_id.email,
        #             'phone': order_line.order_id.partner_id.phone,
        #             'origin': order_line.order_id.name,
        #             'event_id': order_line.event_id.id,
        #             'event_ticket_id': order_line.event_ticket_id and order_line.event_ticket_id.id or None,
        #         }
        #
        #         if order_line.event_ticket_id:
        #             message = _("The registration has been created for event <i>%s</i> with the ticket <i>%s</i> from the Sale Order %s. ") % (order_line.event_id.name, order_line.event_ticket_id.name, order_line.order_id.name)
        #         else:
        #             message = _("The registration has been created for event <i>%s</i> from the Sale Order %s.") % (order_line.event_id.name, order_line.order_id.name)
        #
        #         context.update({'mail_create_nolog': True})
        #         registration_id = registration_obj.create(cr, uid, dic, context=context)
        #         registration_obj.message_post(cr, uid, [registration_id], body=message, context=context)
        # return super(sale_order_line, self).button_confirm(cr, uid, ids, context=context)
