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
from datetime import datetime
import pytz
from odoo import models, fields, _, api
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class IRAttachment(models.Model):
    _inherit = 'ir.attachment'

    snr_team_id = fields.Many2one('cfo.team.snr', 'SNR Team ID')
    jnr_team_id = fields.Many2one('cfo.team.jnr', 'JNR Team ID')
    snr_doc_id = fields.Many2one('volunteers.snr', 'SNR Doc ID')
    jnr_doc_id = fields.Many2one('volunteers.jnr', 'JNR Doc ID')
    snr_mentors_doc_id = fields.Many2one('mentors.snr', 'SNR DOC ID')
    jnr_mentors_doc_id = fields.Many2one('mentors.jnr', 'JNR DOC ID')
    snr_aspirant_doc_id = fields.Many2one('cfo.snr.aspirants', 'Aspirants Docs')
    jnr_aspirant_doc_id = fields.Many2one('cfo.jnr.aspirants', 'Aspirants Docs')
    snr_academic_doc_id = fields.Many2one('academic.institution.snr', 'Academic Docs')
    jnr_academic_doc_id = fields.Many2one('academic.institution.jnr', 'Academic Docs')
    snr_employers_doc_id = fields.Many2one('employers.snr', 'Employer Docs')
    jnr_employers_doc_id = fields.Many2one('employers.jnr', 'Employer Docs')
    snr_social_doc_id = fields.Many2one('social.media.contestants.snr', 'Social Docs')
    jnr_social_doc_id = fields.Many2one('social.media.contestants.jnr', 'Social Docs')
    snr_brand_doc_id = fields.Many2one('brand.ambassador.snr', 'Social Docs')
    jnr_brand_doc_id = fields.Many2one('brand.ambassador.jnr', 'Social Docs')


class CFOTeam(models.Model):
    _name = 'cfo.teams'

    name = fields.Char('Name')
    cfo_comp = fields.Selection([('CFO SNR', 'CFO SNR'), ('CFO JNR', 'CFO JNR')], 'Competition')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')


class CFOTeamSNR(models.Model):
    _name = "cfo.team.snr"

    name = fields.Char(string='Name')
    ref_name = fields.Char('Reference Name')
    mentor_id = fields.Many2one('mentors.snr', 'Mentor')
    brand_amb_id = fields.Many2one('brand.ambassador.snr', 'Brand Ambassador')
    aspirant_leader_id = fields.Many2one('cfo.snr.aspirants', 'Team Leader')
    academic_leader_id = fields.Many2one('academic.institution.snr', 'Team Leader')
    employer_leader_id = fields.Many2one('employers.snr', 'Team Leader')
    aspirant_admin_id = fields.Many2one('cfo.snr.aspirants', 'Team Created By')
    academic_admin_id = fields.Many2one('academic.institution.snr', 'Team Created By')
    employer_admin_id = fields.Many2one('employers.snr', 'Team Created By')
    aspirants_ids = fields.Many2many('cfo.snr.aspirants', string='Team Members')
