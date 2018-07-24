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
    'name': 'CFO Senior Junior',
    'version': '1.0',
    'category': 'Website',
    'summary': 'CFO Senior and Junior Competition',
    'description': """CFO Senior and Junior Competition.""",
    'depends': ['base', 'auth_signup', 'crm', 'website', 'web_editor', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'data/snippets.xml',
        'views/login.xml',
        'views/login_cfo_jnr.xml',
        'views/jsfile.xml',
        'views/competition_view.xml',
        'views/cfo_junior_member_view.xml',
        'views/cfo_senior_member_view.xml',
        'views/cfo_team_view.xml',
        'views/menus.xml',
        'views/res_partner.xml',
        'data/email_template.xml',
        'data/ir_cron.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
