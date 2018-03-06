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

from odoo import models, fields, _, api


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
    remaining_time_deadline = fields.Char("Remaining Time for Deadline")
    crossed_deadline = fields.Boolean("Crossed Deadline")
    
    aspirant_team_member_ids = fields.One2many('snr.aspirant.team.member', 'team_id', string="Team Member")
    academic_team_member_ids = fields.One2many('snr.academic.team.member', 'team_id', string="Team Member")
    employer_team_member_ids = fields.One2many('snr.employer.team.member', 'team_id', string="Team Member")
    cfo_comp = fields.Selection([('CFO SNR', 'CFO SNR'), ('CFO JNR', 'CFO JNR')], 'Competition')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')

    @api.multi
    def onchange_cfo_report_deadline_date(self, cfo_report_deadline_date):
        if cfo_report_deadline_date:
            team_date = datetime.strptime(cfo_report_deadline_date, "%Y-%m-%d %H:%M:%S").date()
            return {'value': {'date_cfo_report_deadline': team_date}}
        return {}


class SNRAspirantTeamMembers(models.Model):
    _name = 'snr.aspirant.team.member'
    team_id = fields.Many2one('cfo.team.snr', string="Team")
    related_user_id = fields.Many2one('cfo.snr.aspirants', string="Related User")
    email = fields.Char(string="Email", related="related_user_id.email_1")
    user_type = fields.Selection([('Admin', 'Admin'), ('Leader', 'Leader'), ('Member', 'Member'), ('Mentor', 'Mentor'),
                                  ('Brand Ambassador', 'Brand Ambassador')])
    member_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept')],
                                     string="Status")


class SNRAcademicTeamMembers(models.Model):
    _name = 'snr.academic.team.member'
    team_id = fields.Many2one('cfo.team.snr', string="Team")
    related_user_id = fields.Many2one('academic.institution.snr', string="Related User")
    email = fields.Char(string="Email", related="related_user_id.email_1")
    user_type = fields.Selection([('Admin', 'Admin'), ('Leader', 'Leader'),('Member', 'Member'), ('Mentor', 'Mentor'),
                                  ('Brand Ambassador', 'Brand Ambassador')])
    member_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept')],
                                     string="Status")


class SNREmployerTeamMembers(models.Model):
    _name = 'snr.employer.team.member'
    team_id = fields.Many2one('cfo.team.snr', string="Team")
    related_user_id = fields.Many2one('employers.snr', string="Related User")
    email = fields.Char(string="Email", related="related_user_id.email_1")
    user_type = fields.Selection([('Admin', 'Admin'), ('Leader', 'Leader'), ('Member', 'Member'), ('Mentor', 'Mentor'),
                                  ('Brand Ambassador', 'Brand Ambassador')])
    member_status = fields.Selection([('Pending', 'Pending'), ('Rejected', 'Rejected'), ('Accept', 'Accept')],
                                     string="Status")


class CFOTeamJNR(models.Model):
    _name = "cfo.team.jnr"

    name = fields.Char(string='Name')
    ref_name = fields.Char('Reference Name')
    mentor_id = fields.Many2one('mentors', 'Mentor')
    brand_amb_id = fields.Many2one('brand.ambassador.jnr', 'Brand Ambassador')
    team_leader_id = fields.Many2one('cfo.jnr.aspirants', 'Team Leader')
    academic_admin_id = fields.Many2one('academic.institution.jnr', 'Team Created By')
    employer_admin_id = fields.Many2one('employers.jnr', 'Team Created By')
    aspirants_ids = fields.Many2many('cfo.jnr.aspirants', string='Team Members')
    document_ids = fields.One2many('ir.attachment', 'jnr_team_id', 'Team Documents')
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
    remaining_time_deadline = fields.Char("Remaining Time for Deadline")
    crossed_deadline = fields.Boolean("Crossed Deadline")
    cfo_comp = fields.Selection([('CFO SNR', 'CFO SNR'), ('CFO JNR', 'CFO JNR')], 'Competition')
    cfo_competition_year = fields.Selection(
        [('2016', '2016'), ('2017', '2017'), ('2018', '2018'), ('2019', '2019'), ('2020', '2020')], 'Year')

    @api.multi
    def onchange_cfo_report_deadline_date(self, cfo_report_deadline_date):
        if cfo_report_deadline_date:
            team_date = datetime.strptime(cfo_report_deadline_date, "%Y-%m-%d %H:%M:%S").date()
            return {'value': {'date_cfo_report_deadline': team_date}}
        return {}
    # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
