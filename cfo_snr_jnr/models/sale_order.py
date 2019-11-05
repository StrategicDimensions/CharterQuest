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
from odoo.tools import float_compare
from odoo.http import request
from odoo.exceptions import UserError, Warning, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    due_day = fields.Integer(string='Due Day')

    @api.multi
    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        OrderLine = self.env['sale.order.line']

        if line_id:
            line = OrderLine.browse(line_id)
            ticket = line.event_ticket_id
            old_qty = int(line.product_uom_qty)
            if ticket.id:
                self = self.with_context(event_ticket_id=ticket.id, fixed_price=1)
        else:
            line = None
            ticket = self.env['event.event.ticket'].search([('product_id', '=', product_id)], limit=1)
            old_qty = 0
        new_qty = set_qty if set_qty else (add_qty or 0 + old_qty)

        # case: buying tickets for a sold out ticket
        values = {}
        if ticket and ticket.seats_availability == 'limited' and ticket.seats_available <= 0:
            values['warning'] = _('Sorry, The %(ticket)s tickets for the %(event)s event are sold out.') % {
                'ticket': ticket.name,
                'event': ticket.event_id.name}
            new_qty, set_qty, add_qty = 0, 0, 0
        # case: buying tickets, too much attendees
        elif ticket and ticket.seats_availability == 'limited' and new_qty > ticket.seats_available:
            values['warning'] = _(
                'Sorry, only %(remaining_seats)d seats are still available for the %(ticket)s ticket for the %(event)s event.') % {
                                    'remaining_seats': ticket.seats_available,
                                    'ticket': ticket.name,
                                    'event': ticket.event_id.name}
            new_qty, set_qty, add_qty = ticket.seats_available, ticket.seats_available, 0
        values.update(super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs))

        # removing attendees
        if ticket and new_qty < old_qty:
            attendees = self.env['event.registration'].search([
                ('state', '!=', 'cancel'),
                ('sale_order_id', 'in', self.ids),  # To avoid break on multi record set
                ('event_ticket_id', '=', ticket.id),
            ], offset=new_qty, limit=(old_qty - new_qty), order='create_date asc')
            attendees.button_reg_cancel()
        # adding attendees
        elif ticket and new_qty > old_qty:
            line = OrderLine.browse(values['line_id'])
            line._update_registrations(confirm=False, cancel_to_draft=True,
                                       registration_data=kwargs.get('registration_data', []))
            # add in return values the registrations, to display them on website (or not)
            values['attendee_ids'] = self.env['event.registration'].search(
                [('sale_order_line_id', '=', line.id), ('state', '!=', 'cancel')]).ids
        return values

    # @api.multi
    # def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, attributes=None, warehouse_id= 0, **kwargs):
    #     """ Add or set product quantity, add_qty can be negative """
    #     self.ensure_one()
    #
    #     SaleOrderLineSudo = self.env['sale.order.line'].sudo()
    #
    #     try:
    #         if add_qty:
    #             add_qty = float(add_qty)
    #     except ValueError:
    #         add_qty = 1
    #     try:
    #         if set_qty:
    #             set_qty = float(set_qty)
    #     except ValueError:
    #         set_qty = 0
    #     quantity = 0
    #     order_line = False
    #     if self.state != 'draft':
    #         request.session['sale_order_id'] = None
    #         raise UserError(_('It is forbidden to modify a sales order which is not in draft status'))
    #     if line_id is not False:
    #         order_lines = self._cart_find_product_line(product_id, line_id, **kwargs)
    #         order_line = order_lines and order_lines[0]
    #
    #     # Create line if no line with product_id can be located
    #     if not order_line:
    #         values = self._website_product_id_change(self.id, product_id, qty=1)
    #         values['name'] = self._get_line_description(self.id, product_id, attributes=attributes)
    #
    #         values['product_warehouse_id'] = int(warehouse_id) if warehouse_id else ''
    #         order_line = SaleOrderLineSudo.create(values)
    #
    #         try:
    #             order_line._compute_tax_id()
    #         except ValidationError as e:
    #             # The validation may occur in backend (eg: taxcloud) but should fail silently in frontend
    #             _logger.debug("ValidationError occurs during tax compute. %s" % (e))
    #         if add_qty:
    #             add_qty -= 1
    #
    #     # compute new quantity
    #     if set_qty:
    #         quantity = set_qty
    #     elif add_qty is not None:
    #         quantity = order_line.product_uom_qty + (add_qty or 0)
    #
    #     # Remove zero of negative lines
    #     if quantity <= 0:
    #         order_line.unlink()
    #     else:
    #         # update line
    #         values = self._website_product_id_change(self.id, product_id, qty=quantity)
    #         if not warehouse_id and order_line.product_warehouse_id:
    #             warehouse_id = order_line.product_warehouse_id
    #         values['product_warehouse_id'] = int(warehouse_id or 0)
    #         if self.pricelist_id.discount_policy == 'with_discount' and not self.env.context.get('fixed_price'):
    #             order = self.sudo().browse(self.id)
    #             product_context = dict(self.env.context)
    #             product_context.setdefault('lang', order.partner_id.lang)
    #             product_context.update({
    #                 'partner': order.partner_id.id,
    #                 'quantity': quantity,
    #                 'date': order.date_order,
    #                 'pricelist': order.pricelist_id.id,
    #             })
    #             product = self.env['product.product'].with_context(product_context).browse(product_id)
    #             values['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
    #                 order_line._get_display_price(product),
    #                 order_line.product_id.taxes_id,
    #                 order_line.tax_id,
    #                 self.company_id
    #             )
    #
    #         order_line.write(values)
    #
    #     return {'line_id': order_line.id, 'quantity': quantity}





class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_warehouse_id = fields.Many2one('stock.warehouse', string="Product Warehouse")

    @api.multi
    def _action_launch_procurement_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        sale order line. procurement group will launch '_run_move', '_run_buy' or '_run_manufacture'
        depending on the sale order line product rule.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        errors = []
        for line in self:

            if line.state != 'sale' or not line.product_id.type in ('consu', 'product'):
                continue
            qty = 0.0
            for move in line.move_ids.filtered(lambda r: r.state != 'cancel'):
                qty += move.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            group_id = line.order_id.procurement_group_id
            if not group_id:
                group_id = self.env['procurement.group'].create({
                    'name': line.order_id.name, 'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = group_id
            else:
                # In case the procurement group is already created and the order was
                # cancelled, we need to update certain values of the group.
                updated_vals = {}
                if group_id.partner_id != line.order_id.partner_shipping_id:
                    updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
                if group_id.move_type != line.order_id.picking_policy:
                    updated_vals.update({'move_type': line.order_id.picking_policy})
                if updated_vals:
                    group_id.write(updated_vals)

            values = line._prepare_procurement_values(group_id=group_id)
            # if line.product_warehouse_id:
            #     values['warehouse_id'] = line.product_warehouse_id

            product_qty = line.product_uom_qty - qty
            try:
                self.env['procurement.group'].run(line.product_id, product_qty, line.product_uom,
                                                  line.order_id.partner_shipping_id.property_stock_customer, line.name,
                                                  line.order_id.name, values)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return True


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_assign(self):
        self.filtered(lambda picking: picking.state == 'draft').action_confirm()
        moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        quant_ids = self.env['stock.quant'].sudo().search([('location_id', '=', self.location_id.id), (
        'product_id', 'in', [each.product_id.id for each in moves])])
        quantity_total = 0.0
        reserved_quantity_total = 0.0

        for each in quant_ids:
            quantity_total += each.quantity
            reserved_quantity_total += each.reserved_quantity

        if reserved_quantity_total >= quantity_total:
            raise Warning(_('There is no stock in current warehouse "%s"') % self.location_id.display_name)
        if not quantity_total:
            raise Warning(_('There is no stock in current warehouse "%s"') %self.location_id.display_name)

        if not moves:
            raise UserError(_('Nothing to check the availability for.'))
        moves._action_assign()
        return True

    @api.multi
    def button_validate(self):
        if not self.env.user.has_group('cfo_snr_jnr.stock_transfer'):
            raise Warning(_("You cannot validate a transfer."))
        return super(Picking, self).button_validate()