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

from odoo import models, fields, _, api


class CFOSeniorAspirants(models.Model):
    _name = 'cfo.snr.aspirants'
    _inherit = ['mail.thread']

    _inherits = {
        'res.partner': 'partner_id',
    }

    def _work_exp_values(self):
        res = []
        for i in range(0, 6):
            res.append((str(i), str(i)))
        return res

    def _compute_age(self):
        res = []
        for i in range(14, 26):
            res.append((str(i), str(i)))
        return res

    doc_lines = fields.One2many('ir.attachment', 'aspirant_doc_id', 'Documents')
    country_of_birth = fields.Many2one('res.country', 'Country of Birth')
    nationality = fields.Many2one('res.country', 'Current Citizenship/Nationality')
    entry_as_student = fields.Boolean('I am entering as Student')
    entry_as_employee = fields.Boolean('I am entering as Employee')
    emp_start_date = fields.Date('Start Date')
    emp_status = fields.Selection([('part-time', 'part-time'), ('full-time', 'full-time')], 'Employment Status')
    emp_experience = fields.Selection(_work_exp_values, 'How many years of formal work experience?')
    partner_id = fields.Many2one('res.partner',
                                 string='Name', ondelete='restrict',
                                 help='Partner-related data of the user', domain=[('cfo_user', '=', True)])
    updated_cfo_bio = fields.Boolean('Updated CFO BIO')
    aspirant_id = fields.Many2one('cfo.team.snr', 'Aspirant ID')
    aspirant_age = fields.Selection(_compute_age, 'Age')
    member_accept = fields.Boolean('Accept')
    user_id = fields.Many2one('res.users', 'Related User')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')
    is_request = fields.Boolean('Request to join')
    new_team_id = fields.Many2one('cfo.team.snr')
    team_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept')],
                                   string="Status")
    is_from_create_member = fields.Boolean(string = "Is From Create Member")
    #     is_cfo_junior = fields.Boolean("Is CFO Junior")
    

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            if user:
                self.user_id = user.id

    @api.multi
    def accept_request(self):
        self.aspirant_id = self.new_team_id.id
        self.is_request = False

    @api.multi
    def accept_team(self):
        self.aspirant_id = self.new_team_id
        self.team_status = 'Accept'
        member = self.env['snr.aspirant.team.member'].sudo().search([('team_id', '=', self.aspirant_id.id),
                                                                     ('related_user_id', '=', self.id)])
        if member:
            member.sudo().write({
                'member_status': 'Accept'
            })

    @api.multi
    def reject_team(self):
        self.aspirant_id = False
        self.team_status = 'Rejected'
        member = self.env['snr.aspirant.team.member'].sudo().search([('team_id', '=', self.aspirant_id.id),
                                                                     ('related_user_id', '=', self.id)])
        if member:
            member.sudo().write({
                'member_status': 'Accept'
            })


class AcademicInstitutionSenior(models.Model):
    _name = 'academic.institution.snr'
    _inherit = ['mail.thread']

    _inherits = {
        'res.partner': 'partner_id',
    }

    doc_lines = fields.One2many('ir.attachment', 'academic_doc_id', 'Documents')
    partner_id = fields.Many2one('res.partner',
                                 string='Name', ondelete='restrict',
                                 help='Partner-related data of the user', domain=[('cfo_user', '=', True)])
    updated_academic_bio = fields.Boolean('Updated Academic BIO')
    user_id = fields.Many2one('res.users', 'Related User')
    ref_name = fields.Char(string = 'Reference')
    cfo_team_ids = fields.Many2many('cfo.team.snr','cfo_team_rel', string='Acadamic ID')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            if user:
                self.user_id = user.id


class EmployersSenior(models.Model):
    _name = 'employers.snr'
    _inherit = ['mail.thread']

    _inherits = {
        'res.partner': 'partner_id',
    }

    doc_lines = fields.One2many('ir.attachment', 'academic_doc_id', 'Documents')
    partner_id = fields.Many2one('res.partner',
                                 string='Name', ondelete='restrict',
                                 help='Partner-related data of the user', domain=[('cfo_user', '=', True)])
    updated_emp_bio = fields.Boolean('Updated Employer BIO')
    user_id = fields.Many2one('res.users', 'Related User')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')
    cfo_team_ids = fields.Many2many('cfo.team.snr','cfo_team_emp_rel', string='Acadamic ID')

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            if user:
                self.user_id = user.id