#     cfo_academic_ids = fields.Many2many('academic.institution.snr',string="Team Member")
    document_ids = fields.One2many('ir.attachment', 'snr_team_id', 'Team Documents')
    team_type = fields.Selection(
        [('CFO Aspirant', 'CFO Aspirant'), ('Academic Institution', 'Academic Institution'),
         ('Employer', 'Employer')], 'Team Type')
    encrypted_team_type = fields.Char('Encrypted Team Type')
    encrypted_id = fields.Char('Encrypted ID')
    mentor_check = fields.Boolean('Mentor Accept')
    cfo_report_deadline_date = fields.Datetime('CFO Report Submission Deadline Date')
    cfo_report_submission_date = fields.Datetime('CFO Report Submission Date')
    acknowledge_cfo_report = fields.Boolean('CFO Report Submitted')
    date_cfo_report_deadline = fields.Date('CFO Report Date')
    remaining_time_deadline = fields.Float("Remaining Time for Deadline")
    crossed_deadline = fields.Boolean("Crossed Deadline")
    
    aspirant_team_member_ids = fields.One2many('snr.aspirant.team.member', 'team_id', string="Team Member")
    academic_team_member_ids = fields.One2many('snr.academic.team.member', 'team_id', string="Team Member")
    employer_team_member_ids = fields.One2many('snr.employer.team.member', 'team_id', string="Team Member")
    cfo_comp = fields.Selection([('CFO SNR', 'CFO SNR'), ('CFO JNR', 'CFO JNR')], 'Competition')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')
    deadline_date_copy = fields.Datetime()

    @api.model
    def create(self, vals):
        res = super(CFOTeamSNR, self).create(vals)
        create = datetime.strptime(res.create_date, '%Y-%m-%d %H:%M:%S')
        deadline_year = create.year if create.month < 4 else create.year + 1

        deadline_date = create.replace(day=30, month=4, year=deadline_year, hour=23, minute=59, second=59, microsecond=0)
        if self._context.get('tz'):
          tz = pytz.timezone(self._context.get('tz'))
        else:
           tz = pytz.utc
        c_time = datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]
        if sign == '-':
            d1_date = (deadline_date + timedelta(hours=hour_tz +5, minutes=min_tz + 30)).strftime('%Y-%m-%d %H:%M:%S')
        if sign == '+':
            d1_date = (deadline_date - timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
        res.update({'cfo_report_deadline_date': d1_date if d1_date else False})
        return res
    
    @api.model
    def _send_reminder_for_bio(self):
        for each_team in self.env['cfo.team.snr'].search([]):
                template = self.env.ref('cfo_snr_jnr.email_template_for_reminder_update_bio',raise_if_not_found=False)
                template_mentor = self.env.ref('cfo_snr_jnr.email_template_for_reminder_update_bio_mentor',raise_if_not_found=False)
                template_amb = self.env.ref('cfo_snr_jnr.email_template_for_reminder_update_bio_amb',raise_if_not_found=False)
                if not each_team.brand_amb_id.updated_brand_amb_bio and each_team.brand_amb_id:
                            template_amb.sudo().with_context(
                            team_name=each_team.ref_name,
                            email_to=each_team.brand_amb_id.email_1,
                        ).send_mail(each_team.brand_amb_id.id, force_send=True)
                if not each_team.mentor_id.updated_mentors_bio and each_team.mentor_id:
                            template_mentor.sudo().with_context(
                            team_name=each_team.ref_name,
                            email_to=each_team.mentor_id.email_1,
                        ).send_mail(each_team.mentor_id.id, force_send=True)
                for each_aspirant_member in each_team.aspirant_team_member_ids:
                    if each_aspirant_member.related_user_id and not each_aspirant_member.related_user_id.updated_cfo_bio:
                            template.sudo().with_context(
                            team_name=each_team.ref_name,
                            email_to=each_aspirant_member.related_user_id.email_1
                        ).send_mail(each_aspirant_member.related_user_id.id, force_send=True)
                for each_acdemic_member in each_team.academic_team_member_ids:
                    if each_acdemic_member.related_user_aspirant_id.email_1 and  not each_acdemic_member.related_user_aspirant_id.updated_cfo_bio:
                            template.sudo().with_context(
                            team_name=each_team.ref_name,
                            email_to=each_acdemic_member.related_user_aspirant_id.email_1
                        ).send_mail(each_acdemic_member.related_user_aspirant_id.id, force_send=True)
                for each_employee_member in each_team.employer_team_member_ids:
                    if each_employee_member.related_user_aspirant_id.email_1 and  not each_employee_member.related_user_aspirant_id.updated_cfo_bio:
                            template.sudo().with_context(
                            team_name=each_team.ref_name,
                            email_to=each_employee_member.related_user_aspirant_id.email_1
                        ).send_mail(each_employee_member.related_user_aspirant_id.id, force_send=True)
                    
    @api.model
    def _compute_remaining_time_deadline(self):
        for each in self.env['cfo.team.snr'].search([]):
            if each.cfo_report_deadline_date:
                today_date = datetime.now().date()
                deadline_date = fields.Date.from_string(each.cfo_report_deadline_date)
                if deadline_date > today_date:
                    each.remaining_time_deadline = (deadline_date - today_date).days
                else:
                    each.remaining_time_deadline = 0.0
                    
    
class SNRAspirantTeamMembers(models.Model):
    _name = 'snr.aspirant.team.member'
    team_id = fields.Many2one('cfo.team.snr', string="Team")
    related_user_id = fields.Many2one('cfo.snr.aspirants', string="Related User")
    email = fields.Char(string="Email", related="related_user_id.email_1")
    user_type = fields.Selection([('Admin', 'Admin'), ('Leader', 'Leader'), ('Member', 'Member'), ('Mentor', 'Mentor'),
                                  ('Brand Ambassador', 'Brand Ambassador')])
    member_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept'), ('removed', 'Removed')],
                                     string="Status")
    member_accept_data = fields.Boolean(string='MEMBER ACCEPT')
    aspirant_member_requested = fields.Boolean(string='True')

