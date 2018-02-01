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

    @http.route(['/cfo_logout'], type='http', auth="public", website=True)
    def cfo_logout(self, **post):
        request.session['logged_user'] = None
        return request.render("cfo_snr_jnr.cfo_login")

    @http.route('/get_member_types', type='json', auth='public', webstie=True)
    def get_member_types(self,val):
        if val:
            list = [conf.name for conf in request.env['cfo.configuration'].search([('cfo_competitions', '=', int(val))])]
            return list

    @http.route(['/cfo_senior'], type='http', auth="public", website=True)
    def cfo_senior(self, **post):
        return request.render('cfo_snr_jnr.cfo_senior')

    @http.route(['/cfo_junior'], type='http', auth="public", website=True)
    def cfo_junior(self, **post):
        return request.render('cfo_snr_jnr.cfo_junior')

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
            qry = "SELECT id from res_users where login= '"+request.params['login']+"';"
            cr.execute(qry)
            row_username = cr.fetchone()
            if not row_username:
                values['error'] = _("Email Address Does Not Exist, Please Register")
            else:
                old_uid = request.uid
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                if uid is not False:
                    request.params['login_success'] = True
                    return http.redirect_with_hash(self._login_redirect(uid=uid, redirect=redirect))
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


class CfoAuthSignup(auth_signup.AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password') }
        member_values = { key: qcontext.get(key) for key in ('login', 'name', 'password','lastname','cfo_competition', 'cfo_membertype', 'cfo_source', 'other') }

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
        print("_signup_with_values=========")
        db, login, password = request.env['res.users'].sudo().signup(values, token)
        request.env.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        uid = request.session.authenticate(db, login, password)
        user = request.env['res.users'].sudo().browse(uid)
        user.sudo().write({'share': False})
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
                    template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
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