class VolunteersSenior(models.Model):
    _name = 'volunteers.snr'
    _inherit = ['mail.thread']

    _inherits = {
        'res.partner': 'partner_id',
    }

    partner_id = fields.Many2one('res.partner',
                                 string='Name', ondelete='restrict',
                                 help='Partner-related data of the user', domain=[('cfo_user', '=', True)])
    volunteers_type = fields.Selection(
        [('External Panel Judge', 'External Panel Judge'), ('External Examiner', 'External Examiner'),
         ('Case Study Expert', 'Case Study Expert'), ('Student', 'Student'), ('Other Expertise', 'Other Expertise'),
         ('Mentor', 'Mentor')], 'Volunteers Type')
    updated_volunteers_bio = fields.Boolean('Updated Volunteers BIO')
    doc_lines = fields.One2many('ir.attachment', 'doc_id', 'Documents')
    student_planning_phase = fields.Selection(
        [('CFO Brand Ambassadors & Social Media Lead', 'CFO Brand Ambassadors & Social Media Lead'),
         ('Volunteer Lead', 'Volunteer Lead'), ('Social and Event Lead', 'Social and Event Lead'),
         ('Marketing Committee Lead', 'Marketing Committee Lead'), ('Youtube Team', 'Youtube Team'),
         ('Team Ambassadors', 'Team Ambassadors'), ('Pre Competition Contest Teams', 'Pre Competition Contest Teams'),
         ('Other Committee', 'Other Committee')], 'Student Planning Phase')
    student_operations_phase = fields.Selection(
        [('Events Logistics Committee', 'Events Logistics Committee'), ('Timekeeper', 'Timekeeper'),
         ('Prep Room Monitor', 'Prep Room Monitor'), ('Presentation Room Monitor', 'Presentation Room Monitor'),
         ('Lounge Monitor', 'Lounge Monitor'), ('Other Committee', 'Other Committee')], 'Student Operations Phase')
    other_planning_phase = fields.Selection(
        [('Legal Affairs Lead', 'Legal Affairs Lead'), ('Event Lead & Social', 'Event Lead & Social'),
         ('Marketing Committee Lead', 'Marketing Committee Lead'), ('Youtube Team', 'Youtube Team'),
         ('Pre Competition Contest Teams', 'Pre Compcfo_team_idsetition Contest Teams'),
         ('Judge Selection Team', 'Judge Selection Team')], 'Other Planning Phase')
    other_operations_phase = fields.Selection(
        [('Events Logistics Committee', 'Events Logistics Committee'), ('Prep Room Monitor', 'Prep Room Monitor'),
         ('Lounge Monitor', 'Lounge Monitor'), ('Other Committee', 'Other Committee')], 'Other operations Phase')
    i_am_a = fields.Selection([('CFO', 'CFO'),
                               ('CEO', 'CEO'),
                               ('Senior/C-Suit Executive', 'Senior/C-Suit Executive'),
                               ('Business academic', 'Business academic'),
                               ('Successful Entrepreneur', 'Successful Entrepreneur'),
                               ('Case study alumnus', 'Case study alumnus'),
                               ('College student', 'College student'),
                               ('University student', 'University student'),
                               ('Part time student', 'Part time student'),
                               ('Job seeker but have special expertise to offer',
                                'Job seeker but have special expertise to offer'),
                               ('Employed and have special expertise to offer',
                                'Employed and have special expertise to offer')], string="I am a")

    i_hold_a = fields.Selection([('Masters level qualification', 'Masters level qualification'),
                                 ('Doctorate level qualification', 'Doctorate level qualification'),
                                 ('Professional Qualification', 'Professional Qualification'),
                                 ('Bachelors/Honours/Masters Degree', 'Bachelors/Honours/Masters Degree')], "I Hold a")
    i_get_involved = fields.Selection([('Marking of reports ONLY', 'Marking of reports ONLY'),
                                       ('Marking of reports and judging during presentations',
                                        'Marking of reports and judging during presentations'),
                                       ('The planning phase (Deadline:31 January 2016)',
                                        'The planning phase (Deadline:31 January 2016)'),
                                       ('Operations phase (Deadline :20 June, 2016 )',
                                        'Operations phase (Deadline :20 June, 2016 )'),
                                       ('The planning phase (Deadline:31 January 2016)',
                                        'The planning phase (Deadline:31 January 2016)'),
                                       ('Operations phase (Deadline :20 June, 2016 )',
                                        'Operations phase (Deadline :20 June, 2016 )')], "I will like get involved in")

    cfo_brand_ambassadors_n_social_media_lead = fields.Boolean("CFO Brand Ambassadors & Social Media Lead")
    volunteer_lead = fields.Boolean("Volunteer Lead")
    social_event_lead = fields.Boolean("Social and Event Lead")
    marketing_committee_lead = fields.Boolean("Marketing Committee Lead")
    youtube_team = fields.Boolean("YouTube Team")
    team_ambassadors = fields.Boolean("Team Ambassacfo_team_idsdors")
    pre_competition_contest_teams = fields.Boolean("Pre Competition Contest Teams")
    other_committee = fields.Boolean("Other committee")
    legal_affairs_lead = fields.Boolean("Legal Affairs Lead")
    event_lead_and_social = fields.Boolean("Event Lead and Social")
    marketing_committee_lead = fields.Boolean("Marketing Committee Lead")
    judge_selection_team = fields.Boolean("Judge Selection Team")

    event_logistics_committee = fields.Boolean("Event Logistics Committee")
    timekeeper = fields.Boolean("Timekeeper")
    prep_room_monitor = fields.Boolean("Prep Room Monitor")
    presentation_room_monitor = fields.Boolean("Presentation Room Monitor")
    lounge_monitor = fields.Boolean("Lounge Monitor")
    operational_other_committee = fields.Boolean("Other Committee")
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')
    user_id = fields.Many2one('res.users', 'Related User')

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            if user:
                self.user_id = user.id


class BrandAmbassadorSenior(models.Model):
    _name = 'brand.ambassador.snr'
    _inherit = ['mail.thread']

    _inherits = {
        'res.partner': 'partner_id',
    }

    doc_lines = fields.One2many('ir.attachment', 'academic_doc_id', 'Documents')
    partner_id = fields.Many2one('res.partner',
                                 string='Name', ondelete='restrict',
                                 help='Partner-related data of the user', domain=[('cfo_user', '=', True)])
    updated_brand_amb_bio = fields.Boolean('Updated Brand Ambassador BIO')
    brand_accept = fields.Boolean('Accept Brand Invite')
    team_ids = fields.One2many('cfo.team.snr', 'brand_amb_id', string='Brand Ambassador for Teams')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')
    user_id = fields.Many2one('res.users', 'Related User')
    new_team_id = fields.Many2one('cfo.team.snr')
    team_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept'),('removed','Removed')],
                                   string="Status")

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            if user:
                self.user_id = user.id

    @api.multi
    def accept_team(self):
        self.team_status = 'Accept'

    @api.multi
    def reject_team(self):
        self.new_team_id = False
        self.team_status = 'Rejected'


class SocialMediaContestantsSenior(models.Model):
    _name = 'social.media.contestants.snr'
    _inherit = ['mail.thread']

    _inherits = {
        'res.partner': 'partner_id',
    }

    doc_lines = fields.One2many('ir.attachment', 'academic_doc_id', 'Documents')
    partner_id = fields.Many2one('res.partner',
                                 string='Name', ondelete='restrict',
                                 help='Partner-related data of the user')
    updated_social_media_bio = fields.Boolean('Updated Brand Ambassador BIO', domain=[('cfo_user', '=', True)])
    social_media_unique_url = fields.Char('Social media unique URL')
    user_id = fields.Many2one('res.users', 'Related User')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            if user:
                self.user_id = user.id