class SNRAcademicTeamMembers(models.Model):
    _name = 'snr.academic.team.member'
    team_id = fields.Many2one('cfo.team.snr', string="Team")
    related_user_id = fields.Many2one('academic.institution.snr', string="Related User",)
    related_user_aspirant_id = fields.Many2one('cfo.snr.aspirants', string="Related User",)
    email = fields.Char(string="Email")
    user_type = fields.Selection([('Admin', 'Admin'), ('Leader', 'Leader'), ('Member', 'Member'), ('Mentor', 'Mentor'),
                                  ('Brand Ambassador', 'Brand Ambassador')])
    member_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept')],
                                     string="Status")
    member_requested = fields.Boolean(string='True')

    @api.model
    def create(self, vals):
        res = super(SNRAcademicTeamMembers, self).create(vals)
        res.update({'email': res.related_user_id.email_1 if res.related_user_id else res.related_user_aspirant_id.email_1 if res.related_user_aspirant_id else False})
        return res

class SNREmployerTeamMembers(models.Model):
    _name = 'snr.employer.team.member'
    team_id = fields.Many2one('cfo.team.snr', string="Team")
    related_user_id = fields.Many2one('employers.snr', string="Related User")
    related_user_aspirant_id = fields.Many2one('cfo.snr.aspirants', string="Related Aspirant User")
    email = fields.Char(string="Email",)
    user_type = fields.Selection([('Admin', 'Admin'), ('Leader', 'Leader'), ('Member', 'Member'), ('Mentor', 'Mentor'),
                                  ('Brand Ambassador', 'Brand Ambassador')])
    member_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept')],
                                     string="Status")
    member_requested = fields.Boolean(string='True')
    
    
    @api.model
    def create(self, vals):
        res = super(SNREmployerTeamMembers, self).create(vals)
        res.update({'email': res.related_user_id.email_1 if res.related_user_id else res.related_user_aspirant_id.email_1 if res.related_user_aspirant_id else False})
        return res


class CFOTeamJNR(models.Model):
    _name = "cfo.team.jnr"

    name = fields.Char(string='Name')
    ref_name = fields.Char('Reference Name')
    mentor_id = fields.Many2one('mentonamers', 'Mentor')
    mentor_id = fields.Many2one('mentors.jnr', 'Mentor',)
    brand_amb_id = fields.Many2one('brand.ambassador.jnr', 'Brand Ambassador')
    aspirant_admin_id = fields.Many2one('cfo.jnr.aspirants', 'Team Created By')
    team_leader_id = fields.Many2one('cfo.jnr.aspirants', 'Team Leader')
    academic_admin_id = fields.Many2one('academic.institution.jnr', 'Team Created By')
    employer_admin_id = fields.Many2one('employers.jnr', 'Team Created By')
    aspirants_ids = fields.Many2many('cfo.jnr.aspirants', string='Team Members')
    document_ids = fields.One2many('ir.attachment', 'jnr_team_id', 'Team Documents')
    team_type = fields.Selection(
        [('CFO Aspirant', 'CFO Aspirant'), ('Secondary/High School', 'Secondary/High School'),
         ('Employer', 'Employer')], 'Team Type')
    encrypted_team_type = fields.Char('Encrypted Team Type')
    encrypted_id = fields.Char('Encrypted ID')
    mentor_check = fields.Boolean('Mentor Accept')
    cfo_report_deadline_date = fields.Datetime('CFO Report Submission Deadline Date')
    cfo_report_submission_date = fields.Datetime('CFO Report Submission Date')
    acknowledge_cfo_report = fields.Boolean('CFO Report Submitted')
    date_cfo_report_deadline = fields.Date('CFO Report Date')
    remaining_time_deadline = fields.Char("Remaining Time for Deadline")
    crossed_deadline = fields.Boolean("Crossed Deadline")
    cfo_comp = fields.Selection([('CFO SNR', 'CFO SNR'), ('CFO JNR', 'CFO JNR')], 'Competition')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')
    aspirant_team_member_ids = fields.One2many('jnr.aspirant.team.member', 'team_id', string="Team Member")
    highschool_team_member_ids = fields.One2many('jnr.highschool.team.member', 'team_id', string="Team Member")

    @api.model
    def create(self, vals):
        res = super(CFOTeamJNR, self).create(vals)
        create = datetime.strptime(res.create_date, '%Y-%m-%d %H:%M:%S')
        deadline_year = create.year if create.month < 4 else create.year + 1
        deadline_date = create.replace(day=30, month=4, year=deadline_year, hour=21, minute=59, second=59, microsecond=0)
        if self._context.get('tz'):
          tz = pytz.timezone(self._context.get('tz'))
        else:
           tz = pytz.utc
        c_time = datetime.now(tz)
        hour_tz = int(str(c_time)[-5:][:2])
        min_tz = int(str(c_time)[-5:][3:])
        sign = str(c_time)[-6][:1]
        if sign == '-':
            d1_date = (deadline_date + timedelta(hours=hour_tz - 2, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
        if sign == '+':
            d1_date = (deadline_date - timedelta(hours=hour_tz - 2, minutes=min_tz)).strftime('%Y-%m-%d %H:%M:%S')
        res.update({'cfo_report_deadline_date': d1_date if d1_date else False})
        return res

    @api.model
    def _compute_remaining_time_deadline(self):
        for each in self.env['cfo.team.jnr'].search([]):
            if each.cfo_report_deadline_date:
                today_date = datetime.now().date()
                deadline_date = fields.Date.from_string(each.cfo_report_deadline_date)
                if deadline_date > today_date:
                    each.remaining_time_deadline = (deadline_date - today_date).days
                else:
                    each.remaining_time_deadline = 0.0

    @api.model
    def _send_reminder_for_bio_jnr(self):
        for each_team in self.env['cfo.team.jnr'].search([]):
                template = self.env.ref('cfo_snr_jnr.email_template_for_reminder_update_bio_jnr',raise_if_not_found=False)
                template_mentor = self.env.ref('cfo_snr_jnr.email_template_for_reminder_update_bio_mentor_jnr',raise_if_not_found=False)
                template_amb = self.env.ref('cfo_snr_jnr.email_template_for_reminder_update_bio_amb_jnr',raise_if_not_found=False)
                if not each_team.brand_amb_id.updated_brand_amb_bio and each_team.brand_amb_id:
                            template_amb.sudo().with_context(
                            team_name=each_team.ref_name,
                            email_to=each_team.brand_amb_id.email_1,
                        ).send_mail(each_team.brand_amb_id.id, force_send=True)
                if not each_team.mentor_id.updated_mentors_bio and each_team.mentor_id:
                            template_mentor.sudo().with_context(
                            team_name=each_team.ref_name,
                            email_to=each_team.mentor_id.email_1,
                        ).send_mail(each_team.mentor_id.id, force_send=True)
                for each_highschool_member in each_team.highschool_team_member_ids:
                    if each_highschool_member.related_user_aspirant_id and not each_highschool_member.related_user_aspirant_id.updated_cfo_bio:
                            template.sudo().with_context(
                            team_name=each_team.ref_name,
                            email_to=each_highschool_member.related_user_aspirant_id.email_1
                        ).send_mail(each_highschool_member.related_user_aspirant_id.id, force_send=True)

class JNRAspirantTeamMembers(models.Model):
    _name = 'jnr.aspirant.team.member'
    
    team_id = fields.Many2one('cfo.team.jnr', string="Team")
    related_user_id = fields.Many2one('cfo.jnr.aspirants', string="Related User")
    email = fields.Char(string="Email", related="related_user_id.email_1")
    user_type = fields.Selection([('Admin', 'Admin'), ('Leader', 'Leader'), ('Member', 'Member'), ('Mentor', 'Mentor'),
                                  ('Brand Ambassador', 'Brand Ambassador')])
    member_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept'), ('removed', 'Removed')],
                                     string="Status")
    member_accept_data = fields.Boolean(string='MEMBER ACCEPT')
    aspirant_member_requested = fields.Boolean(string='True')
    
    
    
class JNRAcademicTeamMembers(models.Model):
    _name = 'jnr.highschool.team.member'
    
    team_id = fields.Many2one('cfo.team.jnr', string="Team")
    related_user_id = fields.Many2one('academic.institution.jnr', string="Related User")
    related_user_aspirant_id = fields.Many2one('cfo.jnr.aspirants', string="Related User")
    email = fields.Char(string="Email")
    user_type = fields.Selection([('Admin', 'Admin'), ('Leader', 'Leader'), ('Member', 'Member'), ('Mentor', 'Mentor'),
                                  ('Brand Ambassador', 'Brand Ambassador')])
    member_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept')],
                                     string="Status")
    member_requested = fields.Boolean(string='True')
    
    @api.model
    def create(self, vals):
        res = super(JNRAcademicTeamMembers, self).create(vals)
        res.update({'email': res.related_user_id.email_1 if res.related_user_id else res.related_user_aspirant_id.email_1 if res.related_user_aspirant_id else False})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
