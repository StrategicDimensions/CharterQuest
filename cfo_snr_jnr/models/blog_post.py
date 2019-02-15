
from odoo import api, models, fields, _

class BlogPost(models.Model):
    _inherit = "blog.post"

    background_image = fields.Binary(string="Background Image")