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
import logging

from odoo import api, fields, models, _
from odoo.addons.auth_signup.models.res_partner import SignupError, now
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'


    def reset_password(self, login):
        """ retrieve the user corresponding to login (login or email),
            and reset their password
        """
        users = self.search([('login', '=', login)])
        if not users:
            users = self.search([('email', '=', login)])
        if len(users) != 1:
            raise Exception(_('Reset Password: Email Does not exist, Please Register'))
        return users.action_reset_password()

    def reset_password(self):
        create_mode = bool(self.env.context.get('create_user'))

        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        template = False
        if create_mode:
            try:
                if self.env.context.get('user_type') in ['Leader', 'Member']:
                    res = self.env['cfo.snr.aspirants'].sudo().search([('user_id', '=', self.id)])
                    template = self.env.ref('cfo_snr_jnr.email_template_request_for_join', raise_if_not_found=False)
                if self.env.context.get('user_type') == 'Mentor':
                    res = self.env['mentors.snr'].sudo().search([('user_id', '=', self.id)])
                    template = self.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor',
                                            raise_if_not_found=False)
                if self.env.context.get('user_type') == 'Brand Ambassador':
                    res = self.env['brand.ambassador.snr'].sudo().search([('user_id', '=', self.id)])
                    template = self.env.ref('cfo_snr_jnr.email_template_request_for_join_amb', raise_if_not_found=False)
            except ValueError:
                pass

        assert template._name == 'mail.template'

        template_values = {
            'email_to': self.env.context.get('email'),
            'email_cc': 'thecfo@charterquest.co.za',
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for user in res:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            with self.env.cr.savepoint():
                template.with_context(team_name=self.env.context.get('team_name'),cfo_login=True,lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)


    @api.multi
    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        template_values = {
            'email_to': '${object.email|safe}',
            'email_cc': True,
            'auto_delete': True,
            'partner_to': False,
            'scheduled_date': False,
        }
        template.write(template_values)

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            with self.env.cr.savepoint():
                template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

    @api.model
    def signup(self, values, token=None):
        """ signup a user, to either:
            - create a new user (no token), or
            - create a user for a partner (with token, but no user for partner), or
            - change the password of a user (with token, and existing user).
            :param values: a dictionary with field values that are written on user
            :param token: signup token (optional)
            :return: (dbname, login, password) for the signed up user
        """
        if token:
            # signup with a token: find the corresponding partner id
            partner = self.env['res.partner']._signup_retrieve_partner(token, check_validity=True, raise_exception=True)
            # invalidate signup token
            partner.write({'signup_token': False, 'signup_type': False, 'signup_expiration': False})

            partner_user = partner.user_ids and partner.user_ids[0] or False

            # avoid overwriting existing (presumably correct) values with geolocation data
            if partner.country_id or partner.zip or partner.city:
                values.pop('city', None)
                values.pop('country_id', None)
            if partner.lang:
                values.pop('lang', None)

            if partner_user:
                # user exists, modify it according to values
                values.pop('login', None)
                values.pop('name', None)
                partner_user.write(values)
                return (self.env.cr.dbname, partner_user.login, values.get('password'))
            else:
                # user does not exist: sign up invited user
                values.update({
                    'name': partner.name,
                    'partner_id': partner.id,
                    'email': values.get('email') or values.get('login'),
                })
                if partner.company_id:
                    values['company_id'] = partner.company_id.id
                    values['company_ids'] = [(6, 0, [partner.company_id.id])]
                self._signup_create_user(values)
        else:
            # no token, sign up an external user
            values['email'] = values.get('email') or values.get('login')
            self._signup_create_user(values)

        return (self.env.cr.dbname, values.get('login'), values.get('password'))

    @api.model
    def _create_member(self, values):
        """ create a Charter Quest Member """
        if self.partner_id:
            values.update({'partner_id': self.partner_id.id})
        if values.get('cfo_comp'):
            configuration = self.env['cfo.competition'].browse(values.pop('cfo_comp'))
            cfo_member_type = values.pop('cfo_member_type')
            if configuration.cfo_comp == 'CFO SNR':
                if cfo_member_type == 'CFO Aspirant':
                    member = self.env['cfo.snr.aspirants'].create(values)
                elif cfo_member_type == 'Academic Institution':
                    member = self.env['academic.institution.snr'].create(values)
                elif cfo_member_type == 'Employer':
                    member = self.env['employers.snr'].create(values)
                elif cfo_member_type == 'Volunteer':
                    member = self.env['volunteers.snr'].create(values)
                elif cfo_member_type == 'Brand Ambassador':
                    member = self.env['brand.ambassador.snr'].create(values)
                elif cfo_member_type == 'Social Media Contestant':
                    member = self.env['social.media.contestants.snr'].create(values)
                elif cfo_member_type == 'Mentor':
                    member = self.env['mentors.snr'].create(values)
            elif configuration.cfo_comp == 'CFO JNR':
                if cfo_member_type == 'CFO Aspirant':
                    member = self.env['cfo.jnr.aspirants'].create(values)
                elif cfo_member_type == 'Secondary/High School':
                    member = self.env['academic.institution.jnr'].create(values)
                elif cfo_member_type == 'Brand Ambassador':
                    member = self.env['brand.ambassador.jnr'].create(values)
                elif cfo_member_type == 'Mentor':
                    member = self.env['mentors.jnr'].create(values)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: