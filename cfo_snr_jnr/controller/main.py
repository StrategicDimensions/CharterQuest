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
import odoo

# class cfo_senior(http.Controller):
# 
#     @http.route(['/login'], type='http', auth="public", website=True)
#     def login(self, **post):
#         return request.render('cfo_snr_jnr.cfo_login')
# 
#     @http.route(['/cfo_logout'], type='http', auth="public", website=True)
#     def cfo_logout(self, **post):
#         request.session['logged_user'] = None
#         return request.render("cfo_snr_jnr.cfo_login")
# 
#     @http.route(['/login_check'], type='json', auth="public", website=True)
#     def login_check(self, username, pswd):
#         cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
#         qry = "SELECT id from res_users where login= '"+username+"' and password='"+pswd+"';"
#         cr.execute(qry)
#         row = cr.fetchone()
#         if row and row[0]:
#             request.session['logged_user'] = row[0]
#             return row[0]
#         return False
#     
# 
#     @http.route(['/user_details'], type='http', auth="public", website=True)
#     def user_details(self, **post):
#         value = post
#         return request.render("cfo_snr_jnr.user_form",value)


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
#                 qry = "SELECT id from res_users where login= '"+request.params['login']+"' and password='"+request.params['password']+"';"
#                 cr.execute(qry)
#                 row = cr.fetchone()
#                 if not row:
#                     values['error'] = _("Your Email Address/Password is Incorrect")
#                 else:
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: