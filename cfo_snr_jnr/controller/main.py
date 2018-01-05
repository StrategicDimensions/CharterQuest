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
import json
from odoo.addons.web.controllers import main as web
from odoo.addons.auth_signup.controllers import main as auth_signup
import odoo
from odoo.exceptions import UserError


class cfo_home(web.Home):

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

class cfo_auth_signup(auth_signup.AuthSignupHome):
    
    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords are not the same, please try again"))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: