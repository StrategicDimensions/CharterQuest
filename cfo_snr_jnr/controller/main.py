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
import werkzeug

from odoo import http, _
from odoo.http import request
import logging
import io
import json
from odoo.addons.web.controllers import main as web
from odoo.addons.auth_signup.controllers import main as auth_signup
import odoo
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.auth_signup.models.res_partner import SignupError, now
import datetime
from datetime import timedelta
import base64
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


class CfoHome(web.Home):

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()
        qcontext['cfo_logn'] = kw.get('cfo_login')
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    if kw.get('cfo_login'):
                        request.session['cfo_login'] = True
                        return http.request.redirect('/my/home')
                    return self.web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('cfo_snr_jnr.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/login'], type='http', auth="public", website=True)
    def login(self, **post):
        value = {}
        print("\n\n\n\n====post=======",post)
        request.session['user_type'] = post.get('user_type')
        if post.get('login'):
            value['login'] = post.get('login')
        if post.get('is_request'):
            value['is_request'] = post.get('is_request')
        if post.get('team_id'):
            value['team_id'] = int(post.get('team_id'))
        if post.get('error'):
            value['error'] = post.get('error')
        return request.render('cfo_snr_jnr.cfo_login', value)

    @http.route('/web/login', type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        print("\n\n\n\n------callll")
        cfo_aspirant_id = request.env['cfo.snr.aspirants'].sudo().search(
            [('email_1', '=', kw.get('login')), ('is_request', '=', True)])
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            if cfo_aspirant_id and kw.get('team'):
                return http.request.redirect('/is_from_request_id?team_id=' + str(kw.get('team')))

            if uid is not False and cfo_aspirant_id:
                request.params['login_success'] = True
                if kw.get('cfo_login'):
                    request.session['cfo_login'] = True
                    return http.request.redirect('/my/home')
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            request.uid = old_uid
            values['error'] = _("Wrong login/password")
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route()
    def web_login(self, redirect=None, **kw):
        cfo_aspirant_id = request.env['cfo.snr.aspirants'].sudo().search(
            [('email_1', '=', kw.get('login')), ('is_request', '=', True)])
        web.ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return http.redirect_with_hash(redirect)
        if not request.uid:
            request.uid = odoo.SUPERUSER_ID
        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
            qry = "SELECT id from res_users where login= '" + request.params['login'] + "';"
            cr.execute(qry)
            row_username = cr.fetchone()
            if not row_username:
                values['error'] = _("Email Address Does Not Exist, Please Register")
                return request.redirect('/login?error=%s' % values['error'])
            else:
                old_uid = request.uid
                uid = request.session.authenticate(request.session.db, request.params['login'],
                                                   request.params['password'])
                if cfo_aspirant_id and kw.get('team'):
                    return http.request.redirect('/is_from_request_id?team_id=%s&cfo_login=%s'%(str(kw.get('team')),kw.get('cfo_login')))

                if uid is not False and not cfo_aspirant_id:
                    request.params['login_success'] = True
                    if kw.get('cfo_login'):
                        request.session['cfo_login'] = True
                        return http.request.redirect('/my/home')
                    return http.redirect_with_hash(self._login_redirect(uid, redirect='/'))
                request.uid = old_uid
                values['error'] = _('Your Email Address/Password is Incorrect')
                return request.redirect('/login?error=%s' % values['error'])
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employee can access this database. Please contact the administrator.')
                return request.redirect('/login?error=%s' % values['error'])

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True
        # if kw.get('cfo_login') == 'true':
        #     return request.redirect('/login')
        # else:
        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/signup'], type='http', auth="public", website=True)
    def signup(self, **post):
        value = {}
        if post.get('error'):
            value['error'] = post.get('error')

        return request.render('cfo_snr_jnr.cfo_signup_form', value)

    @http.route(['/cfo_logout'], type='http', auth="public", website=True)
    def cfo_logout(self, **post):
        request.session['logged_user'] = None
        request.session['cfo_login'] = False
        return request.render("cfo_snr_jnr.cfo_login")

    @http.route('/get_member_types', type='json', auth='public', webstie=True)
    def get_member_types(self, val):
        if val:
            list = [conf.cfo_member_type for conf in
                    request.env['cfo.configuration'].search([('cfo_competitions', '=', int(val))],order="id desc")]
            return list

    @http.route(['/CFO/senior/signup'], type='http', auth="public", website=True)
    def cfo_senior_signup(self, **post):
        return request.render('cfo_snr_jnr.cfo_senior_signup')

    @http.route(['/CFO/junior/signup'], type='http', auth="public", website=True)
    def cfo_junior_signup(self, **post):
        return request.render('cfo_snr_jnr.cfo_junior_signup')

    @http.route(['/cfo_senior'], type='http', auth="public", website=True)
    def cfo_senior(self, **post):
        print("\n\n\n\n\n============snr post==========",post)
        partner = request.env.user.partner_id
        login = request.env.user.login
        today = datetime.datetime.today()
        args = [('email_1', '=', login)]
        # if today.month in [4, 5, 6, 7, 8, 9, 10, 11, 12]:
        #     args.append(('cfo_competition_year', '=', str(today.year + 1)))
        # else:
        #     args.append(('cfo_competition_year', '=', str(today.year)))
        snr_aspirants = request.env['cfo.snr.aspirants'].sudo().search(args)
        snr_academic_institution = request.env['academic.institution.snr'].sudo().search(args)
        snr_employers = request.env['employers.snr'].sudo().search(args)
        snr_volunteers = request.env['volunteers.snr'].sudo().search(args)
        snr_brand_ambassador = request.env['brand.ambassador.snr'].sudo().search(args)
        snr_media_contestants = request.env['social.media.contestants.snr'].sudo().search(args)
        snr_mentors = request.env['mentors.snr'].sudo().search(args)
        is_from_new_member = request.session.get('is_from_new_member')
        values = {}

        values['country_list'] = request.env['res.country'].sudo().search([])
        values['state_list'] = request.env['res.country.state'].sudo().search([])
        if post.get('snr_aspirants') or post.get('snr_academic_institution') or post.get('snr_employers') or post.get(
                'snr_brand_ambassador') or post.get('snr_media_contestants') or post.get('snr_mentors'):
            values['update_bio'] = True
            values['update_bio_info'] = True
        values['date_of_report_submit'] = False
        if snr_aspirants.aspirant_id and snr_aspirants.aspirant_id.cfo_report_deadline_date:
            tz = pytz.timezone(request.env.user.tz) if request.env.user.tz else pytz.utc
            life_date = datetime.datetime.strptime(snr_aspirants.aspirant_id.cfo_report_deadline_date,
                                                   DEFAULT_SERVER_DATETIME_FORMAT)
            life_date = (life_date + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')

            print("\n\n\n\n\n===========datev of report submit========",life_date)
            values['date_of_report_submit'] = life_date

        if is_from_new_member:
            values['is_from_new_member'] = True
        if snr_aspirants:
            values.update({'snr_aspirants': snr_aspirants})
            if snr_aspirants.date_of_birth:
                values.update({'date_of_birth': datetime.datetime.strptime(snr_aspirants.date_of_birth,
                                                                           "%Y-%m-%d").strftime('%d/%m/%Y')})
            if snr_aspirants.start_date:
                values.update({'start_date': datetime.datetime.strptime(snr_aspirants.start_date, "%Y-%m-%d").strftime(
                    '%d/%m/%Y')})
            if snr_aspirants.expected_completion_date:
                values.update({'expected_completion_date': datetime.datetime.strptime(
                    snr_aspirants.expected_completion_date, "%Y-%m-%d").strftime('%d/%m/%Y')})
            values.update({'senior': True})
        if snr_academic_institution:
            values.update({'snr_academic_institution': snr_academic_institution})
            values.update({'academic_institution': True})
        if snr_employers:
            values.update({'snr_employers': snr_employers})
            values.update({'employee': True})
        if snr_volunteers:
            values.update({'snr_volunteers': snr_volunteers})
        if snr_brand_ambassador:
            values.update({'snr_brand_ambassador': snr_brand_ambassador})
            values.update({'brand_ambassador': True})
        if snr_media_contestants:
            values.update({'snr_media_contestants': snr_media_contestants})
            values.update({'media_contestants': True})
        if snr_mentors:
            values.update({'snr_mentors': snr_mentors})
            values.update({'mentor': True})
        #         if post.get('is_in_team'):
        #                 values['cfo_team'] = True
        #                 values['cfo_team_edit'] = True
        if post.get('cfo_team'):
            list = []
            values['cfo_team'] = True
            values['update_bio'] = False
            values['update_bio_info'] = False

            if snr_aspirants.aspirant_id:
                values['aspirant_team'] = snr_aspirants.aspirant_id
            if snr_academic_institution.cfo_team_ids:
                for data in snr_academic_institution.cfo_team_ids:
                    for team in data:
                        list.append(team)
                values['acadamic_team'] = list
            if snr_employers.cfo_team_ids:
                for data in snr_employers.cfo_team_ids:
                    for team in data:
                        list.append(team)
                values['employers_team'] = list
        if request.httprequest.method == 'POST':
            if post.get('snr_aspirant') and not post.get('cfo_team'):
                if post.get('update_bio_info'):
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False

                    birth_date = datetime.datetime.strptime(post.get('date_of_birth'), "%d/%m/%Y").strftime('%m/%d/%Y')
                    snr_aspirants.sudo().write({
                        'name': post.get('name'),
                        'surname': post.get('surname'),
                        'other_names': post.get('other_names'),
                        'date_of_birth': birth_date,
                        'nationality': post.get('nationality'),
                        'country_of_birth': post.get('country_of_birth')
                    })
                if post.get('contact_info'):
                    values['eligibility_status'] = True
                    values['update_bio'] = True
                    values['contact_info'] = False
                    snr_aspirants.sudo().write({
                        'mobile': post.get('mobile'),
                        'phone': post.get('phone'),
                        'home_phone': post.get('home_phone'),
                        'email_1': post.get('email_1'),
                        'email_2': post.get('email_2'),
                        'street': post.get('street'),
                        'street2': post.get('street2'),
                        'city': post.get('city'),
                        'state_id': post.get('state_id'),
                        'zip': post.get('zip'),
                        'country_id': post.get('country_id')
                    })
                if post.get('eligibility_status'):
                    values['competition_rule'] = True
                    values['update_bio'] = True
                    values['eligibility_status'] = False
                    if post.get('start_date'):
                        start_date = datetime.datetime.strptime(post.get('start_date'), "%d/%m/%Y").strftime('%m/%d/%Y')
                    if post.get('expected_completion_date'):
                        expected_completion_date = datetime.datetime.strptime(post.get('expected_completion_date'),
                                                                              "%d/%m/%Y").strftime('%m/%d/%Y')
                    snr_aspirants.sudo().write({
                        'entry_as_student': True if post.get('user_type') == 'student' else False,
                        'entry_as_employee': True if post.get('user_type') == 'employee' else False,
                        'school_name': post.get('school_name'),
                        'department': post.get('department'),
                        'website': post.get('website'),
                        'stu_street': post.get('stu_street'),
                        'stu_street2': post.get('stu_street2'),
                        'stu_city': post.get('stu_city'),
                        'stu_state_id': post.get('stu_state_id'),
                        'stu_zip': post.get('stu_zip'),
                        'stu_country_id': post.get('stu_country_id'),
                        'programme_name': post.get('programme_name'),
                        'start_date': start_date if post.get('start_date') else False,
                        'expected_completion_date': expected_completion_date if post.get(
                            'expected_completion_date') else False,
                        'mode_of_studies': post.get('mode_of_studies'),
                        'formal_work_exp': post.get('formal_work_exp'),
                        'legal_name_employer': post.get('legal_name_employer'),
                        'sector': post.get('sector'),
                        'if_company': post.get('if_company'),
                        'emp_department': post.get('emp_department'),
                        'emp_website': post.get('emp_website'),
                        'emp_start_date': post.get('emp_start_date') or False,
                        'emp_status': post.get('emp_status'),
                        'emp_experience': post.get('emp_experience'),
                        'emp_street': post.get('emp_street'),
                        'emp_street2': post.get('emp_street2'),
                        'emp_city': post.get('emp_city'),
                        'emp_state_id': post.get('emp_state_id'),
                        'emp_zip': post.get('emp_zip'),
                        'emp_country_id': post.get('emp_country_id'),
                        'tertiary_qualification': post.get('tertiary_qualification'),
                        'field_of_studies': post.get('field_of_studies'),
                        'pre_tertiary_qualification': post.get('pre_tertiary_qualification'),
                        'aspirant_age': post.get('aspirant_age')
                    })
                if post.get('competition_rule'):
                    values['update_bio'] = False
                    values['competition_rule'] = False
                    snr_aspirants.sudo().write({
                        'updated_cfo_bio': True})
                if post.get('back_home') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                if post.get('back_contact') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = True
                    values['eligibility_status'] = False
                if post.get('back_eligibility') == '<<Back':
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    values['eligibility_status'] = False
                    values['competition_rule'] = False
                if post.get('back_rule') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    values['eligibility_status'] = True
                    values['competition_rule'] = False

            if post.get('cfo_team_edit') and post.get('snr_aspirants'):
                values['cfo_team_edit'] = True
                values['cfo_team'] = True
                values['update_bio'] = False
                values['update_bio_info'] = False
                if snr_aspirants.aspirant_id:
                    values['aspirant_team'] = snr_aspirants.aspirant_id
            if post.get('snr_academic_institution') and not post.get('cfo_team'):
                if post.get('update_bio_info'):
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    snr_academic_institution.sudo().write({
                        'name': post.get('name'),
                        'surname': post.get('surname'),
                        'other_names': post.get('other_names'),
                    })
                if post.get('contact_info'):
                    values['institution_details'] = True
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['update_bio_info'] = False
                    snr_academic_institution.sudo().write({
                        'mobile': post.get('mobile'),
                        'phone': post.get('phone'),
                        'home_phone': post.get('home_phone'),
                        'email_1': post.get('email_1'),
                        'email_2': post.get('email_2'),
                        'street': post.get('street'),
                        'street2': post.get('street2'),
                        'city': post.get('city'),
                        'state_id': post.get('state_id'),
                        'zip': post.get('zip'),
                        'country_id': post.get('country_id')
                    })
                if post.get('institution_details'):
                    values['competition_rule'] = True
                    values['update_bio'] = True
                    values['institution_details'] = False
                    values['update_bio_info'] = False
                    snr_academic_institution.sudo().write({
                        'school_name': post.get('school_name'),
                        'department': post.get('department'),
                        'website': post.get('website'),
                        'stu_street': post.get('stu_street'),
                        'stu_street2': post.get('stu_street2'),
                        'stu_city': post.get('stu_city'),
                        'stu_state_id': post.get('stu_state_id'),
                        'stu_zip': post.get('stu_zip'),
                        'stu_country_id': post.get('stu_country_id'),
                    })
                if post.get('competition_rule'):
                    values['update_bio'] = False
                    values['competition_rule'] = False
                    values['institution_details'] = False
                    snr_academic_institution.sudo().write({
                        'updated_academic_bio': True
                    })
                if post.get('back_home') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                if post.get('back_contact') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = True
                    values['institution_details'] = False
                if post.get('back_institution') == '<<Back':
                    values['contact_info'] = True
                    values['institution_details'] = False
                    values['competition_rule'] = False
                if post.get('back_competition') == '<<Back':
                    values['update_bio_info'] = False
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['institution_details'] = True
                    values['competition_rule'] = False
            if post.get('cfo_team_edit') and post.get('new_form'):
                list = []
                values['cfo_team_edit'] = True
                values['cfo_team'] = True
                values['update_bio'] = False
                values['update_bio_info'] = False
                if snr_academic_institution.cfo_team_ids:
                    values['acadamic_team'] = ''

            if post.get('cfo_team_edit') and post.get('snr_academic_institution'):
                list = []
                values['cfo_team_edit'] = True
                values['cfo_team'] = True
                values['update_bio'] = False
                values['update_bio_info'] = False
                if snr_academic_institution.cfo_team_ids:
                    values['acadamic_team'] = snr_academic_institution.cfo_team_ids
                if post.get('acadamic_team'):
                    team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', post.get('acadamic_team'))])
                    values['acadamic_team'] = team_id
            if post.get('cfo_team_edit') and post.get('snr_employers'):
                list = []
                values['cfo_team_edit'] = True
                values['cfo_team'] = True
                values['update_bio'] = False
                values['update_bio_info'] = False
                if snr_employers.cfo_team_ids:
                    values['employers_team'] = snr_employers.cfo_team_ids
                if post.get('employers_team'):
                    team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', post.get('employers_team'))])
                    values['employers_team'] = team_id

            if post.get('snr_employers'):
                if post.get('update_bio_info'):
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    snr_employers.sudo().write({
                        'name': post.get('name'),
                        'surname': post.get('surname'),
                        'other_names': post.get('other_names'),
                    })
                if post.get('contact_info'):
                    values['employer_details'] = True
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['update_bio_info'] = False
                    snr_employers.sudo().write({
                        'mobile': post.get('mobile'),
                        'phone': post.get('phone'),
                        'home_phone': post.get('home_phone'),
                        'email_1': post.get('email_1'),
                        'street': post.get('street'),
                        'email_2': post.get('email_2'),
                        'street2': post.get('street2'),
                        'city': post.get('city'),
                        'state_id': post.get('state_id'),
                        'zip': post.get('zip'),
                        'country_id': post.get('country_id')
                    })
                if post.get('employer_details'):
                    values['competition_rule'] = True
                    values['update_bio'] = True
                    values['employer_details'] = False
                    values['update_bio_info'] = False
                    snr_employers.sudo().write({
                        'legal_name_employer': post.get('legal_name_employer'),
                        'if_company': post.get('if_company'),
                        'sector': post.get('sector'),
                        'emp_department': post.get('emp_department'),
                        'emp_website': post.get('emp_website'),
                        'emp_street': post.get('emp_street'),
                        'emp_street2': post.get('emp_street2'),
                        'emp_city': post.get('emp_city'),
                        'emp_state_id': post.get('emp_state_id'),
                        'emp_zip': post.get('emp_zip'),
                        'emp_country_id': post.get('emp_country_id')
                    })
                if post.get('competition_rule'):
                    values['update_bio'] = False
                    values['competition_rule'] = False
                    values['employer_details'] = False
                    snr_employers.sudo().write({
                        'updated_emp_bio': True
                    })
                if post.get('back_home') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = False
                    values['update_bio_info'] = False

                if post.get('back_contact') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = True
                    values['employer_details'] = False

                if post.get('back_next_compitition') == '<<Back':
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    values['employer_details'] = False
                    values['competition_rule'] = False

                if post.get('back_rule') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    values['employer_details'] = True
                    values['competition_rule'] = False
                if post.get('cfo_team_edit') and post.get('new_form'):
                    list = []
                    values['cfo_team_edit'] = True
                    values['cfo_team'] = True
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                    if snr_employers.cfo_team_ids:
                        values['employers_team'] = ''

            if post.get('snr_brand_ambassador'):
                if post.get('update_bio_info'):
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    snr_brand_ambassador.sudo().write({
                        'name': post.get('name'),
                        'surname': post.get('surname'),
                        'other_names': post.get('other_names'),
                    })
                if post.get('contact_info'):
                    values['competition_rule'] = True
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['update_bio_info'] = False
                    snr_brand_ambassador.sudo().write({
                        'mobile': post.get('mobile'),
                        'email_1': post.get('email_1'),
                        'email_2': post.get('email_2'),
                    })
                if post.get('competition_rule'):
                    values['update_bio'] = False
                    values['competition_rule'] = False
                    values['contact_info'] = False
                    snr_brand_ambassador.sudo().write({
                        'updated_brand_amb_bio': True
                    })
                if post.get('back_home') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                if post.get('back_contact') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = True
                    values['competition_rule'] = False
                if post.get('back_competition') == '<<Back':
                    values['update_bio_info'] = False
                    values['update_bio'] = True
                    values['contact_info'] = True
                    values['competition_rule'] = False
            if post.get('snr_mentors'):
                if post.get('update_bio_info'):
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    snr_mentors.sudo().write({
                        'name': post.get('name'),
                        'surname': post.get('surname'),
                        'other_names': post.get('other_names'),
                    })
                if post.get('contact_info'):
                    values['competition_rule'] = True
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['update_bio_info'] = False
                    snr_mentors.sudo().write({
                        'mobile': post.get('mobile'),
                        'email_1': post.get('email_1'),
                        'email_2': post.get('email_2'),
                        'street': post.get('street'),
                        'street2': post.get('street2'),
                        'city': post.get('city'),
                        'state_id': post.get('state_id'),
                        'zip': post.get('zip'),
                        'country_id': post.get('country_id'),
                    })
                if post.get('competition_rule'):
                    values['update_bio'] = False
                    values['competition_rule'] = False
                    values['contact_info'] = False
                    snr_mentors.sudo().write({
                        'updated_mentors_bio': True
                    })
                if post.get('back_home') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                if post.get('back_contact') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = True
                    values['competition_rule'] = False
                if post.get('back_competition') == '<<Back':
                    values['update_bio_info'] = False
                    values['update_bio'] = True
                    values['contact_info'] = True
                    values['competition_rule'] = False
            if post.get('snr_media_contestants'):
                if post.get('update_bio_info'):
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    snr_media_contestants.sudo().write({
                        'name': post.get('name'),
                        'surname': post.get('surname'),
                        'other_names': post.get('other_names'),
                    })
                if post.get('contact_info'):
                    values['competition_rule'] = True
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['update_bio_info'] = False
                    snr_media_contestants.sudo().write({
                        'mobile': post.get('mobile'),
                        'phone': post.get('phone'),
                        'home_phone': post.get('home_phone'),
                        'email_1': post.get('email_1'),
                        'email_2': post.get('email_2'),
                        'street': post.get('street'),
                        'street2': post.get('street2'),
                        'city': post.get('city'),
                        'state_id': post.get('state_id'),
                        'zip': post.get('zip'),
                        'country_id': post.get('country_id')
                    })
                if post.get('competition_rule'):
                    values['update_bio'] = False
                    values['competition_rule'] = False
                    values['contact_info'] = False
                    snr_media_contestants.sudo().write({
                        'updated_social_media_bio': True
                    })
        return request.render('cfo_snr_jnr.cfo_senior_team', values)

    @http.route('/is_from_request_id', type="http", auth="public", website=True)
    def is_from_request_id(self, **post):
        return request.render('cfo_snr_jnr.is_from_request_id', post)

    @http.route('/cfo_senior_request', type="http", auth="public", website=True)
    def cfo_senior_request(self, **post):
        res_user = request.env['res.users'].search([('id', '=', request.env.uid)])
        cfo_aspirant_id = request.env['cfo.snr.aspirants'].sudo().search(
            [('email_1', '=', res_user.login), ('is_request', '=', True)])
        if post.get('button') == '1':
            if request.session.get('user_type') == 'Leader':
                cfo_aspirant_id.write({'team_leader': True, 'team_admin': False, 'team_member': False})
            if request.session.get('user_type') == 'Member':
                cfo_aspirant_id.write({'team_leader': False, 'team_admin': False, 'team_member': True})
            cfo_aspirant_id.write({'aspirant_id': cfo_aspirant_id.new_team_id.id, 'is_request': False, })
            team_member_obj = request.env['snr.aspirant.team.member'].sudo().search(
                [('related_user_id', '=', cfo_aspirant_id.id)])
            team_member_acadamic = request.env['snr.academic.team.member'].sudo().search(
                [('related_user_aspirant_id', '=', cfo_aspirant_id.id)])
            team_member_employers = request.env['snr.employer.team.member'].sudo().search(
                [('related_user_id', '=', cfo_aspirant_id.id)])
            if team_member_obj:
                if len(team_member_obj) == 1:
                    team_member_obj.write({'member_status': 'Accept'})
                if post.get('team_id') != None:
                    team_member_old_obj = request.env['snr.aspirant.team.member'].sudo().search(
                        [('related_user_id', '=', cfo_aspirant_id.id), ('team_id', '!=', int(post.get('team_id')))])
                if team_member_old_obj:
                    team_member_old_obj.unlink();
                team_member_new = request.env['snr.aspirant.team.member'].sudo().search(
                    [('related_user_id', '=', cfo_aspirant_id.id), ('team_id', '=', int(post.get('team_id')))])
                if team_member_new:
                    team_member_new.write({'member_status': 'Accept', 'member_accept_data': True})
            if team_member_acadamic:
                if len(team_member_acadamic) == 1:
                    team_member_acadamic.write({'member_status': 'Accept'})

                team_member_old_acadamic_obj = request.env['snr.academic.team.member'].sudo().search(
                    [('related_user_aspirant_id', '=', cfo_aspirant_id.id),
                     ('team_id', '!=', int(post.get('team_id')))])
                if team_member_old_acadamic_obj:
                    team_member_old_acadamic_obj.unlink();

                team_member_acadamic_new = request.env['snr.academic.team.member'].sudo().search(
                    [('related_user_aspirant_id', '=', cfo_aspirant_id.id), ('team_id', '=', int(post.get('team_id')))])
                if team_member_acadamic_new:
                    team_member_acadamic_new.write({'member_status': 'Accept', 'member_accept_data': True})

            if team_member_employers:
                if len(team_member_employers) == 1:
                    team_member_employers.write({'member_status': 'Accept'})

                team_member_old_employers_obj = request.env['snr.employer.team.member'].sudo().search(
                    [('related_user_id', '=', cfo_aspirant_id.id),
                     ('team_id', '!=', int(post.get('team_id')))])
                if team_member_old_employers_obj:
                    team_member_old_employers_obj.unlink();

                team_member_employers_new = request.env['snr.employer.team.member'].sudo().search(
                    [('related_user_id', '=', cfo_aspirant_id.id), ('team_id', '=', int(post.get('team_id')))])
                if team_member_employers_new:
                    team_member_employers_new.write({'member_status': 'Accept', 'member_accept_data': True})
            request.session['user_type'] = ""
            return request.redirect('/cfo_senior')

        if post.get('button') == '2':
            if request.session.get('user_type') == 'Leader':
                cfo_aspirant_id.write({'team_leader': False, 'team_admin': False, 'team_member': False})
            if request.session.get('user_type') == 'Member':
                cfo_aspirant_id.write({'team_leader': False, 'team_admin': False, 'team_member': False})
            cfo_aspirant_id.write({'is_request': False, })
            team_member_new = request.env['snr.aspirant.team.member'].sudo().search(
                [('related_user_id', '=', cfo_aspirant_id.id), ('team_id', '=', int(post.get('team_id')))])
            if team_member_new:
                team_member_new.write({'member_status': 'Rejected'})
            team_member_acadamic_new = request.env['snr.academic.team.member'].sudo().search(
                [('related_user_aspirant_id', '=', cfo_aspirant_id.id), ('team_id', '=', int(post.get('team_id')))])
            if team_member_acadamic_new:
                team_member_acadamic_new.write({'member_status': 'Rejected'})
            team_member_employers_new = request.env['snr.employer.team.member'].sudo().search(
                [('related_user_id', '=', cfo_aspirant_id.id), ('team_id', '=', int(post.get('team_id')))])
            if team_member_employers_new:
                team_member_employers_new.write({'member_status': 'Rejected'})
            request.session['user_type'] = ""
            return request.redirect('/cfo_senior')

    @http.route('/CFO/senior/register_cfo_senior', type='http', auth="public", website=True)
    def register_cfo_senior(self, **post):
        member_values = {}
        if post.get('cfo_competition') and post.get('cfo_membertype'):
            partner = request.env.user.partner_id
            user = request.env.user
            member_values.update({'name': user.name, 'partner_id': partner.id, 'user_id': user.id, 'team_admin': True})
            if post.get('cfo_competition'):
                member_values.update({'cfo_comp': int(post.pop('cfo_competition'))})
            member_values.update({'cfo_member_type': post.pop('cfo_membertype')})
            if post.get('cfo_source'):
                member_values.update({'registrants_source': post.pop('cfo_source')})
            if post.get('other'):
                member_values.update({'other_reason': post.pop('other', '')})
            if post.get('social_media_options'):
                member_values.update({'social_media_options': post.pop('social_media_options', '')})
            member_values.update({'email_1': user.login, 'password': user.password, 'username': user.login})
            if datetime.date.today().month in [4, 5, 6, 7, 8, 9, 10, 11, 12]:
                member_values.update({'cfo_competition_year': str(datetime.date.today().year + 1)})
            else:
                member_values.update({'cfo_competition_year': str(datetime.date.today().year)})
        if member_values:
            print("\n\n\n\n============member_value====",member_values)
            user._create_member(member_values)
        return request.redirect('/cfo_senior')

    @http.route('/CFO/junior/register_cfo_junior', type='http', auth="public", website=True)
    def register_cfo_junior(self, **post):
        member_values = {}
        if post.get('cfo_competition') and post.get('cfo_membertype'):
            partner = request.env.user.partner_id
            user = request.env.user
            member_values.update({'name': user.name, 'partner_id': partner.id, 'user_id': user.id, 'team_admin': True})
            if post.get('cfo_competition'):
                member_values.update({'cfo_comp': int(post.pop('cfo_competition'))})
            member_values.update({'cfo_member_type': post.pop('cfo_membertype')})
            if post.get('cfo_source'):
                member_values.update({'cfo_registrants_source': post.pop('cfo_source')})
            if post.get('other'):
                member_values.update({'other': post.pop('other', '')})
            if post.get('social_media_options'):
                member_values.update({'social_media_options': post.pop('social_media_options', '')})
            member_values.update({'email_1': user.login, 'password': user.password, 'username': user.login})
            if datetime.date.today().month in [4, 5, 6, 7, 8, 9, 10, 11, 12]:
                member_values.update({'cfo_competition_year': str(datetime.date.today().year + 1)})
            else:
                member_values.update({'cfo_competition_year': str(datetime.date.today().year)})
        if member_values:
            user._create_member(member_values)
        return request.redirect('/cfo_junior')

    @http.route('/check_user_team', type='json', auth="public", website=True)
    def check_user_team(self, **post):
        if post.get('email') and not post.get('user_type'):
            res = request.env['res.users'].sudo().search(
                [('login', '=', post.get('email'))])
            if res:
                print("\n\n\n\n\n\n============into res call=========")
                cfo_snr = request.env['cfo.snr.aspirants'].sudo().search([('email_1', '=', post.get('email'))])
                cfo_acd_snr = request.env['academic.institution.snr'].sudo().search([('email_1', '=', post.get('email'))])
                cfo_emp_snr = request.env['employers.snr'].sudo().search([('email_1', '=', post.get('email'))])
                cfo_mtr_snr = request.env['mentors.snr'].sudo().search([('email_1', '=', post.get('email'))])
                cfo_vlte_snr = request.env['volunteers.snr'].sudo().search([('email_1', '=', post.get('email'))])
                cfo_amb_snr = request.env['brand.ambassador.snr'].sudo().search([('email_1', '=', post.get('email'))])
                cfo_smc_snr = request.env['social.media.contestants.snr'].sudo().search([('email_1', '=', post.get('email'))])

                cfo_jnr = request.env['cfo.jnr.aspirants'].sudo().search([('email_1', '=', post.get('email'))])
                cfo_acd_jnr = request.env['academic.institution.jnr'].sudo().search([('email_1', '=', post.get('email'))])
                cfo_mtr_jnr = request.env['mentors.jnr'].sudo().search([('email_1', '=', post.get('email'))])
                cfo_amb_jnr = request.env['brand.ambassador.jnr'].sudo().search([('email_1', '=', post.get('email'))])

                if cfo_snr or cfo_acd_snr or cfo_emp_snr or cfo_mtr_snr or cfo_mtr_snr or cfo_vlte_snr or cfo_amb_snr or cfo_smc_snr or cfo_jnr or cfo_acd_jnr or cfo_mtr_jnr or cfo_amb_jnr:
                    print("\n\n\n\n=========res.id=====",res.id)
                    return {'user_id': res.id}
                # elif cfo_jnr or cfo_acd_jnr or cfo_mtr_jnr or cfo_amb_jnr:
                #     return {'user_id': res.id}
                else:
                    return {'new_user':True}
            else:
                return {'create_user': True}
        if post.get('email') and post.get('user_type'):
            res = request.env['res.users'].sudo().search(
                [('login', '=', post.get('email'))])
            if not res:
                return {
                    'new_user': True
                }
            else:
                return {'user_id': res.id}

    @http.route('/check_team_name', type='json', auth="public", website=True)
    def check_team_name(self, **post):
        if post.get('team_name'):
            team_name_snr = request.env['cfo.team.snr'].sudo().search([('name', '=', post.get('team_name'))])
            team_name_jnr = request.env['cfo.team.jnr'].sudo().search([('name', '=', post.get('team_name'))])
            if team_name_snr:
                return team_name_snr
            if team_name_jnr:
                return team_name_jnr

    @http.route('/request_to_join',type='json', auth="public", website=True)
    def check_request_member(self, **post):
        res = request.env['res.users'].sudo().search([('login', '=', post.get('email'))])
        if res.state == 'new':
            return {'update_bio':True}
        else:
            if post.get('user_type') == 'Brand Ambassador' or post.get('user_type') == 'Mentor':
                amb_id = request.env['brand.ambassador.snr'].sudo().search(
                    [('user_id', '=', int(post.get('user_id')))])
                mentor_id = request.env['mentors.snr'].sudo().search(
                    [('user_id', '=', int(post.get('user_id')))])
                amb_jnr_id = request.env['brand.ambassador.jnr'].sudo().search(
                    [('user_id', '=', int(post.get('user_id')))])
                mentor_jnr_id = request.env['mentors.jnr'].sudo().search(
                    [('user_id', '=', int(post.get('user_id')))])
                if mentor_id or amb_id or amb_jnr_id or mentor_jnr_id:
                    return {'request_to_join': True}
                else:
                    return {'request_to_join': False}
            if post.get('user_type') in ['Leader', 'Member']:
                member_id = request.env['cfo.snr.aspirants'].sudo().search(
                    [('user_id', '=', int(post.get('user_id')))])
                member_jnr_id = request.env['cfo.jnr.aspirants'].sudo().search(
                    [('user_id', '=', int(post.get('user_id')))])
                if member_id or member_jnr_id:
                    return {'request_to_join': True}
                else:
                    return {'request_to_join': False}

    @http.route('/get_cfo_snr_member', type='json', auth="public", website=True)
    def get_cfo_snr_member(self, **post):
        # team_member = request.env['cfo.snr.member.add'].sudo().search([],limit=1, order="id")
        team_member = request.env['ir.config_parameter'].sudo().get_param('cfo_snr_jnr.snr_total_member')
        print("\n\n\n\n\n\n===============team member=========",team_member)
        if team_member:
            return {'team_member': team_member}
        else:
            return {'team_member': 3}

    @http.route('/get_cfo_jnr_member', type='json', auth="public", website=True)
    def get_cfo_jnr_member(self, **post):
        # team_member = request.env['jnr.member.config.settings'].sudo().search([], limit=1, order="id")
        team_member = request.env['ir.config_parameter'].sudo().get_param('cfo_snr_jnr.total_member')
        if team_member:
            return {'team_member': team_member}
        else:
            return {'team_member': 2}

    @http.route('/create_new_member', type='json', auth="public", website=True)
    def create_new_member(self, **post):
        res_user = request.env['res.users'].sudo().search([('login', '=', post.get('email'))])
        cfo_snr = request.env['cfo.snr.aspirants'].sudo().search([('email_1', '=', post.get('email'))])
        # cfo_acd_snr = request.env['academic.institution.snr'].sudo().search([('email_1', '=', post.get('email'))])
        # cfo_emp_snr = request.env['employers.snr'].sudo().search([('email_1', '=', post.get('email'))])
        cfo_mtr_snr = request.env['mentors.snr'].sudo().search([('email_1', '=', post.get('email'))])
        # cfo_vlte_snr = request.env['volunteers.snr'].sudo().search([('email_1', '=', post.get('email'))])
        cfo_amb_snr = request.env['brand.ambassador.snr'].sudo().search([('email_1', '=', post.get('email'))])
        # cfo_smc_snr = request.env['social.media.contestants.snr'].sudo().search([('email_1', '=', post.get('email'))])

        cfo_jnr = request.env['cfo.jnr.aspirants'].sudo().search([('email_1', '=', post.get('email'))])
        cfo_acd_jnr = request.env['academic.institution.jnr'].sudo().search([('email_1', '=', post.get('email'))])
        cfo_mtr_jnr = request.env['mentors.jnr'].sudo().search([('email_1', '=', post.get('email'))])
        cfo_amb_jnr = request.env['brand.ambassador.jnr'].sudo().search([('email_1', '=', post.get('email'))])

        if not cfo_snr or not cfo_mtr_snr or not cfo_mtr_snr or cfo_amb_snr or not cfo_jnr or not cfo_mtr_jnr or not cfo_amb_jnr or not cfo_acd_jnr:
            if not res_user:
                print("\n\n\n\n\====callllll========")
                user = request.env['res.users'].sudo().create({
                    'name': post.get('name'),
                    'login': post.get('email'),
                    'state': 'new',
                    'in_group_9': True,
                    'share': True,
                })
                request.session['cfo_login'] = True
                request.session['is_from_new_member'] = True
                user.partner_id.write({'email': post.get('email'), 'is_from_new_member': True, 'cfo_user': True})
            else:
                user = request.env['res.users'].sudo().search([('login', '=', post.get('email'))])
            if post.get('from_aspirant'):
                if post.get('user_type') in ['Leader']:
                    request.env['cfo.snr.aspirants'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'member_accept': True,
                        'team_leader': True,
                        'is_from_create_member': True,
                        'aspirant_id': post.get('team_id'),
                        'cfo_competition_year': str(post.get('year'))
                    })
                if post.get('user_type') in ['Member']:
                    request.env['cfo.snr.aspirants'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'member_accept': True,
                        'team_member': True,
                        'is_from_create_member': True,
                        'aspirant_id': post.get('team_id'),
                        'cfo_competition_year': str(post.get('year'))
                    })
                if post.get('user_type') == 'Mentor':
                    request.env['mentors.snr'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'cfo_competition_year': str(post.get('year'))
                    })

                if post.get('user_type') == 'Brand Ambassador':
                    request.env['brand.ambassador.snr'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'cfo_competition_year': str(post.get('year'))
                    })
                user.with_context(create_user=True,user_type=post.get('user_type'),email=post.get('email'),team_name=post.get('team_name')).create_password()
            if post.get('from_acadamic'):
                if post.get('user_type') in ['Leader']:
                    request.env['cfo.snr.aspirants'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'member_accept': True,
                        'team_leader': True,
                        'is_from_create_member': True,
                        'aspirant_id': post.get('team_id'),
                        'cfo_competition_year': str(post.get('year')),
                        'cfo_type': 'Academic Institution'
                    })
                if post.get('user_type') in ['Member']:
                    request.env['cfo.snr.aspirants'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'member_accept': True,
                        'team_member': True,
                        'is_from_create_member': True,
                        'aspirant_id': post.get('team_id'),
                        'cfo_competition_year': str(post.get('year')),
                        'cfo_type': 'Academic Institution'
                    })
                if post.get('user_type') == 'Mentor':
                    request.env['mentors.snr'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'cfo_competition_year': str(post.get('year'))
                    })
                if post.get('user_type') == 'Brand Ambassador':
                    request.env['brand.ambassador.snr'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'cfo_competition_year': str(post.get('year'))
                    })
                user.with_context(create_user=True,user_type=post.get('user_type'),email=post.get('email'),team_name=post.get('team_name')).create_password()
            if post.get('from_employer'):
                if post.get('user_type') in ['Leader']:
                    request.env['cfo.snr.aspirants'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'member_accept': True,
                        'team_leader': True,
                        'is_from_create_member': True,
                        'aspirant_id': post.get('team_id'),
                        'cfo_competition_year': str(post.get('year')),
                        'cfo_type': 'Employer'
                    })
                if post.get('user_type') in ['Member']:
                    request.env['cfo.snr.aspirants'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'member_accept': True,
                        'team_member': True,
                        'is_from_create_member': True,
                        'aspirant_id': post.get('team_id'),
                        'cfo_competition_year': str(post.get('year')),
                        'cfo_type': 'Employer'
                    })
                if post.get('user_type') == 'Mentor':
                    request.env['mentors.snr'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'cfo_competition_year': str(post.get('year'))
                    })
                if post.get('user_type') == 'Brand Ambassador':
                    request.env['brand.ambassador.snr'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'cfo_competition_year': str(post.get('year'))
                    })
                user.with_context(create_user=True, user_type=post.get('user_type'),email=post.get('email'),team_name=post.get('team_name')).create_password()
            if post.get('from_jnr_school'):
                if post.get('user_type') in ['Leader']:
                    request.env['cfo.jnr.aspirants'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'member_accept': True,
                        'team_leader': True,
                        'is_from_create_member': True,
                        'aspirant_id': post.get('team_id'),
                        'cfo_competition_year': str(post.get('year')),
                        'cfo_type': 'Secondary/High School'
                    })
                if post.get('user_type') in ['Member']:
                    request.env['cfo.jnr.aspirants'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'member_accept': True,
                        'team_member': True,
                        'is_from_create_member': True,
                        'aspirant_id': post.get('team_id'),
                        'cfo_competition_year': str(post.get('year')),
                        'cfo_type': 'Secondary/High School'
                    })
                if post.get('user_type') == 'Mentor':
                    request.env['mentors.jnr'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'cfo_competition_year': str(post.get('year'))
                    })
                if post.get('user_type') == 'Brand Ambassador':
                    request.env['brand.ambassador.jnr'].sudo().create({
                        'partner_id': user.partner_id.id,
                        'email_1': post.get('email'),
                        'user_id': user.id,
                        'cfo_competition_year': str(post.get('year'))
                    })
                user.with_context(create_user=True,user_type=post.get('user_type'),email=post.get('email'),team_name=post.get('team_name')).create_password()
        #     if post.get('from_aspirant') or post.get('from_acadamic') or post.get('from_employer') or post.get('from_jnr_school'):
        #         create_mode = bool(self.env.context.get('create_user'))
        #
        #         # no time limit for initial invitation, only for reset password
        #         expiration = False if create_mode else now(days=+1)
        #
        #         self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)
        #
        #         if post.get('user_type') in ['Leader','Member']:
        #             res = request.env['cfo.snr.aspirants'].sudo().search(
        #                 [('user_id', '=', user.id)])
        #             aspirant_team_member_id = request.env['snr.aspirant.team.member'].sudo().search(
        #                 [('related_user_id', '=', res.id), ('member_status', '=', 'Accept')])
        #             res.sudo().write({
        #                 'is_request': True,
        #             })
        #             template_leader_member = request.env.ref('cfo_snr_jnr.email_template_request_for_join',
        #                                               raise_if_not_found=False)
        #             if template_leader_member:
        #                 template_leader_member.sudo().with_context(
        #                     user_type=post.get('user_type'),
        #                     team_name=post.get('team_name'),
        #                     email_to=post.get('email')
        #                 ).with_context(create_user=True, cfo_login=True).send_mail(res.id, force_send=True)
        #         if post.get('user_type') == 'Mentor':
        #             mentor_id = request.env['mentors.snr'].sudo().search(
        #                 [('user_id', '=',user.id)])
        #             template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor',
        #                                               raise_if_not_found=False)
        #             if template_mentor:
        #                 template_mentor.sudo().with_context(
        #                     user_type=post.get('user_type'),
        #                     team_name=post.get('team_name'),
        #                     email_to=post.get('email')
        #                 ).with_context(create_user=True, cfo_login=True).send_mail(mentor_id.id, force_send=True)
        #         if post.get('user_type') == 'Brand Ambassador':
        #             amb_id = request.env['brand.ambassador.snr'].sudo().search(
        #                 [('user_id', '=', user.id)])
        #             template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb',
        #                                               raise_if_not_found=False)
        #             if template_amb:
        #                 template_amb.sudo().with_context(
        #                     user_type=post.get('user_type'),
        #                     team_name=post.get('team_name'),
        #                     email_to=post.get('email')
        #                 ).with_context(create_user=True, cfo_login=True).send_mail(amb_id.id, force_send=True)
        else:
            return {'email_exist': True}

    @http.route('/get_country', type='json', auth='public', website=True)
    def get_country(self, **post):
        state_id = request.env['res.country.state'].search([('id', '=', post.get('state_id'))])
        return {'name': state_id.country_id.name, 'id': str(state_id.country_id.id)}

    @http.route('/update_team_from_report', type='json', auth='public', website=True)
    def update_team_from_report(self, **post):
        team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', post.get('aspirant_team'))])
        if post.get('member_type') == 'Brand Ambassador':
            brand_ambassador = request.env['brand.ambassador.snr'].sudo().search(
                [('email_1', 'ilike', post.get('email'))], limit=1)
            team_id.write({'brand_amb_id': brand_ambassador.id})
        if post.get('member_type') == 'Mentor':
            mentor_id = request.env['mentors.snr'].sudo().search(
                [('email_1', 'ilike', post.get('email'))], limit=1)
            team_id.write({'mentor_id': mentor_id.id})

    @http.route('/send_reminder_mail', type="json", auth="public", website=True)
    def send_reminder_mail(self, **post):
        if post.get('team_id'):
            cfo_report_deadline_date = ''
            team_snr_id = request.env['cfo.team.snr'].sudo().search([('id', '=', post.get('team_id'))])
            team_jnr_id= request.env['cfo.team.jnr'].sudo().search([('id', '=', post.get('team_id'))])
            # template = request.env.ref('cfo_snr_jnr.email_template_upload_report_reminder_snr',
            #                            raise_if_not_found=False)
            _logger.info("send_reminder_mail <%s>",team_jnr_id)
            print("\n\n\n\n\n\n\n=================================send reminder mail=========",team_snr_id,team_jnr_id)
            if team_snr_id:
                tz = pytz.timezone(request.env.user.tz) if request.env.user.tz else pytz.utc
                life_date = datetime.datetime.strptime(team_snr_id.cfo_report_deadline_date,
                                                       DEFAULT_SERVER_DATETIME_FORMAT)
                life_date = (life_date + timedelta(hours=2)).strftime('%d-%m-%Y %H:%M:%S')
                cfo_report_deadline_date = life_date
            if team_jnr_id:
                tz = pytz.timezone(request.env.user.tz) if request.env.user.tz else pytz.utc
                life_date = datetime.datetime.strptime(team_jnr_id.cfo_report_deadline_date,
                                                       DEFAULT_SERVER_DATETIME_FORMAT)
                life_date = (life_date + timedelta(hours=2)).strftime('%d-%m-%Y %H:%M:%S')
                cfo_report_deadline_date = life_date
            if team_snr_id.team_type == 'CFO Aspirant':
                for member_id in team_snr_id.aspirant_team_member_ids:
                    template = request.env.ref('cfo_snr_jnr.email_template_upload_report_reminder_snr',
                                               raise_if_not_found=False)
                    # if template and member_id.user_type == 'Admin':
                    print("\n\n\n\n\n\n=========team_snr_id.cfo_report_deadline_date=====",team_snr_id.cfo_report_deadline_date)
                    print("\n\n\n\n\n\n=========member_id.related_user_id.name=====", member_id.related_user_id.name)
                    if template and ((member_id.user_type == 'Admin') or (member_id.user_type == 'Leader') or (member_id.user_type == 'Member')):
                        template.sudo().with_context(
                            team_id=team_snr_id.id,
                            team_name=team_snr_id.name,
                            cfo_report_deadline_date=cfo_report_deadline_date,
                            email_to=member_id.related_user_id.email_1,
                        ).send_mail(member_id.related_user_id.id, force_send=True)
                return True
            if team_jnr_id.team_type == 'CFO Aspirant':
                for member_id in team_jnr_id.aspirant_team_member_ids:
                    template = request.env.ref('cfo_snr_jnr.email_template_upload_report_reminder_jnr',
                                               raise_if_not_found=False)
                    # if template and member_id.user_type == 'Admin':
                    if template and ((member_id.user_type == 'Admin') or (member_id.user_type == 'Leader') or (member_id.user_type == 'Member')):
                        _logger.info("member_id.related_user_id.name <%s>",member_id.related_user_id.name)
                        print("\n\n\n\n\n\n=========member_id.related_user_id.name=====",member_id.related_user_id.name)
                        template.sudo().with_context(
                            team_id=team_jnr_id.id,
                            team_name=team_jnr_id.name,
                            cfo_report_deadline_date=cfo_report_deadline_date,
                            email_to=member_id.related_user_id.email_1,
                        ).send_mail(member_id.related_user_id.id, force_send=True)
                return True
            if team_snr_id.team_type == 'Academic Institution':
                for member_id in team_snr_id.academic_team_member_ids:
                    template = request.env.ref('cfo_snr_jnr.email_template_upload_report_reminder_snr',
                                               raise_if_not_found=False)
                    # if template and member_id.related_user_aspirant_id and ((member_id.user_type == 'Admin') or (member_id.user_type == 'Leader')):
                    print("\n\n\n\n\n\n=========member_id.related_user_aspirant_id.id=====",
                          member_id.related_user_aspirant_id.name)
                    if template and member_id.related_user_aspirant_id and ((member_id.user_type == 'Admin') or (member_id.user_type == 'Leader') or (member_id.user_type == 'Member')):
                        template.sudo().with_context(
                            team_id=team_snr_id.id,
                            team_name=team_snr_id.name,
                            cfo_report_deadline_date=cfo_report_deadline_date,
                            email_to=member_id.related_user_aspirant_id.email_1,
                        ).send_mail(member_id.related_user_aspirant_id.id, force_send=True)

                    template_acadamic = request.env.ref('cfo_snr_jnr.email_template_upload_report_reminder_snr_acadamic',
                                                        raise_if_not_found=False)
                    # if template_acadamic and member_id.related_user_id and member_id.user_type == 'Admin':
                    if template_acadamic and member_id.related_user_id:
                        template_acadamic.sudo().with_context(
                            team_id=team_snr_id.id,
                            team_name=team_snr_id.name,
                            cfo_report_deadline_date=cfo_report_deadline_date,
                            email_to=member_id.related_user_id.email_1,
                        ).send_mail(member_id.related_user_id.id, force_send=True)
                return True

            if team_jnr_id.team_type == 'Secondary/High School':
                # for member_id in team_jnr_id.highschool_team_member_ids:
                #     template_highschool = request.env.ref('cfo_snr_jnr.email_template_upload_report_reminder_jnr_acadamic',
                #                                         raise_if_not_found=False)
                #     # if template_highschool and member_id.related_user_id and member_id.user_type == 'Admin':
                #     if template_highschool and (member_id.related_user_id or member_id.related_user_aspirant_id):
                #         print ("\n\n\n\n\n=========member_id=======",member_id.related_user_id,member_id.related_user_aspirant_id)
                #         template_highschool.sudo().with_context(
                #             team_id=team_jnr_id.id,
                #             team_name=team_jnr_id.name,
                #             cfo_report_deadline_date=team_jnr_id.cfo_report_deadline_date,
                #             email_to=member_id.related_user_id.email_1 or member_id.related_user_aspirant_id.email_1,
                #         ).send_mail(member_id.related_user_id.id if member_id.related_user_id.id else member_id.related_user_aspirant_id.id, force_send=True)
                # return True
                for member_id in team_jnr_id.highschool_team_member_ids:
                    template = request.env.ref('cfo_snr_jnr.email_template_upload_report_reminder_jnr',
                                               raise_if_not_found=False)
                    _logger.info("member_id.related_user_aspirant_id.id <%s> and <%s>",member_id.related_user_id.name, member_id.related_user_aspirant_id.name)
                    if template and member_id.related_user_aspirant_id and ((member_id.user_type == 'Admin') or (member_id.user_type == 'Leader') or (member_id.user_type == 'Member')):
                        _logger.info("member_id.related_user_aspirant_id.id <%s>", member_id.related_user_aspirant_id.name)
                        print("\n\n\n\n\n\n=========member_id.related_user_aspirant_id.id=====",member_id.related_user_aspirant_id.name)
                        template.sudo().with_context(
                            team_id=team_jnr_id.id,
                            team_name=team_jnr_id.name,
                            cfo_report_deadline_date=cfo_report_deadline_date,
                            email_to=member_id.related_user_aspirant_id.email_1,
                        ).send_mail(member_id.related_user_aspirant_id.id, force_send=True)

                    template_highschool = request.env.ref('cfo_snr_jnr.email_template_upload_report_reminder_jnr_acadamic',raise_if_not_found=False)
                    if template_highschool and member_id.related_user_id:
                        template_highschool.sudo().with_context(
                            team_id=team_jnr_id.id,
                            team_name=team_jnr_id.name,
                            cfo_report_deadline_date=cfo_report_deadline_date,
                            email_to=member_id.related_user_id.email_1,
                        ).send_mail(member_id.related_user_id.id, force_send=True)
                return True

            if team_snr_id.team_type == 'Employer':
                for member_id in team_snr_id.employer_team_member_ids:
                    template = request.env.ref('cfo_snr_jnr.email_template_upload_report_reminder_snr',
                                               raise_if_not_found=False)
                    if template and member_id.related_user_aspirant_id and ((member_id.user_type == 'Admin') or (member_id.user_type == 'Leader') or (member_id.user_type == 'Member')):
                        print("\n\n\n\n=======member_id===in member_id.related_user_aspirant_id ======", member_id.related_user_aspirant_id)
                        template.sudo().with_context(
                            team_id=team_snr_id.id,
                            team_name=team_snr_id.name,
                            cfo_report_deadline_date=cfo_report_deadline_date,
                            email_to=member_id.related_user_aspirant_id.email_1,
                        ).send_mail(member_id.related_user_aspirant_id.id, force_send=True)

                    template_employer = request.env.ref('cfo_snr_jnr.email_template_upload_report_reminder_snr_employer',
                                                        raise_if_not_found=False)
                    # if template_employer and member_id.related_user_id and member_id.user_type == 'Admin':
                    if template_employer and member_id.related_user_id:
                        template_employer.sudo().with_context(
                            team_id=team_snr_id.id,
                            team_name=team_snr_id.name,
                            cfo_report_deadline_date=cfo_report_deadline_date,
                            email_to=member_id.related_user_id.email_1,
                        ).send_mail(member_id.related_user_id.id, force_send=True)
                return True

    @http.route('/download_report', type='json', auth="public", website=True)
    def download_report(self, **post):
        attachment_ids = request.env['ir.attachment'].sudo().search([('snr_team_id', '=', int(post.get('team_id'))),
                                                                     ('mimetype', '=', 'application/pdf')],
                                                                    order="id desc", limit=1)

    @http.route("/remove_attachment_from_team", type="json", auth="public", website=True)
    def remove_attachment_from_team(self, **post):
        if post.get('attachment_id'):
            attachment_id = request.env['ir.attachment'].sudo().search([('id', '=', post.get('attachment_id'))])
            if attachment_id:
                attachment_id.unlink();
                return True

    @http.route('/create_team', type='json', auth="public", website=True)
    def create_team(self, **post):
        res_user_ids = request.env['res.users'].sudo().search([('login','=',post.get('email'))])
        if post.get('aspirant_id') and not post.get('aspirant_team'):
            aspirant_id = request.env['cfo.snr.aspirants'].sudo().search([('id', '=', int(post.get('aspirant_id')))],
                                                                         limit=1)
            aspirant_ids = request.env['cfo.snr.aspirants'].sudo().browse()
            if not aspirant_id.aspirant_id:
                team_id = request.env['cfo.team.snr'].sudo().create({
                    'name': post.get('name'),
                    'ref_name': post.get('sys_name'),
                    'team_type': 'CFO Aspirant',
                    'cfo_competition_year': aspirant_id.cfo_competition_year,
                    'aspirant_admin_id': aspirant_id.id,
                    'cfo_comp': 'CFO SNR'
                })
                if post.get('member_request_list'):
                    '''
                    Send email for Join Our Team.
                    '''
                    for each_request in post.get('member_request_list'):
                        if each_request.get('user_type') == 'Mentor' or each_request.get('user_type') == 'Brand Ambassador':
                            mentor_id = request.env['mentors.snr'].sudo().search(
                                [('user_id', '=', int(each_request.get('user_id')))])
                            amb_id = request.env['brand.ambassador.snr'].sudo().search(
                                [('user_id', '=', int(each_request.get('user_id')))])
                            if mentor_id:
                                template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor_snr',
                                                                  raise_if_not_found=False)
                                if template_mentor:
                                    template_mentor.sudo().with_context(
                                        user_type=each_request.get('user_type'),
                                        team_id=team_id.id,
                                        team_name=team_id.ref_name,
                                        # email_to=each_request.get('email'),
                                        email_cc='thecfo@charterquest.co.za',
                                    ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(mentor_id.id, force_send=True)
                            if amb_id:
                                template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb_snr',
                                                               raise_if_not_found=False)
                                if template_amb:
                                    template_amb.sudo().with_context(
                                        user_type=each_request.get('user_type'),
                                        team_id=team_id.id,
                                        team_name=team_id.ref_name,
                                        # email_to=each_request.get('email'),
                                        email_cc='thecfo@charterquest.co.za',
                                    ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(amb_id.id, force_send=True)

                        # if each_request.get('user_type') == 'Brand Ambassador':
                        #     amb_id = request.env['brand.ambassador.snr'].sudo().search(
                        #         [('user_id', '=', int(each_request.get('user_id')))])
                        #
                        #     template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb',
                        #                                    raise_if_not_found=False)
                        #
                        #     if template_amb:
                        #         template_amb.sudo().with_context(
                        #             user_type=each_request.get('user_type'),
                        #             team_id=team_id.id,
                        #             team_name=team_id.ref_name,
                        #             email_to=each_request.get('email'),
                        #             email_cc='thecfo@charterquest.co.za',
                        #         ).send_mail(amb_id.id, force_send=True)

                        if each_request.get('user_type') in ['Leader', 'Member']:
                            res = request.env['cfo.snr.aspirants'].sudo().search(
                                [('user_id', '=', int(each_request.get('user_id')))])
                            aspirant_team_member_id = request.env['snr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', res.id), ('member_status', '=', 'Accept')])

                            res.sudo().write({
                                'is_request': True,
                                'new_team_id': team_id.id
                            })
                            template = request.env.ref('cfo_snr_jnr.email_template_request_for_join_snr',
                                                       raise_if_not_found=False)
                            if template:
                                template.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(res.id, force_send=True)

                            aspirant_team_member_id.write({'aspirant_member_requested': True})
                team_id._compute_remaining_time_deadline()
                for each in post.get('list_of_member'):
                    member_ids = request.env['snr.aspirant.team.member'].sudo().search(
                        [('team_id', '=', team_id.id), ('user_type', '=', 'Member')])
                    user = request.env['cfo.snr.aspirants'].sudo().search(
                        [('email_1', '=', str(each['email']))], limit=1)
                    mentor = request.env['mentors.snr'].sudo().search(
                        [('email_1', '=', str(each['email']))], limit=1)
                    brand_ambassador = request.env['brand.ambassador.snr'].sudo().search(
                        [('email_1', '=', str(each['email']))], limit=1)
                    if not user and not mentor and not brand_ambassador and not member_ids:
                        return {'error': 'error'}
                    else:
                        if len(member_ids) <= 3:
                            if each['user_type'] == 'Member':
                                if not request.env['snr.aspirant.team.member'].sudo().search(
                                        [('related_user_id', '=', user.id), ('user_type', '=', 'Member')]):
                                    request.env['snr.aspirant.team.member'].sudo().create({
                                        'team_id': team_id.id,
                                        'related_user_id': user.id,
                                        'user_type': each['user_type'],
                                        'member_status': 'Accept'
                                    })
                                    user.sudo().write({
                                        'team_status': 'Accept',
                                        'team_member': True,
                                        'aspirant_id': team_id.id,
                                        'new_team_id': team_id.id
                                    })
                                elif request.env['snr.aspirant.team.member'].sudo().search(
                                        [('related_user_id', '=', user.id), ('user_type', '=', 'Member'),
                                         ('aspirant_member_requested', '=', True)]):
                                    request.env['snr.aspirant.team.member'].sudo().create({
                                        'team_id': team_id.id,
                                        'related_user_id': user.id,
                                        'user_type': each['user_type'],
                                        'member_status': 'Pending'
                                    })
                        else:
                            return {'member_limit_error': True}
                        if each['user_type'] == 'Admin':
                            team_id.aspirant_admin_id = user.id

                            if not request.env['snr.aspirant.team.member'].sudo().search(
                                    [('related_user_id', '=', user.id), ('user_type', '=', 'Admin')]):
                                mem_id = request.env['snr.aspirant.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_id': user.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Accept'
                                })
                                user.sudo().write({
                                    'team_status': 'Accept',
                                    'team_admin': True,
                                    'aspirant_id': team_id.id,
                                    'new_team_id': team_id.id
                                })
                        if each['user_type'] == 'Leader':
                            team_id.aspirant_leader_id = user.id
                            if not request.env['snr.aspirant.team.member'].sudo().search(
                                    [('related_user_id', '=', user.id), ('user_type', '=', 'Leader')]):
                                request.env['snr.aspirant.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_id': user.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Accept'
                                })
                                user.sudo().write({
                                    'team_status': 'Accept',
                                    'team_leader': True,
                                    'aspirant_id': team_id.id,
                                    'new_team_id': team_id.id
                                })
                                leader_admin = request.env['snr.aspirant.team.member'].sudo().search(
                                    [('related_user_id', '=', user.id)])
                                if len(leader_admin) > 1:
                                    for leader_admin in leader_admin:
                                        leader_admin.related_user_id.write({
                                            'team_leader': True,
                                            'team_admin': True,
                                        })
                        elif request.env['snr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Leader'),
                                 ('aspirant_member_requested', '=', True)]):
                            request.env['snr.aspirant.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_id': user.id,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })

                        if each['user_type'] == 'Mentor':
                            team_id.mentor_id = mentor.id
                            mentor.sudo().write({
                                'team_ids': [(4, team_id.id)],
                                'team_status': 'Pending',
                                'new_team_id': team_id.id,
                            })
                        if each['user_type'] == 'Brand Ambassador':
                            team_id.brand_amb_id = brand_ambassador.id
                            brand_ambassador.sudo().write({
                                'team_status': 'Pending',
                                'new_team_id': team_id.id,
                                'team_ids': [(4, team_id.id)],
                            })

                aspirant_id.write({
                    'aspirant_id': team_id.id
                })
            else:
                return {'team_error': True}
        if post.get('aspirant_team'):
            aspirant_id = request.env['cfo.snr.aspirants'].sudo().search([('id', '=', int(post.get('aspirant_id')))])
            team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', int(post.get('aspirant_team')))], limit=1)
            member = request.env['snr.aspirant.team.member'].sudo().search([('team_id', '=', team_id.id)])
            #             team_id_mentor = request.env['cfo.team.snr'].sudo().search([('id', '=', int(post.get('')))], limit=1)
            for each in member:
                each.unlink()
            team_id.sudo().write({
                'name': post.get('name'),
                'ref_name': post.get('sys_name'),
                'team_type': 'CFO Aspirant',
                'aspirant_admin_id': aspirant_id.id,
                'cfo_competition_year': aspirant_id.cfo_competition_year,
                'cfo_comp': 'CFO SNR'
            })
            if post.get('member_request_list'):
                '''
                Send email for Join Our Team.
                '''
                for each_request in post.get('member_request_list'):
                    if each_request.get('user_type') == 'Mentor' or each_request.get('user_type') == 'Brand Ambassador':
                        mentor_id = request.env['mentors.snr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        amb_id = request.env['brand.ambassador.snr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        if mentor_id:
                            template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor_snr',
                                                              raise_if_not_found=False)
                            if template_mentor:
                                template_mentor.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(mentor_id.id, force_send=True)
                        if amb_id:
                            template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb_snr',
                                                           raise_if_not_found=False)

                            if template_amb:
                                template_amb.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(amb_id.id, force_send=True)

                    # if each_request.get('user_type') == 'Brand Ambassador':
                    #     amb_id = request.env['brand.ambassador.snr'].sudo().search(
                    #         [('user_id', '=', int(each_request.get('user_id')))])
                    #     template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb',
                    #                                    raise_if_not_found=False)
                    #
                    #     if template_amb:
                    #         template_amb.sudo().with_context(
                    #             user_type=each_request.get('user_type'),
                    #             team_id=team_id.id,
                    #             team_name=team_id.ref_name,
                    #             email_to=each_request.get('email')
                    #         ).send_mail(amb_id.id, force_send=True)

                    if each_request.get('user_type') in ['Leader', 'Member']:
                        res = request.env['cfo.snr.aspirants'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        aspirant_team_member_id = request.env['snr.aspirant.team.member'].sudo().search(
                            [('related_user_id', '=', res.id), ('member_status', '=', 'Accept')])
                        res.sudo().write({
                            'is_request': True,
                            'new_team_id': team_id.id
                        })

                        template = request.env.ref('cfo_snr_jnr.email_template_request_for_join_snr',
                                                   raise_if_not_found=False)
                        if template:
                            template.sudo().with_context(
                                user_type=each_request.get('user_type'),
                                team_id=team_id.id,
                                team_name=team_id.ref_name,
                                # email_to=each_request.get('email'),
                                email_cc='thecfo@charterquest.co.za',
                            ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(res.id, force_send=True)

                        aspirant_team_member_id.write({'aspirant_member_requested': True})

            for each in post.get('list_of_member'):
                member_ids = request.env['snr.aspirant.team.member'].sudo().search(
                    [('team_id', '=', team_id.id), ('user_type', '=', 'Member')])
                user = request.env['cfo.snr.aspirants'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                mentor = request.env['mentors.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                brand_ambassador = request.env['brand.ambassador.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                if not user and not mentor and not brand_ambassador and not member_ids:
                    return {'error': 'error'}
                else:
                    if len(member_ids) <= 3:
                        if each['user_type'] == 'Member':
                            if not request.env['snr.aspirant.team.member'].sudo().search(
                                    [('related_user_id', '=', user.id), ('user_type', '=', 'Member')]):
                                request.env['snr.aspirant.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_id': user.id,
                                    'team_member': True,
                                    'user_type': each['user_type'],
                                    'member_status': 'Accept'
                                })
                                user.sudo().write({
                                    'team_status': 'Accept',
                                    'new_team_id': team_id.id,
                                    'aspirant_id': team_id.id,
                                    'team_member': True,
                                    'team_admin': False,
                                })
                            elif request.env['snr.aspirant.team.member'].sudo().search(
                                    [('related_user_id', '=', user.id), ('user_type', '=', 'Member'),
                                     ('aspirant_member_requested', '=', True)]):
                                request.env['snr.aspirant.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_id': user.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                    else:
                        return {'member_limit_error': True}
                    if each['user_type'] == 'Admin':
                        team_id.aspirant_admin_id = user.id
                        if not request.env['snr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Admin')]):
                            request.env['snr.aspirant.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_id': user.id,
                                'team_admin': True,
                                'user_type': each['user_type'],
                                'member_status': 'Accept'
                            })
                            user.sudo().write({
                                'team_status': 'Accept',
                                'new_team_id': team_id.id,
                                'aspirant_id': team_id.id,
                            })
                    if each['user_type'] == 'Leader':
                        team_id.aspirant_leader_id = user.id
                        team_leader_1 = request.env['snr.aspirant.team.member'].sudo().search(
                            [('related_user_id', '=', user.id), ('user_type', '=', 'Leader')])
                        if not request.env['snr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Leader')]):
                            request.env['snr.aspirant.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_id': user.id,
                                'team_leader': True,
                                'user_type': each['user_type'],
                                'member_status': 'Accept'
                            })
                            user.sudo().write({
                                'team_status': 'Accept',
                                'new_team_id': team_id.id,
                                'aspirant_id': team_id.id,
                                'team_leader': True,
                                'team_admin': False,
                            })
                            leader_admin = request.env['snr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', user.id)])
                            if len(leader_admin) > 1:
                                for leader_admin in leader_admin:
                                    leader_admin.related_user_id.write({
                                        'team_leader': True,
                                        'team_admin': True,
                                    })
                        if request.env['snr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Leader'),
                                 ('aspirant_member_requested', '=', True)]):
                            request.env['snr.aspirant.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_id': user.id,
                                'team_leader': True,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })
                    if each['user_type'] == 'Mentor':
                        teamslt = []
                        team_id.mentor_id = mentor.id
                        mentor.sudo().write({
                            'team_ids': [(4, team_id.id)],
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                        })
                    if each['user_type'] == 'Brand Ambassador':
                        team_id.brand_amb_id = brand_ambassador.id
                        brand_ambassador.sudo().write({
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                            'aspirant_id': team_id.id,
                            'team_ids': [(4, team_id.id)],
                        })
        request.env['snr.aspirant.team.member'].sudo().search(
            [('team_id', '=', False), ('related_user_id', '=', False)]).unlink()
        return {'success': 'success '}

    @http.route('/cfo_snr_report_form', type='http', auth='public', website=True)
    def cfo_snr_report_form_new(self, **post):
        print("\n\n\n\n\n\===============cfo snr reports====",post)
        team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', post.get('aspirant_team'))])
        template = request.env.ref('cfo_snr_jnr.email_template_for_success_report_snr', raise_if_not_found=False)
        template_mentor = request.env.ref('cfo_snr_jnr.email_template_for_success_report_mentor_snr',
                                          raise_if_not_found=False)
        template_amb = request.env.ref('cfo_snr_jnr.email_template_for_success_report_ambassador_snr',
                                       raise_if_not_found=False)

        if team_id and team_id.mentor_id and template_mentor:
            template_mentor.sudo().with_context(
                team_name=team_id.ref_name,
                # email_to=team_id.mentor_id.email_1
            ).send_mail(team_id.mentor_id.id, force_send=True)

        if team_id and team_id.brand_amb_id and template_amb:
            template_amb.sudo().with_context(
                team_name=team_id.ref_name,
                # email_to=team_id.brand_amb_id.email_1
            ).send_mail(team_id.brand_amb_id.id, force_send=True)

        for aspirant_member in team_id.aspirant_team_member_ids:
            if template:
                template.sudo().with_context(
                    team_name=team_id.name,
                    # email_to=aspirant_member.related_user_id.email_1
                ).send_mail(aspirant_member.related_user_id.id, force_send=True)

            team_id.acknowledge_cfo_report = True
            team_id.cfo_report_submission_date = datetime.datetime.now()

        for academic_member in team_id.academic_team_member_ids:
            template = request.env.ref('cfo_snr_jnr.email_template_for_success_report', raise_if_not_found=False)
            template_acadamic = request.env.ref('cfo_snr_jnr.email_template_for_success_report_acadamic',
                                                raise_if_not_found=False)

            if template_acadamic and academic_member.related_user_id:
                template_acadamic.sudo().with_context(
                    team_name=team_id.name,
                    # email_to=academic_member.related_user_id.email_1
                ).send_mail(academic_member.related_user_id.id, force_send=True)
            if template and academic_member.related_user_aspirant_id:
                template.sudo().with_context(
                    team_name=team_id.name,
                    # email_to=academic_member.related_user_aspirant_id.email_1
                ).send_mail(academic_member.related_user_aspirant_id.id, force_send=True)

        for employer_member in team_id.employer_team_member_ids:
            template = request.env.ref('cfo_snr_jnr.email_template_for_success_report', raise_if_not_found=False)
            template_employer = request.env.ref('cfo_snr_jnr.email_template_for_success_report_employer',
                                                raise_if_not_found=False)

            if template_employer and employer_member.related_user_id:
                template_employer.sudo().with_context(
                    team_name=team_id.name,
                    # email_to=employer_member.related_user_id.email_1
                ).send_mail(employer_member.related_user_id.id, force_send=True)
            if template and employer_member.related_user_aspirant_id:
                template.sudo().with_context(
                    team_name=team_id.name,
                    # email_to=employer_member.related_user_aspirant_id.email_1
                ).send_mail(employer_member.related_user_aspirant_id.id, force_send=True)

            team_id.acknowledge_cfo_report = True
            team_id.cfo_report_submission_date = datetime.datetime.now()

        if (post.get('pdf') or post.get('doc')):
            if post.get('pdf'):
                filename = post.get('pdf').filename
                file = post.get('pdf')
                attach_id = request.env['ir.attachment'].sudo().create({
                    'snr_team_id': team_id.id,
                    'name': filename,
                    'type': 'binary',
                    'res_id':1,
                    'datas_fname': filename,
                    'datas': base64.b64encode(file.read()),
                    'member_status': 'Pending',
                })
            if post.get('doc'):
                filename = post.get('doc').filename
                file = post.get('doc')
                attach_id = request.env['ir.attachment'].sudo().create({
                    'snr_team_id': team_id.id,
                    'name': filename,
                    'type': 'binary',
                    'res_id': 2,
                    'datas_fname': filename,
                    'datas': base64.b64encode(file.read()),
                    'member_status': 'Pending',
                })
        if (post.get('team_pdf') or post.get('team_doc')):
            if post.get('team_pdf'):
                filename = post.get('team_pdf').filename
                file = post.get('team_pdf')
                attach_id = request.env['ir.attachment'].sudo().create({
                    'snr_team_id': team_id.id,
                    'name': filename,
                    'type': 'binary',
                    'res_id': 3,
                    'datas_fname': filename,
                    'datas': base64.b64encode(file.read()),
                    'member_status': 'Pending',
                })
            if post.get('team_doc'):
                filename = post.get('team_doc').filename
                file = post.get('team_doc')
                print("\n\n\n\n======filename===file===",filename,file)
                attach_id = request.env['ir.attachment'].sudo().create({
                    'snr_team_id': team_id.id,
                    'name': filename,
                    'type': 'binary',
                    'res_id': 4,
                    'datas_fname': filename,
                    'datas': base64.b64encode(file.read()),
                    'member_status': 'Pending',
                })
        if post.get('team_png'):
            if 'team_png' in request.params:
                attached_files = request.httprequest.files.getlist('team_png')
                print("\n\n\n\n==========attached_files==",attached_files)
                i=0
                for attachment in attached_files:
                    print("\n\n\n\n==========attachment==", attachment)
                    # attached_file = attachment.read()
                    attach_id = request.env['ir.attachment'].sudo().create({
                            'snr_team_id': team_id.id,
                            'name': attachment.filename,
                            'type': 'binary',
                            'res_id': 5 + i,
                            'datas_fname': attachment.filename,
                            'datas': base64.b64encode(attachment.read()),
                            'member_status': 'Pending',
                        })
                    i=i+1

        return request.render('cfo_snr_jnr.report_submit_success')
        # if (post.get('pdf_db') or post.get('doc_db')):
        #     return request.render('cfo_snr_jnr.report_submit_success')

    @http.route('/create_acadamic_team', type='json', auth='public', website=True)
    def create_acadamic_team(self, **post):
        if post.get('snr_academic_institution') and not post.get('acadamic_team'):
            acadamic_id = request.env['academic.institution.snr'].sudo().search(
                [('id', '=', int(post.get('snr_academic_institution')))],
                limit=1)
            print("\n\n\n=======acadamic id=====",acadamic_id)
            team_id = request.env['cfo.team.snr'].sudo().create({
                'name': post.get('name'),
                'ref_name': post.get('sys_name'),
                'team_type': 'Academic Institution',
                'cfo_competition_year': acadamic_id.cfo_competition_year,
                'academic_admin_id': acadamic_id.id,
                'cfo_comp': 'CFO SNR'
            })
            if post.get('acadamic_member_list'):
                '''
                Send email for Join Our Team.
                '''

                for each_request in post.get('acadamic_member_list'):
                    if each_request.get('user_type') == 'Mentor' or each_request.get('user_type') == 'Brand Ambassador':
                        mentor_id = request.env['mentors.snr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        amb_id = request.env['brand.ambassador.snr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        if mentor_id:
                            template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor_snr',
                                                              raise_if_not_found=False)
                            if template_mentor:
                                template_mentor.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(mentor_id.id, force_send=True)
                        if amb_id:
                            template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb_snr',
                                                           raise_if_not_found=False)
                            if template_amb:
                                template_amb.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(amb_id.id, force_send=True)

                    if each_request.get('user_type') in ['Leader', 'Member']:
                        res = request.env['cfo.snr.aspirants'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        print("\n\n\n=========member=====",res)
                        team_member_id = request.env['snr.academic.team.member'].sudo().search(
                            [('related_user_aspirant_id', '=', res.id), ('member_status', '=', 'Accept'), ])
                        res.sudo().write({
                            'is_request': True,
                            'new_team_id': team_id.id
                        })
                        template = request.env.ref('cfo_snr_jnr.email_template_request_for_join_snr',
                                                   raise_if_not_found=False)
                        if template:
                            template.sudo().with_context(
                                user_type=each_request.get('user_type'),
                                team_id=team_id.id,
                                team_name=team_id.ref_name,
                                # email_to=each_request.get('email'),
                                email_cc='thecfo@charterquest.co.za',
                            ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(res.id, force_send=True)
                        team_member_id.write({'member_requested': True})
            team_id._compute_remaining_time_deadline()
            for each in post.get('list_of_member'):
                member_ids = request.env['snr.academic.team.member'].sudo().search(
                    [('team_id', '=', team_id.id), ('user_type', '=', 'Member')])
                user_aspirant = request.env['cfo.snr.aspirants'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                user = request.env['academic.institution.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                mentor = request.env['mentors.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                brand_ambassador = request.env['brand.ambassador.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                if not user and not mentor and not brand_ambassador and not member_ids and not user_aspirant:
                    return {'error': 'error'}
                else:
                    if len(member_ids) <= 3:
                        if each['user_type'] == 'Member':
                            if not request.env['snr.academic.team.member'].sudo().search(
                                    [('related_user_aspirant_id', '=', user_aspirant.id),
                                     ('user_type', '=', 'Member')]):
                                request.env['snr.academic.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id': user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                                user_aspirant.sudo().write({
                                    'team_member': True,
                                    'aspirant_id': team_id.id
                                })
                            elif request.env['snr.academic.team.member'].sudo().search(
                                    [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Member'),
                                     ('member_requested', '=', True)]):
                                request.env['snr.academic.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id': user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                    else:
                        return {'member_limit_error': True}

                    if each['user_type'] == 'Admin':
                        team_id.academic_admin_id = user.id
                        acadamic_admin_new_id = request.env['snr.academic.team.member'].sudo().search(
                            [('related_user_id', '=', user.id), ('user_type', '=', 'Admin')])
                        request.env['snr.academic.team.member'].sudo().create({
                            'team_id': team_id.id,
                            'related_user_id': user.id,
                            'user_type': each['user_type'],
                            'member_status': 'Pending'
                        })
                        user.sudo().write({
                            'team_admin': True,
                            'cfo_team_ids': [(4, team_id.id)]
                        })

                    if each['user_type'] == 'Leader':
                        team_id.aspirant_leader_id = user_aspirant.id
                        if not request.env['snr.academic.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader')]):
                            request.env['snr.academic.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Accept'
                            })
                            user_aspirant.sudo().write({
                                'team_leader': True,
                                'aspirant_id': team_id.id
                            })
                        elif request.env['snr.academic.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader'),
                                 ('member_requested', '=', True)]):
                            request.env['snr.academic.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })

                    if each['user_type'] == 'Mentor':
                        team_id.mentor_id = mentor.id
                        mentor.sudo().write({
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                            'team_ids': [(4, team_id.id)],
                        })

                    if each['user_type'] == 'Brand Ambassador':
                        team_id.brand_amb_id = brand_ambassador.id
                        brand_ambassador.sudo().write({
                            'new_team_id': team_id.id,
                            'team_ids': [(4, team_id.id)],
                        })
                acadamic_id.write({'cfo_team_ids': [(4, team_id.id)]
                                   })
        if post.get('acadamic_team'):
            acadamic_id = request.env['academic.institution.snr'].sudo().search(
                [('id', '=', int(post.get('snr_academic_institution')))])
            team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', int(post.get('acadamic_team')))], limit=1)
            member = request.env['snr.academic.team.member'].sudo().search([('team_id', '=', team_id.id)])
            for each in member:
                each.unlink()
            team_id.sudo().write({
                'name': post.get('name'),
                'ref_name': post.get('sys_name'),
                'team_type': 'Academic Institution',
                'academic_admin_id': acadamic_id.id,
                'cfo_competition_year': acadamic_id.cfo_competition_year,
                'cfo_comp': 'CFO SNR'
            })
            if post.get('acadamic_member_list'):
                '''
                Send email for Join Our Team.
                '''
                for each_request in post.get('acadamic_member_list'):
                    if each_request.get('user_type') == 'Mentor' or each_request.get('user_type') == 'Brand Ambassador':
                        mentor_id = request.env['mentors.snr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        amb_id = request.env['brand.ambassador.snr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        if mentor_id:
                            template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor_snr',
                                                              raise_if_not_found=False)
                            if template_mentor:
                                template_mentor.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc = 'thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(mentor_id.id, force_send=True)
                        if amb_id:
                            template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb_snr',
                                                           raise_if_not_found=False)

                            if template_amb:
                                template_amb.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(amb_id.id, force_send=True)
                    if each_request.get('user_type') in ['Leader', 'Member']:
                        res = request.env['cfo.snr.aspirants'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        team_member_id = request.env['snr.academic.team.member'].sudo().search(
                            [('related_user_aspirant_id', '=', res.id), ('member_status', '=', 'Accept'), ])
                        res.sudo().write({
                            'is_request': True,
                            'new_team_id': team_id.id
                        })
                        template = request.env.ref('cfo_snr_jnr.email_template_request_for_join_snr',
                                                   raise_if_not_found=False)
                        if template:
                            template.sudo().with_context(
                                user_type=each_request.get('user_type'),
                                team_id=team_id.id,
                                team_name=team_id.ref_name,
                                # email_to=each_request.get('email'),
                                email_cc='thecfo@charterquest.co.za',
                            ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(res.id, force_send=True)
                        team_member_id.write({'member_requested': True})

            for each in post.get('list_of_member'):
                member_ids = request.env['snr.academic.team.member'].sudo().search(
                    [('team_id', '=', team_id.id), ('user_type', '=', 'Member')])
                user = request.env['academic.institution.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                user_aspirant = request.env['cfo.snr.aspirants'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                mentor = request.env['mentors.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                brand_ambassador = request.env['brand.ambassador.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                if not user and not mentor and not brand_ambassador and not member_ids and not user_aspirant:
                    return {'error': 'error'}
                else:
                    if len(member_ids) <= 3:
                        if each['user_type'] == 'Member':
                            if not request.env['snr.academic.team.member'].sudo().search(
                                    [('related_user_aspirant_id', '=', user_aspirant.id)]):
                                request.env['snr.academic.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id': user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                                user_aspirant.sudo().write({
                                    'aspirant_id': team_id.id,
                                    'team_member': True,
                                })
                            elif request.env['snr.academic.team.member'].sudo().search(
                                    [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Member'),
                                     ('member_requested', '=', True)]):
                                member = request.env['snr.academic.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id': user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                    else:
                        return {'member_limit_error': True}
                    if each['user_type'] == 'Admin':
                        team_id.academic_admin_id = user.id
                        acadamic_new_admin_id = request.env['snr.academic.team.member'].sudo().search(
                            [('related_user_id', '=', user.id), ('user_type', '=', 'Admin')])
                        request.env['snr.academic.team.member'].sudo().create({
                            'team_id': team_id.id,
                            'related_user_id': user.id,
                            'user_type': each['user_type'],
                            'member_status': 'Pending'
                        })
                        user.sudo().write({
                            'team_status': 'Accept',
                            'cfo_team_ids': [(4, team_id.id)],
                            'team_admin': True,
                        })
                    if each['user_type'] == 'Leader':
                        team_id.aspirant_leader_id = user_aspirant.id
                        if not request.env['snr.academic.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader'), ]):
                            request.env['snr.academic.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Accept'
                            })
                            user_aspirant.sudo().write({
                                'aspirant_id': team_id.id,
                                'team_leader': True,
                                'team_admin': False,
                            })
                        elif request.env['snr.academic.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader'),
                                 ('member_requested', '=', True)]):
                            request.env['snr.academic.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })

                    if each['user_type'] == 'Mentor':
                        team_id.mentor_id = mentor.id
                        mentor.sudo().write({
                            'team_ids': [(4, team_id.id)],
                            'team_status': 'Pending',
                            'new_team_id': team_id.id
                        })
                    if each['user_type'] == 'Brand Ambassador':
                        team_id.brand_amb_id = brand_ambassador.id
                        brand_ambassador.sudo().write({
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                            'team_ids': [(4, team_id.id)],
                        })
        request.env['snr.academic.team.member'].sudo().search(
            [('team_id', '=', False), ('related_user_aspirant_id', '=', False)]).unlink()
        return {'success': 'success '}

    @http.route('/create_employers_team', type='json', auth='public', website=True)
    def create_employers_team(self, **post):
        if post.get('snr_employers') and not post.get('employer_team'):
            employer_id = request.env['employers.snr'].sudo().search(
                [('id', '=', int(post.get('snr_employers')))],
                limit=1)

            team_id = request.env['cfo.team.snr'].sudo().create({
                'name': post.get('name'),
                'ref_name': post.get('sys_name'),
                'team_type': 'Employer',
                'cfo_competition_year': employer_id.cfo_competition_year,
                'employer_admin_id': employer_id.id,
                'cfo_comp': 'CFO SNR'
            })
            if post.get('employer_member_list'):
                '''
                Send email for Join Our Team.
                '''
                for each_request in post.get('employer_member_list'):
                    if each_request.get('user_type') == 'Mentor' or each_request.get('user_type') == 'Brand Ambassador':
                        mentor_id = request.env['mentors.snr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        amb_id = request.env['brand.ambassador.snr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        if mentor_id:
                            template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor_snr',
                                                              raise_if_not_found=False)
                            if template_mentor:
                                template_mentor.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(mentor_id.id, force_send=True)
                        if amb_id:
                            template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb_snr',
                                                           raise_if_not_found=False)
                            if template_amb:
                                template_amb.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(amb_id.id, force_send=True)
                    if each_request.get('user_type') in ['Leader', 'Member']:
                        res = request.env['cfo.snr.aspirants'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        team_member_id = request.env['snr.employer.team.member'].sudo().search(
                            [('related_user_aspirant_id', '=', res.id), ('member_status', '=', 'Accept'), ])
                        res.sudo().write({
                            'is_request': True,
                            'new_team_id': team_id.id
                        })
                        template = request.env.ref('cfo_snr_jnr.email_template_request_for_join_snr',
                                                   raise_if_not_found=False)
                        if template:
                            template.sudo().with_context(
                                user_type=each_request.get('user_type'),
                                team_id=team_id.id,
                                team_name=team_id.ref_name,
                                # email_to=each_request.get('email'),
                                email_cc='thecfo@charterquest.co.za',
                            ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(res.id, force_send=True)
                        team_member_id.write({'member_requested': True})
            team_id._compute_remaining_time_deadline()
            for each in post.get('list_of_member'):
                member_ids = request.env['snr.employer.team.member'].sudo().search(
                    [('team_id', '=', team_id.id), ('user_type', '=', 'Member')])
                user_aspirant = request.env['cfo.snr.aspirants'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                user = request.env['employers.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                mentor = request.env['mentors.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                brand_ambassador = request.env['brand.ambassador.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                if not user and not mentor and not brand_ambassador and not member_ids and not user_aspirant:
                    return {'error': 'error'}
                else:
                    if len(member_ids) <= 3:
                        if each['user_type'] == 'Member':
                            if not request.env['snr.employer.team.member'].sudo().search(
                                    [('related_user_aspirant_id', '=', user_aspirant.id),
                                     ('user_type', '=', 'Member')]):
                                request.env['snr.employer.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id': user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                                user_aspirant.sudo().write({
                                    'team_member': True,
                                    'aspirant_id': team_id.id
                                })
                            if request.env['snr.academic.team.member'].sudo().search(
                                    [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Member'),
                                     ('member_requested', '=', True)]):
                                request.env['snr.academic.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id': user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                    else:
                        return {'member_limit_error': True}

                    if each['user_type'] == 'Admin':
                        team_id.employer_admin_id = user.id
                        request.env['snr.employer.team.member'].sudo().create({
                            'team_id': team_id.id,
                            'related_user_id': user.id,
                            'user_type': each['user_type'],
                            'member_status': 'Pending'
                        })
                        user.sudo().write({
                            'team_admin': True,
                            'cfo_team_ids': [(4, team_id.id)]
                        })

                    if each['user_type'] == 'Leader':
                        if not request.env['snr.employer.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader')]):
                            request.env['snr.employer.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Accept'
                            })
                            user_aspirant.sudo().write({
                                'team_leader': True,
                                'aspirant_id': team_id.id
                            })
                        if request.env['snr.employer.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader'),
                                 ('member_requested', '=', True)]):
                            request.env['snr.academic.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })

                    if each['user_type'] == 'Mentor':
                        team_id.mentor_id = mentor.id
                        mentor.sudo().write({
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                            'team_ids': [(4, team_id.id)],
                        })

                    if each['user_type'] == 'Brand Ambassador':
                        team_id.brand_amb_id = brand_ambassador.id
                        brand_ambassador.sudo().write({
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                            'team_ids': [(4, team_id.id)],
                        })
                employer_id.write({'cfo_team_ids': [(4, team_id.id)]
                                   })
        # else:
        #     return {'team_error': True}
        if post.get('employer_team'):
            employer_id = request.env['employers.snr'].sudo().search(
                [('id', '=', int(post.get('snr_employers')))])
            team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', int(post.get('employer_team')))], limit=1)
            member = request.env['snr.employer.team.member'].sudo().search([('team_id', '=', team_id.id)])
            for each in member:
                each.unlink()
            team_id.sudo().write({
                'name': post.get('name'),
                'ref_name': post.get('sys_name'),
                'team_type': 'Employer',
                'employer_admin_id': employer_id.id,
                'cfo_competition_year': employer_id.cfo_competition_year,
                'cfo_comp': 'CFO SNR'
            })
            if post.get('employer_member_list'):
                '''
                Send email for Join Our Team.
                '''
                for each_request in post.get('employer_member_list'):
                    if each_request.get('user_type') == 'Mentor' or each_request.get('user_type') == 'Brand Ambassador':
                        mentor_id = request.env['mentors.snr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        amb_id = request.env['brand.ambassador.snr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        if mentor_id:
                            template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor_snr',
                                                              raise_if_not_found=False)
                            if template_mentor:
                                template_mentor.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(mentor_id.id, force_send=True)
                        if amb_id:
                            template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb_snr',
                                                           raise_if_not_found=False)

                            if template_amb:
                                template_amb.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(amb_id.id, force_send=True)

                    if each_request.get('user_type') in ['Leader', 'Member']:
                        res = request.env['cfo.snr.aspirants'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        team_member_id = request.env['snr.employer.team.member'].sudo().search(
                            [('related_user_aspirant_id', '=', res.id), ('member_status', '=', 'Accept'), ])
                        res.sudo().write({
                            'is_request': True,
                            'new_team_id': team_id.id
                        })
                        template = request.env.ref('cfo_snr_jnr.email_template_request_for_join_snr',
                                                   raise_if_not_found=False)
                        if template:
                            template.sudo().with_context(
                                user_type=each_request.get('user_type'),
                                team_id=team_id.id,
                                team_name=team_id.ref_name,
                                # email_to=each_request.get('email'),
                                email_cc='thecfo@charterquest.co.za',
                            ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(res.id, force_send=True)
                        team_member_id.write({'member_requested': True})

            for each in post.get('list_of_member'):
                member_ids = request.env['snr.employer.team.member'].sudo().search(
                    [('team_id', '=', team_id.id), ('user_type', '=', 'Member')])
                user = request.env['employers.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                user_aspirant = request.env['cfo.snr.aspirants'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                mentor = request.env['mentors.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                brand_ambassador = request.env['brand.ambassador.snr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                if not user and not mentor and not brand_ambassador and not member_ids and not user_aspirant:
                    return {'error': 'error'}
                else:
                    if len(member_ids) <= 3:
                        if each['user_type'] == 'Member':
                            if not request.env['snr.employer.team.member'].sudo().search(
                                    [('related_user_aspirant_id', '=', user_aspirant.id)]):
                                request.env['snr.employer.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id': user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                                user_aspirant.sudo().write({
                                    'aspirant_id': team_id.id,
                                    'team_member': True,
                                })
                        if request.env['snr.employer.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Member'),
                                 ('member_requested', '=', True)]):
                            request.env['snr.employer.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })
                    else:
                        return {'member_limit_error': True}
                    if each['user_type'] == 'Admin':
                        team_id.employer_admin_id = user.id
                        request.env['snr.employer.team.member'].sudo().create({
                            'team_id': team_id.id,
                            'related_user_id': user.id,
                            'user_type': each['user_type'],
                            'member_status': 'Pending'
                        })
                        user.sudo().write({
                            'cfo_team_ids': [(4, team_id.id)],
                            'team_admin': True,
                        })
                    if each['user_type'] == 'Leader':
                        team_id.aspirant_leader_id = user_aspirant.id
                        if not request.env['snr.employer.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader'), ]):
                            request.env['snr.employer.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Accept'
                            })
                            user_aspirant.sudo().write({
                                'aspirant_id': team_id.id,
                                'team_leader': True,
                                'team_admin': False,
                            })
                        if request.env['snr.employer.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader'),
                                 ('member_requested', '=', True)]):
                            request.env['snr.employer.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })

                    if each['user_type'] == 'Mentor':
                        team_id.mentor_id = mentor.id
                        mentor.sudo().write({
                            'team_ids': [(4, team_id.id)],
                            'team_status': 'Pending',
                            'new_team_id': team_id.id
                        })
                    if each['user_type'] == 'Brand Ambassador':
                        team_id.brand_amb_id = brand_ambassador.id
                        brand_ambassador.sudo().write({
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                            'team_ids': [(4, team_id.id)],
                        })
        request.env['snr.employer.team.member'].sudo().search(
            [('team_id', '=', False), ('related_user_aspirant_id', '=', False)]).unlink()
        return {'success': 'success '}

    @http.route('/submit_cfo_report_data', type="json", auth="public", website=True)
    def submit_cfo_report_data(self, **post):
        print("\n\n\n\n\=====post for submit report==========",post)
        aspirant_id = request.env['cfo.snr.aspirants'].sudo().search([('id', '=', post.get('aspirant_id'))])
        team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', post.get('team_id'))])
        list_without_bio_member = []
        for team_id in team_id:
            for team_member in team_id.aspirant_team_member_ids:
                if not team_member.related_user_id.updated_cfo_bio:
                    list_without_bio_member.append(
                        {'member_name': team_member.related_user_id.name, 'member_type': team_member.user_type})
            for team_member in team_id.academic_team_member_ids:
                if team_member.related_user_aspirant_id and not team_member.related_user_aspirant_id.updated_cfo_bio:
                    list_without_bio_member.append({'member_name': team_member.related_user_aspirant_id.partner_id.name,
                                                    'member_type': team_member.user_type})
            for team_member in team_id.employer_team_member_ids:
                if team_member.related_user_aspirant_id and not team_member.related_user_aspirant_id.updated_cfo_bio:
                    list_without_bio_member.append({'member_name': team_member.related_user_aspirant_id.partner_id.name,
                                                    'member_type': team_member.user_type})
            if team_id.mentor_id and not team_id.mentor_id.updated_mentors_bio:
                list_without_bio_member.append(
                    {'member_name': team_id.mentor_id.partner_id.name, 'member_type': 'Mentor'})
            if team_id.brand_amb_id and not team_id.brand_amb_id.updated_brand_amb_bio:
                list_without_bio_member.append(
                    {'member_name': team_id.brand_amb_id.partner_id.name, 'member_type': 'Brand Ambassador'})
            if list_without_bio_member:
                return {'bio_not_upadate': True, 'list_without_bio_member': list_without_bio_member}
            else:
                return {'snr_aspirants': aspirant_id, 'aspirant_team': team_id}

    @http.route('/cfo_snr_report', type="http", auth="public", website=True)
    def cfo_snr_report(self, **post):
        if post.get('aspirant_id') and post.get('team_id'):
            aspirant_id = request.env['cfo.snr.aspirants'].sudo().search([('id', '=', post.get('aspirant_id'))])
            team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', post.get('team_id'))])
            return request.render('cfo_snr_jnr.cfo_snr_report_new',
                                  {'snr_aspirants': aspirant_id, 'aspirant_team': team_id})

    @http.route('/remove_member', type='json', auth="public", website=True)
    def remove_member(self, **post):
        team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', post.get('team_id'))])
        if post.get('member_type') == 'Brand Ambassador':
            amb_delete = team_id.write({'brand_amb_id': ''})
        if post.get('member_type') == 'Mentor':
            mnt_delete = team_id.write({'mentor_id': ''})
        if post.get('member_id'):
            member = request.env['snr.aspirant.team.member'].sudo().search([('id', '=', int(post.get('member_id')))])
            if member.user_type == 'Leader':
                member.related_user_id.write({'team_leader': False})
                member.unlink()
            if member and member.user_type != 'Leader':
                member.related_user_id.aspirant_id = False
                member.unlink()
        return True

    @http.route('/remove_member_acadamic', type='json', auth="public", website=True)
    def remove_member_acadamic(self, **post):
        team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', post.get('team_id'))])
        if post.get('member_type') == 'Brand Ambassador':
            amb_delete = team_id.write({'brand_amb_id': ''})
        if post.get('member_type') == 'Mentor':
            mnt_delete = team_id.write({'mentor_id': ''})
        if post.get('member_id'):
            member = request.env['snr.academic.team.member'].sudo().search([('id', '=', int(post.get('member_id')))])
            if member.user_type == 'Leader':
                member.related_user_id.write({'team_leader': False})
            if member:
                member.related_user_id.aspirant_id = False
                member.unlink()
        return True

    @http.route('/remove_member_from_team', type="json", auth='public', website=True)
    def remove_member_from_team(self, **post):
        if post.get('aspirant_team'):
            is_delete = ''
            team_id = request.env['cfo.team.snr'].sudo().search([('id', '=', post.get('aspirant_team'))])
            if post.get('member_type') == 'Brand Ambassador':
                is_delete = team_id.write({'brand_amb_id': ''})
            if post.get('member_type') == 'Mentor':
                is_delete = team_id.write({'mentor_id': ''})
            if is_delete:
                return {'removed': True}

class CfoAuthSignup(auth_signup.AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'cfo_signup')}
        print("\n\n\n\n\n\n\n\n===============values===========11=",values)
        member_values = {key: qcontext.get(key) for key in (
            'login', 'name', 'password', 'lastname', 'cfo_competition', 'cfo_membertype', 'cfo_source',
            'other',
            'cfo_signup')}
        print("\n\n\n\n\n\n\n\n===============member_values===========11=", member_values)
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords are not the same, please try again"))

        supported_langs = [lang['code'] for lang in
                           request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        if member_values.get('lastname'):
            values.update({'name': member_values.get('name') + ' ' + member_values.get('lastname')})
        print("\n\n\n\n\n\n\n===========supported_langs=====1==", supported_langs)
        user_val = self._signup_with_values(qcontext.get('token'), values, member_values)
        request.env.cr.commit()
        print("\n\n\n\n\n\n\n===========user_val=====1==", user_val)
        return user_val;

    def _signup_with_values(self, token, values, values1=''):
        print("\n\n\n\n\n\n\n======token, valuesd===========",token,values)
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        print("\n\n\n\n\n\n\n=======db, login, password===========", db, login, password)
        request.env.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(db, login, password)
        user = request.env['res.users'].sudo().browse(uid)
        user.sudo().write({'share': True})
        print("\n\n\n\n\n\n\n=======values===========", values)
        if values.get('cfo_signup'):
            user.partner_id.sudo().write({
                'cfo_user': True
            })
            http.request.session['cfo_login'] = True
        #         member_values = {}
        #         if values1.get('lastname'):
        #             member_values.update({'name': values1.get('name') + ' ' + values1.pop('lastname')})
        #             if values1.get('cfo_competition'):
        #                 member_values.update({'cfo_comp': int(values1.pop('cfo_competition'))})
        #             member_values.update({'cfo_member_type': values1.pop('cfo_membertype')})
        #             if values1.get('cfo_source'):
        #                 member_values.update({'cfo_registrants_source': values1.pop('cfo_source')})
        #             if values1.get('other'):
        #                 member_values.update({'other': values1.pop('other', '')})
        #             member_values.update({'login': values1.get('login')})
        #             member_values.update({'aspirants_email': values1.get('login')})
        #             member_values.update({'password': values1.get('password')})
        #             if datetime.date.today().month in [4,5,6,7,8,9,10,11,12]:
        #                 member_values.update({'cfo_competition_year': str(datetime.date.today().year + 1)})
        #             else:
        #                 member_values.update({'cfo_competition_year': str(datetime.date.today().year)})
        if not uid:
            raise SignupError(_('Authentication Failed.'))

        return uid;
    #         if member_values:
    #             user._create_member(member_values)
    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""

        get_param = request.env['ir.config_parameter'].sudo().get_param
        return {
            'signup_enabled': get_param('auth_signup.allow_uninvited') == 'True',
            'reset_password_enabled': get_param('auth_signup.reset_password') == 'True',
        }

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = request.params.copy()
        qcontext.update(self.get_auth_signup_config())
        if not qcontext.get('token') and request.session.get('auth_signup_token'):
            qcontext['token'] = request.session.get('auth_signup_token')
        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                token_infos = request.env['res.partner'].sudo().signup_retrieve_info(qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                id = self.do_signup(qcontext)
                user = request.env['res.users'].sudo().browse([id])
                # Send an account creation confirmation email
                # if qcontext.get('token'):
                if user.partner_id['cfo_user'] == True:
                    user_sudo = request.env['res.users'].sudo().search(
                        [('login', '=', qcontext.get('login'))])
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',raise_if_not_found=False)

                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                            password=request.params.get('password')
                        ).send_mail(user_sudo.id, force_send=True)
                return super(CfoAuthSignup, self).web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
                return request.redirect('/signup?error=%s' % qcontext['error'])
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                    return request.redirect('/signup?error=%s' % qcontext['error'])
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")
                    return request.redirect('/signup?error=%s' % qcontext['error'])

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class WebsiteSaleController(WebsiteSale):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        res = super(WebsiteSaleController, self).product(product, category, search)
        categs = request.env['product.public.category'].search([('parent_id', '=', False)])

        parent_category_ids = []
        if category:
            category = request.env['product.public.category'].search([('id', '=', int(category))])
            parent_category_ids = [category.id]
            current_category = category
            while current_category.parent_id:
                parent_category_ids.append(current_category.parent_id.id)
                current_category = current_category.parent_id
        res.qcontext['parent_category_ids'] = parent_category_ids
        res.qcontext['categories'] = categs
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
