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

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _work_exp_values(self):
        res = []
        for i in range(0, 6):
            res.append((str(i), str(i)))
        return res

    first_name = fields.Char('First Name')
    surname = fields.Char('Surname')
    other_names = fields.Char('Other Names')
    home_phone = fields.Char('Home Telephone')
    email_1 = fields.Char('Primary Email')
    email_2 = fields.Char('Secondary Email')
    school_name = fields.Char('Legal/Registered name School/College/University')
    department = fields.Char('Department/Faculty/Unit')
    programme_name = fields.Char('Programme Name')
    start_date = fields.Date('Start Date')
    expected_completion_date = fields.Date('Expected Completion Date')
    mode_of_studies = fields.Selection([('Part Time', 'Part Time'), ('Full Time', 'Full Time')], 'Mode of Studies')
    formal_work_exp = fields.Selection(_work_exp_values, 'How many years of formal work experience?')
    tertiary_qualification = fields.Selection(
        [('none', 'None'), ('current studies', 'current studies'), ('Bachelor degree', 'Bachelor degree'),
         ('Professional Qualification', 'Professional Qualification')], 'Prior tertiary Qualification')
    field_of_studies = fields.Char('Field of studies')
    pre_tertiary_qualification = fields.Char('Pre tertiary qualification')
    date_of_birth = fields.Date('Date of Birth')
    stu_street = fields.Char('Street')
    stu_street2 = fields.Char('Street2')
    stu_zip = fields.Char('Zip', size=24, change_default=True)
    stu_city = fields.Char('City')
    stu_state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
    stu_country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
    emp_street = fields.Char('Street')
    emp_street2 = fields.Char('Street2')
    emp_zip = fields.Char('Zip', size=24, change_default=True)
    emp_city = fields.Char('City')
    emp_state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
    emp_country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
    sector = fields.Selection([('Private sector', 'Private sector'), ('Public sector', 'Public sector'), ('NGO', 'NGO'),
                               ('Other NFPO', 'Other NFPO')], 'Sector')
    legal_name_employer = fields.Char('Legal/Registered name of Employer')
    if_company = fields.Selection([('Listed', 'Listed'), ('Not Listed', 'Not Listed')], 'If company: Listed or not?')
    emp_department = fields.Char('Department/Unit')
    emp_website = fields.Char('Website of Employer')
    username = fields.Char('Username')
    password = fields.Char('Password')
    cfo_type = fields.Selection(
        [('CFO Aspirant', 'CFO Aspirant'), ('Academic Institution', 'Academic Institution'), ('Employer', 'Employer'),
         ('Volunteer', 'Volunteer'), ('Brand Ambassador', 'Brand Ambassador'),
         ('Social Media Contestant', 'Social Media Contestant'), ('Fyla', 'Fyla'),
         ('Secondary/High School', 'Secondary/High School')], 'Type')
    cfo_account_activate = fields.Boolean('CFO Account Active')
    cfo_encoded_link = fields.Char('CFO Encoded Link')
    team_leader = fields.Boolean('Team Leader')
    team_admin = fields.Boolean('Team Admin')
    team_member = fields.Boolean('Team Member')
    registrants_source = fields.Selection([('Social Media', 'Social Media'), (
        'Google search engine brought me to website', 'Google search engine brought me to website'), (
                                               'E-banner/Web ad that brought me to website',
                                               'E-banner/Web ad that brought me to website'), (
                                               'Website whilst visiting for other matters',
                                               'Website whilst visiting for other matters'), (
                                               'Email Campaign that bought me to the website',
                                               'Email Campaign that bought me to the website'),
                                           ('Radio/TV', 'Radio/TV'),
                                           ('A friend', 'A friend'), ('My School/mentor', 'My School/mentor'),
                                           ('My Employer/Boss', 'My Employer/Boss'), (
                                               'Brand Ambassador/Social Media Contestant',
                                               'Brand Ambassador/Social Media Contestant'), (
                                               'Professional Body (CIMA, SAICA, ACCA, CFA Institute)',
                                               'Professional Body (CIMA, SAICA, ACCA, CFA Institute)'),
                                           ('Other', 'Other')],
                                          'How did you 1st learn about the CFO')
    social_media_options = fields.Selection(
        [('Facebook', 'Facebook'), ('Twitter', 'Twitter'), ('U-tube', 'U-tube'), ('Linked in', 'Linked in'),
         ('Instagram', 'Instagram'), ('other Social Media', 'other Social Media')], 'Social Media Options')
    other_reason = fields.Char('Other Reason')
    external_panel_judge = fields.Boolean('Volunteer as External Panel Judge')
    external_examiner = fields.Boolean('External Examiner')
    case_study_exper = fields.Boolean('Case study expert & other expertise')
    ai_and_employer = fields.Boolean('AI & Employer')
    brand_ambassador = fields.Boolean('Brand Ambassador')
    mentor = fields.Boolean('Mentor')
    social_media_contestant = fields.Boolean('Social Media Contestant')
    volunteer_as_student = fields.Boolean('Volunteer as Student')
    volunteer_other_expertise = fields.Boolean('Volunteer Other Expertise')

    is_residential_address = fields.Boolean("Same as residential address")
    post_street = fields.Char('Street')
    post_street2 = fields.Char('Street2')
    post_zip = fields.Char('Zip', size=24, change_default=True)
    post_city = fields.Char('City')
    post_state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
    post_country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
    is_from_new_member = fields.Boolean(string = 'IS From New Member')
    # cfo junior
    # 'is_cfo_junior = fields.boolean("Is CFO Junior"),
    race = fields.Selection(
        [('Black', 'Black'), ('Coloured', 'Coloured'), ('Indian/Asian', 'Indian/Asian'), ('White', 'White'),
         ('Other', 'Other')], string="Race")
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female')], string="Gender")
    parent_name = fields.Char('Name')
    parent_email = fields.Char('Email')
    parent_number = fields.Char('Number')
    parent_occupation = fields.Char('Occupation')
    junior_school_name_1 = fields.Char('School Name1')
    junior_school_name_2 = fields.Char('School Name2')
    programme_name_junior = fields.Selection(
        [('IEB Matric', 'IEB Matric'), ('Public Matric', 'Public Matric'), ('Cambridge IGCSE', 'Cambridge IGCSE'),
         ('Cambridge AS Level', 'Cambridge AS Level'), ('Cambridge A Level', 'Cambridge A Level'), ('Other', 'Other')],
        "Programme Name")
    cfo_user = fields.Boolean(string="Cfo User")
    charterquest_tags = fields.Many2many('res.partner.category','charter_quest_rel',string='Charterquest Tags')
    # cfo junior ends
    ##Mearging by Raaj
    cfo_categ = fields.Selection([('CFO', 'CFO'), ('CFO Junior', 'CFO Junior')], 'CFO Category')

    _sql_constraints = [('email_1_uniq', 'unique(email_1)', 'Already this email has been registered')]

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id
            
            
    @api.multi
    def _compute_signup_url(self):
        """ proxy for function field towards actual implementation """
        result = self._get_signup_url_for_action()
        for partner in self:
            partner.signup_url = result.get(partner.id, False)
            if self._context.get('cfo_login'):
                partner.signup_url +='&cfo_login=True' 
                
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