class MentorsSenior(models.Model):
    _name = 'mentors.snr'
    _inherit = ['mail.thread']

    _inherits = {
        'res.partner': 'partner_id',
    }

    doc_lines = fields.One2many('ir.attachment', 'academic_doc_id', 'Documents')
    partner_id = fields.Many2one('res.partner',
                                 string='Name', ondelete='restrict',
                                 help='Partner-related data of the user', domain=[('cfo_user', '=', True)])
    updated_mentors_bio = fields.Boolean('Updated Mentors BIO')
    mentor_accept = fields.Boolean("Accept Mentors")
    user_id = fields.Many2one('res.users', 'Related User')
    team_ids = fields.One2many('cfo.team.snr', 'mentor_id', string='Mentors for Teams')
    i_am_a = fields.Selection([('CFO', 'CFO'),
                               ('CEO', 'CEO'),
                               ('Entrepreneur', 'Entrepreneur'),
                               ('Manager', 'Manager'),
                               ('Professional Coach/Mentor', 'Professional Coach/Mentor'),
                               ('Business Educator', 'Business Educator'),
                               ('Recent Business Graduate', 'Recent Business Graduate')], string="I am a")

    i_hold_a = fields.Selection([('Masters level qualification', 'Masters level qualification'),
                                 ('Doctorate level qualification', 'Doctorate level qualification'),
                                 ('Bachelors level qualification', 'Bachelors level qualification'),
                                 ('Professional Qualification', 'Professional Qualification')], "I Hold a")
    i_get_involved = fields.Selection([('Marking of reports ONLY', 'Marking of reports ONLY'),
                                       ('Marking of reports and judging during presentations',
                                        'Marking of reports and judging during presentations'),
                                       ('The planning phase (Deadline:31 January 2016)',
                                        'The planning phase (Deadline:31 January 2016)'),
                                       ('Operations phase (Deadline :20 June, 2016 )',
                                        'Operations phase (Deadline :20 June, 2016 )'),
                                       ('The planning phase (Deadline:31 January 2016)',
                                        'The planning phase (Deadline:31 January 2016)'),
                                       ('Operations phase (Deadline :20 June, 2016 )',
                                        'Operations phase (Deadline :20 June, 2016 )')], "I will like get involved in")
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')
    new_team_id = fields.Many2one('cfo.team.snr')
    team_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept'),('removed','Removed')],
                                   string="Status")

    #     is_cfo_junior = fields.boolean('Is CFO Junior?')

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            user = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)], limit=1)
            if user:
                self.user_id = user.id

    @api.multi
    def accept_team(self):
        self.team_status = 'Accept'

    @api.multi
    def reject_team(self):
        self.new_team_id = False
        self.team_status = 'Rejected'


class CFOSeniorMember(models.Model):
    _name = 'cfo.snr.member'
    _inherit = ['mail.thread']
    #     _rec_name = aspirants_name

    name = fields.Char('Name', required=True)
    aspirants_name = fields.Many2one('res.partner', 'Name', required=True, domain=[('cfo_user', '=', True)])
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
    unit = fields.Char('Department/Faculty/Unit')
    website = fields.Char('Website')
    college_street = fields.Char('Address')
    college_street2 = fields.Char('Street2')
    college_city = fields.Char('City')
    college_province = fields.Many2one('res.country.state', 'Province')
    college_zip = fields.Char('Zip')
    college_country = fields.Many2one('res.country', 'Country')
    cfo_team = fields.Many2one('cfo.team.snr', 'CFO Snr Teams')

    cfo_member_type = fields.Selection([('CFO Aspirant', 'CFO Aspirant'),
                                        ('Academic Institution', 'Academic Institution'),
                                        ('Employer', 'Employer'),
                                        ('Volunteer', 'Volunteer'),
                                        ('Brand Ambassador', 'Brand Ambassador'),
                                        ('Social Media Contestant', 'Social Media Contestant'),
                                        ('Mentor', 'Mentor'),
                                        ('Secondary/High School', 'Secondary/High School')],
                                       'Type')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')
    cfo_registrants_source = fields.Selection([('Social Media', 'Social Media'),
                                               ('Direct web address', 'Direct web address'),
                                               ('Google/other search engine', 'Google/other search engine'),
                                               ('E-banner/Web advertisement', 'E-banner/Web advertisement'),
                                               ('Email campaign/Signature card with link',
                                                'Email campaign/Signature card with link'),
                                               ("Person Vue website/exam booking page",
                                                "Person Vue website/exam booking page"),
                                               ("Other website listing", "Other website listing"),
                                               ("Radio/TV", "Radio/TV"),
                                               ("Print Media", "Print Media"),
                                               ("Direct mail via the post", "Direct mail via the post"),
                                               ("Word-of-mouth/current/prior CharterQuest Student",
                                                "Word-of-mouth/current/prior CharterQuest Student"),
                                               ("My school/mentor/friend", "My school/mentor/friend"),
                                               ("My Employer/Boss/Supervisor", "My Employer/Boss/Supervisor"),
                                               ("Brand Ambassador", "Brand Ambassador"),
                                               ("Professional Body (CIMA, SAICA, ACCA, CFA Institute)",
                                                "Professional Body (CIMA, SAICA, ACCA, CFA Institute)"),
                                               ("Billboard/street post/community center/church",
                                                "Billboard/street post/community center/church"),
                                               ("Other(please specify)", "Other(please specify)")
                                               ], 'How Did you 1st Hear About the CFO')

    login = fields.Char('User name')
    password = fields.Char('Password')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
