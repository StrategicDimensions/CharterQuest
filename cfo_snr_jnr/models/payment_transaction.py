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

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError, _logger


class PaymentTransactionCus(models.Model):
    _inherit = "payment.transaction"

    @api.model
    def form_feedback(self, data, acquirer_name):
        invalid_parameters, tx = None, None

        tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
        if hasattr(self, tx_find_method_name):
            tx = getattr(self, tx_find_method_name)(data)

        # TDE TODO: form_get_invalid_parameters from model to multi
        invalid_param_method_name = '_%s_form_get_invalid_parameters' % acquirer_name
        if hasattr(self, invalid_param_method_name):
            invalid_parameters = getattr(tx, invalid_param_method_name)(data)

        if invalid_parameters:
            _error_message = '%s: incorrect tx data:\n' % (acquirer_name)
            for item in invalid_parameters:
                _error_message += '\t%s: received %s instead of %s\n' % (item[0], item[1], item[2])
            _logger.error(_error_message)
            return False

        # TDE TODO: form_validate from model to multi
        feedback_method_name = '_%s_form_validate' % acquirer_name
        if hasattr(self, feedback_method_name):
            return getattr(tx, feedback_method_name)(data)
        return True


class PayuTrans(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _payu_form_get_tx_from_data(self, data):
        """ Given a data dict coming from payu, verify it and find the related
        transaction record. """
        reference = data.get('REFERENCE')
        transaction = self.search([('reference', '=', reference)])
        if not transaction:
            error_msg = (_('PayU: received data for reference %s; no order found') % (reference))
            raise ValidationError(error_msg)
        elif len(transaction) > 1:
            error_msg = (_('PayU: received data for reference %s; multiple orders found') % (reference))
            raise ValidationError(error_msg)
        return transaction

    @api.multi
    def _payu_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        if self.acquirer_reference and data.get('PAYUREFERENCE') != self.acquirer_reference:
            invalid_parameters.append(('Transaction Id', data.get('PAYUREFERENCE'), self.acquirer_reference))
        # check what is buyed
        amount = data.get('AMOUNT', 0)
        if int(amount) != int(self.amount * 100):  # payu send amount in cent
            invalid_parameters.append(('Amount', data.get('AMOUNT'), '%.2f' % self.amount))
        if data.get('CURRENCYCODE') != self.currency_id.name:
            invalid_parameters.append(('Currency', data.get('CURRENCYCODE'), self.currency_id.name))
        return invalid_parameters

    @api.multi
    def _payu_form_validate(self, data):
        status = data.get('TRANSACTION_STATUS')
        data = {
            'acquirer_reference': data.get('PAYUREFERENCE'),
            'state_message': data.get('RESULTMESSAGE', ''),
            'date_validate': fields.Datetime.now()
        }
        if status == 'SUCCESSFUL':
            self.write(dict(data, state='done'))
            return True
        elif status == 'PROCESSING':
            self.write(dict(data, state='pending'))
            return True
        elif status == 'FAILED':
            self.write(dict(data, state='error'))
            return False
        elif status == 'NEW':
            self.write(dict(data, state='draft'))
            return True
        else:
            error = _('Payu: feedback error')
            self.write(dict(data, state_message=error, state='error'))
            return False