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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    price = fields.Float(string='Price',
                         digits_compute=dp.get_precision('Product Price')),
    author_id = fields.Many2one('res.partner', 'Author')
    format = fields.Char('Format')
    publisher = fields.Char('Publisher')
    country_id = fields.Many2one('res.country', 'Country of Publication')
    date_of_publish = fields.Date('Date of Publish')
    course_code = fields.Char('Course Code')
    book_edition = fields.Char('Book Edition')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
