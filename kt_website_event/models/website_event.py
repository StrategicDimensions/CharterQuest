# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class event_type(models.Model):
    _inherit = 'event.type'

    publish_on_website = fields.Boolean('Publish on Website')
    publish_on_portal = fields.Boolean('Publish on Portal')


class event_ticket(models.Model):
    _inherit = 'event.event.ticket'

    is_free = fields.Boolean('Is Free')


class Dynamic_menu(models.Model):
    _name = 'dynamic.menu'

    name = fields.Char(string="Name")
    parent_id = fields.Many2one('dynamic.menu', 'Parent')
    menu_url = fields.Char(string="Url")
    menu_sequence = fields.Char(string="Sequence")

    # @api.constrains('menu_sequence')
    # def check_sequence(self):
    #     for record in self:
    #         obj = self.search([('menu_sequence', '=', record.menu_sequence), ('id', '!=', record.id)])
    #         if obj:
    #             raise ValidationError("Sequence must be unique")


class DynamicButtons(models.Model):
    _name = 'dynamic.buttons'

    name = fields.Char(string="Name")
    menu_url = fields.Char(string="Url")

