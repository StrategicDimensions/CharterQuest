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

from odoo import api, fields, models, _

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    team_id = fields.Many2one('cfo.teams','Team ID')
    doc_id = fields.Many2one('volunteers','Doc ID')
    mentors_doc_id = fields.Many2one('mentors','DOC ID')
    fyla_application_id_att = fields.Many2one('fyla.application',"FYLA Application")
    aspirant_doc_id = fields.Many2one('cfo.aspirants','Aspirants Docs')
    academic_doc_id = fields.Many2one('academic.institution','Academic Docs')
    employers_doc_id = fields.Many2one('employers','Employer Docs')
    social_doc_id = fields.Many2one('social.media.contestants','Social Docs')
    brand_doc_id = fields.Many2one('brand.ambassador','Social Docs')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: