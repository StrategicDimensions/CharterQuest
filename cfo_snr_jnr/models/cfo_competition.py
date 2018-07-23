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

from odoo import models,fields, _

class CFOCompetition(models.Model):
    _name = 'cfo.competition'
    _inherit = ['mail.thread']

    name = fields.Char('Name')
    cfo_comp = fields.Selection([('CFO SNR', 'CFO SNR'), ('CFO JNR', 'CFO JNR')], 'Competition')


class CFOConfiguration(models.Model):
    _name = 'cfo.configuration'
    _inherit = ['mail.thread']

    name = fields.Char('Name')
    cfo_member_type = fields.Selection([('CFO Aspirant', 'CFO Aspirant'),
                             ('Academic Institution', 'Academic Institution'),
                             ('Employer', 'Employer'),
                             ('Volunteer', 'Volunteer'),
                             ('Brand Ambassador', 'Brand Ambassador'),
                             ('Social Media Contestant', 'Social Media Contestant'),
                             ('Mentor', 'Mentor'),
                             ('Secondary/High School','Secondary/High School')],
                             'Type')
    cfo_competitions = fields.Many2one('cfo.competition', string='CFO Competitions')
    cfo_comp = fields.Selection([('CFO SNR', 'CFO SNR'), ('CFO JNR', 'CFO JNR')], 'Competition')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
