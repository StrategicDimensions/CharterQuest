# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class Http(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls):
        # add signup token or login to the session if given
        if 'auth_signup_token' in request.params:
            print("\n\n\n\n===========call1111111============")
            request.session['auth_signup_token'] = request.params['auth_signup_token']
        if 'auth_login' in request.params:
            print("\n\n\n\n===========call222222============")
            request.session['auth_login'] = request.params['auth_login']

        return super(Http, cls)._dispatch()
