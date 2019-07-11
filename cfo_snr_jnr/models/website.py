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
from odoo import models, api, fields, _
from odoo.http import request


class WebsiteMenu(models.Model):
    _inherit = "website.menu"

    @api.multi
    def get_parents(self, revert=False, include_self=False):
        """List current menu's parents.

        :param bool revert:
            Indicates if the result must be revert before returning.
            Activating this will mean that the result will be ordered from
            parent to child.

        :param bool include_self:
            Indicates if the current menu item must be included in the result.

        :return list:
            Menu items ordered from child to parent, unless ``revert=True``.
        """
        result = list()
        menu = self if include_self else self.parent_id
        while menu:
            result.append(menu)
            menu = menu.parent_id
        return reversed(result) if revert else result


class Website(models.Model):
    _inherit = 'website'

    def get_logged_user_detail(self):
        if request.session.get('logged_user'):
            user_rec = self.env['res.users'].browse(request.session.get('logged_user'))
            return user_rec
        return False

    def get_competition_types(self, member=''):
        domain = []
        if member:
            domain.append(('cfo_comp', '=', member))
        res = self.env['cfo.competition'].search(domain)
        return res

    def get_social_media_options(self):
        return ['Facebook', 'Twitter', 'U-tube', 'Linked in', 'Instagram', 'other Social Media']

    def get_cfo_registrants_source(self):
        return ["Social Media", "Google search engine brought me to website",
                "E-banner/Web ad that brought me to website",
                "Website whilst visiting for other matters", "Email Campaign that bought me to the website",
                "Radio/TV", "A friend", "My School/mentor",
                "My Employer/Boss", "Brand Ambassador/Social Media Contestant",
                "Professional Body (CIMA, SAICA, ACCA, CFA Institute)",
                "Other"]

    @api.multi
    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
        self.ensure_one()
        partner = self.env.user.partner_id
        sale_order_id = request.session.get('sale_order_id')
        if not sale_order_id:
            last_order = partner.last_website_so_id
            available_pricelists = self.get_pricelist_available()
            # Do not reload the cart of this user last visit if the cart is no longer draft or uses a pricelist no longer available.
            sale_order_id = last_order.state == 'draft' and last_order.pricelist_id in available_pricelists and last_order.id

        pricelist_id = request.session.get('website_sale_current_pl') or self.get_current_pricelist().id

        if self.env['product.pricelist'].browse(force_pricelist).exists():
            pricelist_id = force_pricelist
            request.session['website_sale_current_pl'] = pricelist_id
            update_pricelist = True

        if not self._context.get('pricelist'):
            self = self.with_context(pricelist=pricelist_id)

        # Test validity of the sale_order_id
        sale_order = self.env['sale.order'].sudo().browse(sale_order_id).exists() if sale_order_id else None



        # create so if needed
        if not sale_order and (force_create or code):
            # TODO cache partner_id session
            pricelist = self.env['product.pricelist'].browse(pricelist_id).sudo()
            so_data = self._prepare_sale_order_values(partner, pricelist)
            sale_order = self.env['sale.order'].sudo().create(so_data)

            # set fiscal position
            if request.website.partner_id.id != partner.id:
                sale_order.onchange_partner_shipping_id()
            else:  # For public user, fiscal position based on geolocation
                country_code = request.session['geoip'].get('country_code')
                if country_code:
                    country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1).id
                    fp_id = request.env['account.fiscal.position'].sudo()._get_fpos_by_region(country_id)
                    sale_order.fiscal_position_id = fp_id
                else:
                    # if no geolocation, use the public user fp
                    sale_order.onchange_partner_shipping_id()

            request.session['sale_order_id'] = sale_order.id

            if request.website.partner_id.id != partner.id:
                partner.write({'last_website_so_id': sale_order.id})

        if sale_order:
            # case when user emptied the cart
            if not request.session.get('sale_order_id'):
                request.session['sale_order_id'] = sale_order.id

            # check for change of pricelist with a coupon
            pricelist_id = pricelist_id or partner.property_product_pricelist.id

            # check for change of partner_id ie after signup
            if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
                flag_pricelist = False
                if pricelist_id != sale_order.pricelist_id.id:
                    flag_pricelist = True
                fiscal_position = sale_order.fiscal_position_id.id

                # change the partner, and trigger the onchange
                sale_order.write({'partner_id': partner.id})
                sale_order.onchange_partner_id()
                sale_order.onchange_partner_shipping_id()  # fiscal position
                sale_order['payment_term_id'] = self.sale_get_payment_term(partner)

                # check the pricelist : update it if the pricelist is not the 'forced' one
                values = {}
                if sale_order.pricelist_id:
                    if sale_order.pricelist_id.id != pricelist_id:
                        values['pricelist_id'] = pricelist_id
                        update_pricelist = True

                # if fiscal position, update the order lines taxes
                if sale_order.fiscal_position_id:
                    sale_order._compute_tax_id()

                # if values, then make the SO update
                if values:
                    sale_order.write(values)

                # check if the fiscal position has changed with the partner_id update
                recent_fiscal_position = sale_order.fiscal_position_id.id
                if flag_pricelist or recent_fiscal_position != fiscal_position:
                    update_pricelist = True

            if code and code != sale_order.pricelist_id.code:
                code_pricelist = self.env['product.pricelist'].sudo().search([('code', '=', code)], limit=1)
                if code_pricelist:
                    pricelist_id = code_pricelist.id
                    update_pricelist = True
            elif code is not None and sale_order.pricelist_id.code:
                # code is not None when user removes code and click on "Apply"
                pricelist_id = partner.property_product_pricelist.id
                update_pricelist = True

            # update the pricelist
            if update_pricelist:
                request.session['website_sale_current_pl'] = pricelist_id
                values = {'pricelist_id': pricelist_id}
                sale_order.write(values)
                for line in sale_order.order_line:
                    if line.exists():
                        sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)
            if 'CB' not in sale_order.name:
                name = sale_order.name + 'CB'
                sale_order.name = name
        else:
            request.session['sale_order_id'] = None
            return self.env['sale.order']

        return sale_order


class WebsiteSuppliers(models.Model):
    _name = 'website.suppliers'

    name = fields.Char(string="Name")
    is_placeholder = fields.Boolean(string="Is Placeholder ?")
    placeholder = fields.Html(string="Placeholder")
    image = fields.Binary(string="Image")
    background_color = fields.Char(string="Background Color of Placeholder")
    height = fields.Char(string="Height", default="50")
    width = fields.Char(string="Width", default="100")
    active = fields.Boolean(string="Active", default=True)


class EnrolmentPlaceholders(models.Model):
    _name = 'enrolment.placeholders'

    name = fields.Char(string="Name")
    page = fields.Selection([
        ('course_page', 'Course Page'),
        ('fees_page', 'Fees Page'),
        ('discount_page', 'Discount Page'),
        ('price_page', 'Price Page'),
        ('registration_page', 'Registration Page'),
        ('payment_page', 'Payment Page'),
        ('fees_page_right_side', 'Fees Page Right Side'),
        ('after_campus', 'After Campus'),
    ], default="course_page", string="Page Visibility")
    is_placeholder = fields.Boolean(string="Is Placeholder ?")
    placeholder = fields.Html(string="Placeholder")
    image = fields.Binary(string="Image")
    background_color = fields.Char(string="Background Color of Placeholder")
    height = fields.Char(string="Height", default="50")
    width = fields.Char(string="Width", default="100")
    active = fields.Boolean(string="Active", default=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
