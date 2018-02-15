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
import json
from odoo.addons.web.controllers import main as web
from odoo.addons.auth_signup.controllers import main as auth_signup
import odoo
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError
import datetime

_logger = logging.getLogger(__name__)


class CfoHome(web.Home):

    @http.route(['/login'], type='http', auth="public", website=True)
    def login(self, **post):
        return request.render('cfo_snr_jnr.cfo_login')

    @http.route(['/signup'], type='http', auth="public", website=True)
    def signup(self, **post):
        return request.render('cfo_snr_jnr.cfo_signup_form')

    @http.route(['/cfo_logout'], type='http', auth="public", website=True)
    def cfo_logout(self, **post):
        request.session['logged_user'] = None
        request.session['cfo_login'] = False
        return request.render("cfo_snr_jnr.cfo_login")

    @http.route('/get_member_types', type='json', auth='public', webstie=True)
    def get_member_types(self, val):
        if val:
            list = [conf.cfo_member_type for conf in
                    request.env['cfo.configuration'].search([('cfo_competitions', '=', int(val))])]
            return list

    @http.route(['/CFO/senior/signup'], type='http', auth="public", website=True)
    def cfo_senior_signup(self, **post):
        return request.render('cfo_snr_jnr.cfo_senior_signup')

    @http.route(['/CFO/junior/signup'], type='http', auth="public", website=True)
    def cfo_junior_signup(self, **post):
        return request.render('cfo_snr_jnr.cfo_junior_signup')

    @http.route(['/cfo_senior'], type='http', auth="public", website=True)
    def cfo_senior(self, **post):
        partner = request.env.user.partner_id
        login = request.env.user.login
        today = datetime.datetime.today()
        args = [('email_1', '=', login)]
        if today.month in [4, 5, 6, 7, 8, 9, 10, 11, 12]:
            args.append(('cfo_competition_year', '=', str(today.year + 1)))
        else:
            args.append(('cfo_competition_year', '=', str(today.year)))
        snr_aspirants = request.env['cfo.snr.aspirants'].sudo().search(args)
        snr_academic_institution = request.env['academic.institution.snr'].sudo().search(args)
        snr_employers = request.env['employers.snr'].sudo().search(args)
        snr_volunteers = request.env['volunteers.snr'].sudo().search(args)
        snr_brand_ambassador = request.env['brand.ambassador.snr'].sudo().search(args)
        snr_media_contestants = request.env['social.media.contestants.snr'].sudo().search(args)
        snr_mentors = request.env['mentors.snr'].sudo().search(args)
        values = {}
        values['country_list'] = request.env['res.country'].sudo().search([])
        values['state_list'] = request.env['res.country.state'].sudo().search([])
        if post.get('snr_aspirants'):
            values['update_bio'] = True
            values['update_bio_info'] = True
        if snr_aspirants:
            values.update({'snr_aspirants': snr_aspirants})
        if snr_academic_institution:
            values.update({'snr_academic_institution': snr_academic_institution})
        if snr_employers:
            values.update({'snr_employers': snr_employers})
        if snr_volunteers:
            values.update({'snr_volunteers': snr_volunteers})
        if snr_brand_ambassador:
            values.update({'snr_brand_ambassador': snr_brand_ambassador})
        if snr_media_contestants:
            values.update({'snr_media_contestants': snr_media_contestants})
        if snr_mentors:
            values.update({'snr_mentors': snr_mentors})
        if snr_aspirants or snr_academic_institution or snr_employers or snr_volunteers or snr_brand_ambassador:
            values.update({'senior': True})
        if request.httprequest.method == 'POST':
            if post.get('update_bio_info'):
                values['contact_info'] = True
                values['update_bio'] = True
                values['update_bio_info'] = False
                snr_aspirants.sudo().write({
                    'name': post.get('name'),
                    'surname': post.get('surname'),
                    'other_names': post.get('other_names'),
                    'date_of_birth': post.get('date_of_birth') if post.get('date_of_birth') else False,
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
                    'start_date': post.get('start_date') if post.get('start_date') else False,
                    'expected_completion_date': post.get('expected_completion_date') if post.get(
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
                    'updated_cfo_bio': True
                })
        return request.render('cfo_snr_jnr.cfo_senior', values)

    @http.route(['/cfo_junior'], type='http', auth="public", website=True)
    def cfo_junior(self, **post):
        partner = request.env.user.partner_id
        login = request.env.user.login
        today = datetime.datetime.today()
        args = [('email_1', '=', login)]
        if today.month in [4, 5, 6, 7, 8, 9, 10, 11, 12]:
            args.append(('cfo_competition_year', '=', str(today.year + 1)))
        else:
            args.append(('cfo_competition_year', '=', str(today.year)))
        jnr_aspirants = request.env['cfo.jnr.aspirants'].sudo().search(args)
        jnr_academic_institution = request.env['academic.institution.jnr'].sudo().search(args)
        #         jnr_employers = request.env['employers.jnr'].sudo().search(args)
        #         jnr_volunteers = request.env['volunteers.jnr'].sudo().search(args)
        jnr_brand_ambassador = request.env['brand.ambassador.jnr'].sudo().search(args)
        #         jnr_media_contestants = request.env['social.media.contestants.jnr'].sudo().search(args)
        jnr_mentors = request.env['mentors.jnr'].sudo().search(args)
        values = {}
        if jnr_aspirants:
            values.update({'jnr_aspirants': jnr_aspirants})
        if jnr_academic_institution:
            values.update({'jnr_academic_institution': jnr_academic_institution})
        #         if jnr_employers:
        #             values.update({'jnr_employers': jnr_employers})
        #         if jnr_volunteers:
        #             values.update({'jnr_volunteers': jnr_volunteers})
        if jnr_brand_ambassador:
            values.update({'jnr_brand_ambassador': jnr_brand_ambassador})
        #         if jnr_media_contestants:
        #             values.update({'jnr_media_contestants': jnr_media_contestants})
        if jnr_mentors:
            values.update({'jnr_mentors': jnr_mentors})
        if values:
            values.update({'junior': True})
        return request.render('cfo_snr_jnr.cfo_junior', values)

    @http.route('/web/login', type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
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
            else:
                old_uid = request.uid
                uid = request.session.authenticate(request.session.db, request.params['login'],
                                                   request.params['password'])
                if uid is not False:
                    request.params['login_success'] = True
                    if kw.get('cfo_login'):
                        request.session['cfo_login'] = True
                    return http.request.redirect('/my/home')
                request.uid = old_uid
                values['error'] = _("Your Email Address/Password is Incorrect")
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

    @http.route('/CFO/senior/register_cfo_senior', type='http', auth="public", website=True)
    def register_cfo_senior(self, **post):
        member_values = {}
        if post.get('cfo_competition') and post.get('cfo_membertype'):
            partner = request.env.user.partner_id
            user = request.env.user
            member_values.update({'name': user.name, 'partner_id': partner.id, 'user_id': user.id})
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
            user._create_member(member_values)
        return request.redirect('/cfo_senior')

    @http.route('/CFO/junior/register_cfo_junior', type='http', auth="public", website=True)
    def register_cfo_junior(self, **post):
        member_values = {}
        if post.get('cfo_competition') and post.get('cfo_membertype'):
            partner = request.env.user.partner_id
            user = request.env.user
            member_values.update({'name': user.name, 'partner_id': partner.id, 'user_id': user.id})
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


class CfoAuthSignup(auth_signup.AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'cfo_signup')}
        member_values = {key: qcontext.get(key) for key in (
            'login', 'name', 'password', 'lastname', 'cfo_competition', 'cfo_membertype', 'cfo_source', 'other',
            'cfo_signup')}

        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords are not the same, please try again"))

        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        if member_values.get('lastname'):
            values.update({'name': member_values.get('name') + ' ' + member_values.get('lastname')})

        self._signup_with_values(qcontext.get('token'), values, member_values)
        request.env.cr.commit()

    def _signup_with_values(self, token, values, values1=''):
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(db, login, password)
        user = request.env['res.users'].sudo().browse(uid)
        user.sudo().write({'share': False})
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

    #         if member_values:
    #             user._create_member(member_values)

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    user_sudo = request.env['res.users'].sudo().search([('login', '=', qcontext.get('login'))])
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                               raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({'auth_login': user_sudo.email}),
                            password=request.params.get('password')
                        ).send_mail(user_sudo.id, force_send=True)
                return super(CfoAuthSignup, self).web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
