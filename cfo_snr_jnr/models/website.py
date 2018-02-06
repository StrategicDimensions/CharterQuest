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

#     def get_member_types(self,val):
#         print('cfo_competition==========',val)
#         return self.env['cfo.configuration'].search([])

    def get_cfo_registrants_source(self):
        return ["Social Media","Direct web address","Google/other search engine",
                "E-banner/Web advertisement","Email campaign/Signature card with link",
                "Person Vue website/exam booking page","Other website listing","Radio/TV",
                "Print Media","Direct mail via the post","Word-of-mouth/current/prior CharterQuest Student",
                "My school/mentor/friend","My Employer/Boss/Supervisor","Brand Ambassador",
                "Professional Body (CIMA, SAICA, ACCA, CFA Institute)","Billboard/street post/community center/church",
                "Other(please specify)"]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: