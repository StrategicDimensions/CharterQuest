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
from odoo import models, _
from odoo.http import request


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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
