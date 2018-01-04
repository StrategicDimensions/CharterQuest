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

class CFOMember(models.Model):
    _name = 'cfo.member'
    _inherit = ['mail.thread']
#     _rec_name = aspirants_name

    name = fields.Char('Name', required=True)
    aspirants_name = fields.Many2one('res.partner', 'Name', required=True)
    other_names = fields.Char('Other Names')
    birth_country = fields.Many2one('res.country', 'Country of Birth')
    cfo_comp = fields.Selection([('CFO SNR', 'CFO SNR'), ('CFO JNR', 'CFO JNR')], 'Competition')
    mobile = fields.Char('Mobile')
    home_phone = fields.Char('Home Phone')
    street = fields.Char('Address')
    street2 = fields.Char('Street2')
    city = fields.Char('City')
    province = fields.Many2one('res.country.state', 'Province')
    zip = fields.Char('Zip')
    country = fields.Many2one('res.country', 'Country')
    programme_name = fields.Char('Programme Name')
    
    aspirants_email = fields.Char('Primary Email')
    secondary_email = fields.Char('Secondary Email')
    birth_date = fields.Date('Date of Birth')
    nationality = fields.Many2one('res.country', 'Current Citizenship/Nationality')
    office_telephone = fields.Char('Office Telephone')
    entry_type = fields.Selection([('Student', 'Student'), ('Employee', 'Employee')], 'I am entering as')
    age = fields.Selection([('14', '14'),
                           ('15', '15'),
                           ('16', '16'),
                           ('17', '17'),
                           ('18', '18'),
                           ('19', '19'),
                           ('20', '20'),
                           ('21', '21'),
                           ('22', '22'),
                           ('23', '23'),
                           ('24', '24'),
                           ('25', '25'),
                           ], 'Age')
    college_university = fields.Char('Legal/Registered Name College/University')
    unit  =fields.Char('Department/Faculty/Unit')
    website  =fields.Char('Website')
    college_street = fields.Char('Address')
    college_street2 = fields.Char('Street2')
    college_city = fields.Char('City')
    college_province = fields.Many2one('res.country.state', 'Province')
    college_zip = fields.Char('Zip')
    college_country = fields.Many2one('res.country', 'Country')
    cfo_team = fields.Many2one('cfo.team', 'CFO Snr Teams')

    cfo_member_type = fields.Selection([('CFO Aspirant', 'CFO Aspirant'),
                             ('Academic Institution', 'Academic Institution'),
                             ('Employer', 'Employer'),
                             ('Volunteer', 'Volunteer'),
                             ('Brand Ambassador', 'Brand Ambassador'),
                             ('Social Media Contestant', 'Social Media Contestant'),
                             ('Mentor', 'Mentor'),
                             ('Secondary/High School','Secondary/High School')],
                             'Type')
    cfo_comp = fields.Selection([('CFO SNR', 'CFO SNR'), ('CFO JNR', 'CFO JNR')], 'Competition')
    cfo_competition_year = fields.Selection([('2016', '2016'),('2017', '2017'),('2018', '2018'),('2019', '2019'),('2020', '2020')], 'Year')


class CFOTeam(models.Model):
    _name = 'cfo.team'
 
    name = fields.Char('Name')
    cfo_comp = fields.Selection([('CFO SNR', 'CFO SNR'), ('CFO JNR', 'CFO JNR')], 'Competition')
    cfo_competition_year = fields.Selection([('2016', '2016'),('2017', '2017'),('2018', '2018'),('2019', '2019'),('2020', '2020')], 'Year')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
