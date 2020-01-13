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
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    recaptcha_site_key = fields.Char(string="Site Key")
    recaptcha_secret_key = fields.Char(string="Secret Key")

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            recaptcha_site_key=self.env['ir.config_parameter'].sudo().get_param(
                'cfo_snr_jnr.recaptcha_site_key'),
            recaptcha_secret_key=self.env['ir.config_parameter'].sudo().get_param(
                'cfo_snr_jnr.recaptcha_secret_key'),

        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param_obj = self.env['ir.config_parameter']
        param_obj.sudo().set_param('cfo_snr_jnr.recaptcha_site_key', self.recaptcha_site_key)
        param_obj.sudo().set_param('cfo_snr_jnr.recaptcha_secret_key', self.recaptcha_secret_key)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: