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

from odoo import api,exceptions, fields, models, _
import random
from collections import defaultdict
import werkzeug.urls

class Country(models.Model):
    _inherit = 'res.country'

    active = fields.Boolean(default=True)

class SignupError(Exception):
    pass

def random_token():
    # the token has an entropy of about 120 bits (6 bits/char * 20 chars)
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.SystemRandom().choice(chars) for _ in range(20))

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
    student_number = fields.Char('Student No', size=64)
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
            print("\n\n\n================context========",self._context)
            if self._context.get('cfo_login'):
                partner.signup_url +='&cfo_login=True'
                partner.signup_url +='&is_request=True'
                partner.signup_url +='&team_id=%s'%(self._context.get('team_id'))
                partner.signup_url+='&user_type=%s'%(self._context.get('user_type'))

    def _get_signup_url_for_action(self, action=None, view_type=None, menu_id=None, res_id=None, model=None):
        """ generate a signup url for the given partner ids and action, possibly overriding
            the url state components (menu_id, id, view_type) """
        res = dict.fromkeys(self.ids, False)
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for partner in self:
            # when required, make sure the partner has a valid signup token
            if self.env.context.get('signup_valid') and not partner.user_ids:
                partner.sudo().signup_prepare()
            route = 'login'
            # the parameters to encode for the query
            query = dict(db=self.env.cr.dbname)
            signup_type = self.env.context.get('signup_force_type_in_url', partner.sudo().signup_type or '')
            if signup_type:
                route = 'reset_password' if signup_type == 'reset' else signup_type

            if partner.sudo().signup_token and signup_type:
                query['token'] = partner.sudo().signup_token
            elif partner.user_ids:
                query['login'] = partner.user_ids[0].login
                if partner.user_ids[0].state == 'new':
                    route = 'reset_password'
                if partner.user_ids[0].state == 'active':
                    route = 'login'
                # res[partner.id] = werkzeug.urls.url_join(base_url,
                #                                          "/%s?%s" % (route, werkzeug.urls.url_encode(query)))
                # return res
            else:
                continue  # no signup token, no user, thus no signup url!

            fragment = dict()
            base = '/web#'
            if action == '/mail/view':
                base = '/mail/view?'
            elif action:
                fragment['action'] = action
            if view_type:
                fragment['view_type'] = view_type
            if menu_id:
                fragment['menu_id'] = menu_id
            if model:
                fragment['model'] = model
            if res_id:
                fragment['res_id'] = res_id

            if fragment:
                query['redirect'] = base + werkzeug.urls.url_encode(fragment)
            if route == 'reset_password':
                res[partner.id] = werkzeug.urls.url_join(base_url, "/web/%s?%s" % (route, werkzeug.urls.url_encode(query)))
            if route == 'login':
                res[partner.id] = werkzeug.urls.url_join(base_url,
                                                         "/%s?%s" % (route, werkzeug.urls.url_encode(query)))
        return res

    @api.multi
    def action_signup_prepare(self):
        print("\n\n\n\n\n=============signup_prepare============")
        return self.signup_prepare()

    @api.model
    def get_lecturer(self):
        data=self.env['res.partner'].search_read([('is_lecturer','=',True)],['id','name'])
        return data

    def signup_get_auth_param(self):
        """ Get a signup token related to the partner if signup is enabled.
            If the partner already has a user, get the login parameter.
        """
        res = defaultdict(dict)

        allow_signup = self.env['ir.config_parameter'].sudo().get_param('auth_signup.allow_uninvited',
                                                                        'False').lower() == 'true'
        for partner in self:
            if allow_signup and not partner.user_ids:
                partner = partner.sudo()
                partner.signup_prepare()
                res[partner.id]['auth_signup_token'] = partner.signup_token
            elif partner.user_ids:
                res[partner.id]['auth_login'] = partner.user_ids[0].login
        return res


    @api.multi
    def signup_cancel(self):
        return self.write({'signup_token': False, 'signup_type': False, 'signup_expiration': False})


    @api.multi
    def signup_prepare(self, signup_type="signup", expiration=False):
        """ generate a new token for the partners with the given validity, if necessary
            :param expiration: the expiration datetime of the token (string, optional)
        """
        for partner in self:
            if expiration or not partner.signup_valid:
                token = random_token()
                while self._signup_retrieve_partner(token):
                    token = random_token()
                partner.write({'signup_token': token, 'signup_type': signup_type, 'signup_expiration': expiration})
        return True


    @api.model
    def _signup_retrieve_partner(self, token, check_validity=False, raise_exception=False):
        """ find the partner corresponding to a token, and possibly check its validity
            :param token: the token to resolve
            :param check_validity: if True, also check validity
            :param raise_exception: if True, raise exception instead of returning False
            :return: partner (browse record) or False (if raise_exception is False)
        """
        partner = self.search([('signup_token', '=', token)], limit=1)
        if not partner:
            if raise_exception:
                raise exceptions.UserError(_("Signup token '%s' is not valid") % token)
            return False
        if check_validity and not partner.signup_valid:
            if raise_exception:
                raise exceptions.UserError(_("Signup token '%s' is no longer valid") % token)
            return False
        return partner

    @api.model
    def signup_retrieve_info(self, token):
        """ retrieve the user info about the token
            :return: a dictionary with the user information:
                - 'db': the name of the database
                - 'token': the token, if token is valid
                - 'name': the name of the partner, if token is valid
                - 'login': the user login, if the user already exists
                - 'email': the partner email, if the user does not exist
        """
        partner = self._signup_retrieve_partner(token, raise_exception=True)
        res = {'db': self.env.cr.dbname}
        if partner.signup_valid:
            res['token'] = token
            res['name'] = partner.name
        if partner.user_ids:
            res['login'] = partner.user_ids[0].login
        else:
            res['email'] = res['login'] = partner.email or ''
        return res
# class ResBankType(models.Model):
#     _name = "res.bank.type"
#
#     name = fields.Char(string="Account Type")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
