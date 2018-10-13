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


{
    'name': 'Events Sales Custome',
    'version': '11.0.1',
    'category': 'Tools',
    'sequence':2,
    'website' : 'https://www.odoo.com/page/events',
    'description': """
Creating registration with sale orders.
=======================================

This module allows you to automate and connect your registration creation with
your main sale flow and therefore, to enable the invoicing feature of registrations.

It defines a new kind of service products that offers you the possibility to
choose an event category associated with it. When you encode a sale order for
that product, you will be able to choose an existing event of that category and
when you confirm your sale order it will automatically create a registration for
this event.
""",
    'author': 'OpenERP SA',
    'depends': ['event', 'sale_management', 'account'],
    'data': [
        # 'views/event_demo.xml',
        'views/event_sale_view.xml',
        # 'views/event_sale_data.xml',
        'views/event_sale_report.xml',
        'report/report_registrationbadge.xml',
        'security/ir.model.access.csv',
    ],
    # 'test': ['test/confirm.yml'],
    'installable': True,
    'auto_install': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
