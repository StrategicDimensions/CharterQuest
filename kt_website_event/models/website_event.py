# -*- coding: utf-8 -*-

from odoo import models, fields

class event_type(models.Model):
    _inherit = 'event.type'

    publish_on_website = fields.Boolean('Publish on Website')
    publish_on_portal = fields.Boolean('Publish on Portal')


class event_ticket(models.Model):
    _inherit = 'event.event.ticket'

    is_free = fields.Boolean('Is Free')


class Dynamic_menu(models.Model):
    _name = 'dynamic.menu'

    name = fields.Char(string="Main Menu")
    parent_id = fields.Many2one('dynamic.menu', 'name')
    menu_url = fields.Char(string="Url")
