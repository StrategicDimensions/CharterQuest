
from odoo import fields, models,api, _
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
import logging
from odoo import exceptions
log = logging.getLogger(__name__)


class sale_advance_payment_inv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"
    _description = "Sales Advance Payment Invoice"

    def _get_advance_product(self):
        return self.env.ref('sale.advance_product_0').id

    @api.onchange('advance_payment_method')
    def onchange_method(self):
        if self.advance_payment_method == 'percentage':
            return {'value': {'amount': 0, 'product_id': False}}
        if self.product_id:
            # product = self.env['product.product'].browse(self.product_id.id)
            return {'value': {'amount': self.product_id.list_price}}
        return {'value': {'amount': 0}}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: