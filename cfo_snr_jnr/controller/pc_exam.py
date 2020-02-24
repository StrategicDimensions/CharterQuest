import hashlib
import time
import werkzeug
from urllib.parse import urljoin
from odoo.http import request
import json, base64
from odoo import http, SUPERUSER_ID, _
from odoo.addons.payment_payu_com.controllers.main import PayuController


class PCExambooking(http.Controller):

    @http.route(['/registerPB'], type='http', auth="public", methods=['POST', 'GET'], website=True,
                csrf=False)
    def pc_exam_form_render(self):
        return request.render('cfo_snr_jnr.pc_exam_process_form', {'page_name': 'campus'})

    @http.route(['/reg'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def pc_exam_type_reg(self, **post):
        print('\n\n\n\n\n=======post======',post)
        value={}
        value['campus']=post.get('Select Campus')
        value['page_name']=post.get("page_name")
        return request.render('cfo_snr_jnr.pc_exam_type_process_form', value)

    @http.route(['/pcexamsearch'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def pc_exam_search_reg(self, **post):
        print("\n\n\n\n\n\===========exam post======",post)
        value={}
        value['campus'] = post.get('campus')
        value['page_name'] = post.get("page_name")
        value['select_exam_type'] = post.get('Select Exam Type')
        return request.render('cfo_snr_jnr.pc_exam_search_process_form', value)

    @http.route(['/examsearch'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def exam_search_reg(self, **post):
        print("\n\n\n\n\n\===========exam post======", post)
        return request.render('cfo_snr_jnr.exam_process_form', {'page_name': post.get('page_name')})

    @http.route(['/pricing'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def pricing(self, **post):
        print("\n\n\n\n\n\===========exam post======", post)
        return request.render('cfo_snr_jnr.exam_pricing_form', {'page_name': post.get('page_name')})

    @http.route(['/exam_registration'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def registration(self, **post):
        print("\n\n\n\n\n\===========exam post======", post)
        return request.render('cfo_snr_jnr.exam_registration_form', {'page_name': post.get('page_name')})

    @http.route(['/registerexam'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def registerexam(self, **post):
        print("\n\n\n\n\n\===========exam post======", post)
        return request.render('cfo_snr_jnr.exam_registration', {'page_name': post.get('page_name')})

    @http.route(['/exam/redirect_payu'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def exam_redirect(self, **post):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return_url = urljoin(base_url, '/exam/payment/payu_com/dpn/')
        cancel_url = urljoin(base_url, '/exam/payment/payu_com/cancel/')
        currency = request.env.ref('base.main_company').currency_id

        payment_acquire = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payu')])
        # amount = post.get('inputTotalDue') if post.get('inputTotalDue') else post.get('toalamount')
        payu_tx_values = dict(post)
        # first_name = ''
        # last_name = ''
        # if ' ' in sale_order_id.partner_id.name:
        #     first_name, last_name = sale_order_id.partner_id.name.split(' ', 1)
        # else:
        #     first_name = sale_order_id.partner_id.name
        transactionDetails = {}
        transactionDetails['store'] = {}
        transactionDetails['store']['soapUsername'] = payment_acquire.payu_api_username
        transactionDetails['store']['soapPassword'] = payment_acquire.payu_api_password
        transactionDetails['store']['safekey'] = payment_acquire.payu_seller_account
        transactionDetails['store']['environment'] = payment_acquire.environment
        transactionDetails['store']['TransactionType'] = 'PAYMENT'
        transactionDetails['basket'] = {}
        transactionDetails['basket']['description'] = 'CFO'
        transactionDetails['basket']['amountInCents'] = 0
        transactionDetails['basket']['currencyCode'] = currency.name
        transactionDetails['additionalInformation'] = {}
        transactionDetails['additionalInformation']['merchantReference'] = 'krupa'
        transactionDetails['additionalInformation']['returnUrl'] = return_url
        transactionDetails['additionalInformation']['cancelUrl'] = cancel_url
        transactionDetails['additionalInformation']['supportedPaymentMethods'] = 'CREDITCARD'
        transactionDetails['additionalInformation']['demoMode'] = False
        transactionDetails['Stage'] = False
        transactionDetails['customer'] = {}
        transactionDetails['customer']['email'] = ''
        transactionDetails['customer']['firstName'] = ''
        transactionDetails['customer']['lastName'] = ''
        transactionDetails['customer']['mobile'] = 12356

        if payment_acquire:
            payu_tx_values.update({
                'x_login': payment_acquire.payu_api_username,
                'x_merchant_id': payment_acquire.payu_seller_account,
                'x_trans_key': payment_acquire.payu_api_password,
                'x_fp_timestamp': str(int(time.time())),
                'x_fp_sequence': '%s%s' % (payment_acquire.id, int(time.time())),
                'currency_code': currency.name,
                'return': '%s' % urljoin(base_url, PayuController._return_url)
            })

        tx_values = {
            'acquirer_id': payment_acquire.id,
            'type': 'form',
            'amount': "{0:.2f}".format(0),
            'currency_id': currency.id,
            # 'partner_id': sale_order_id.partner_id.id,
            'partner_country_id': 1,
            'reference': request.env['payment.transaction'].get_next_reference('krupa'),
            # 'sale_order_id': sale_order_id.id,
        }

        tx = request.env['payment.transaction'].sudo().create(tx_values)
        url = PayuController.payuMeaSetTransactionApiCall('', transactionDetails)
        return werkzeug.utils.redirect(url)

    @http.route('/exam/payment/payu_com/dpn', type='http', auth="public", methods=['POST', 'GET'], website=True)
    def exam_payu_com_dpn(self, **post):
        """This method is used for getting response from Payu and create invoice automatically if successful"""
        cr, uid, context = request.cr, request.uid, request.context
        payment_acquire = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payu')])
        transactionDetails = {}
        transactionDetails['store'] = {}
        transactionDetails['store']['soapUsername'] = payment_acquire.payu_api_username
        transactionDetails['store']['soapPassword'] = payment_acquire.payu_api_password
        transactionDetails['store']['safekey'] = payment_acquire.payu_seller_account
        transactionDetails['store']['environment'] = payment_acquire.environment
        transactionDetails['additionalInformation'] = {}
        transactionDetails['additionalInformation']['payUReference'] = post['PayUReference']
        try:
            result = PayuController.payuMeaGetTransactionApiCall('', transactionDetails)
            payment_transation_id = request.env['payment.transaction'].sudo().search(
                [('reference', '=', result['merchantReference'])])
            payu_response = {}
            if result:
                payu_response['TRANSACTION_STATUS'] = result['transactionState']
                # payu_response['SUCCESSFUL'] = result['successful']
                payu_response['AMOUNT'] = payment_transation_id.amount * 100 if payment_transation_id else 0.00
                payu_response['CURRENCYCODE'] = result['basket']['currencyCode']
                payu_response['PAYUREFERENCE'] = result['payUReference']
                payu_response['REFERENCE'] = result['merchantReference']
                payu_response['RESULTMESSAGE'] = result['resultMessage']
            response_state = request.env['payment.transaction'].sudo().form_feedback(payu_response, 'payu')
            # response_state = PaymentTransactionCus.form_feedback('', payu_response, 'payu')
            # if response_state:
            #     return werkzeug.utils.redirect('/shop/payment/validate')
            # else:
            #     return werkzeug.utils.redirect('/shop/unsuccessful')

            # sale_order_id = request.env['sale.order'].sudo().search([('name', '=', result['merchantReference'])])
            # sale_order_data = sale_order_id
            # request.session['sale_last_order_id'] = sale_order_id.id
            #
            # tx_id = request.env['payment.transaction'].sudo().search([('reference', '=', result['merchantReference'])])
            # tx = tx_id
            # if not sale_order_id or (sale_order_id.amount_total and not tx):
            #     return request.redirect('/shop')
            # if (not sale_order_id.amount_total and not tx) or tx.state in ['pending']:
            #     if sale_order_id.state in ['draft', 'sent']:
            #         if (not sale_order_id.amount_total and not tx):
            #             sale_order_id.action_button_confirm()
            #         email_act = sale_order_id.action_quotation_send()
            # elif tx and tx.state == 'cancel':
            #     sale_order_id.action_cancel()
            # elif tx and (tx.state == 'draft' or tx.state == 'sent' or tx.state == 'done'):
            #     #             if result and payu_response['successful'] and payu_response['TRANSACTION_STATUS'] in ['SUCCESSFUL', 'PARTIAL_PAYMENT', 'OVER_PAYMENT']:
            #     if result and payu_response['TRANSACTION_STATUS'] in ['SUCCESSFUL', 'PARTIAL_PAYMENT', 'OVER_PAYMENT']:
            #         transaction = tx.sudo().write(
            #             {'state': 'done', 'date_validate': datetime.now(),
            #              'acquirer_reference': result['payUReference']})
            #         email_act = sale_order_id.action_quotation_send()
            #         action_confirm_res = sale_order_id.action_confirm()
            #         sale_order = sale_order_id.read([])
            #     #             if sale_order_id.state == 'sale':
            #     #                 journal_ids = request.env['account.journal'].sudo().search([('name', '=', 'FNB 62085815143')], limit=1)
            #     #                 journal = journal_ids.read([])
            #     currency = request.env['res.currency'].sudo().search([('name', '=', 'ZAR')], limit=1)
            #     method = request.env['account.payment.method'].sudo().search([('name', '=', 'Manual')], limit=1)
            #     journal_id = request.env['account.journal'].sudo().search(
            #         [('name', '=', 'FNB - Cheque Account 6208585815143')], limit=1, order="id desc")
            #     if journal_id:
            #         account_payment = {
            #             'partner_id': sale_order[0]['partner_id'][0],
            #             'partner_type': 'customer',
            #             'journal_id': journal_id.id,
            #             # 'invoice_ids':[(4,inv_obj.id,0)],
            #             'amount': sale_order[0]['amount_total'],
            #             'communication': sale_order_id.name,
            #             'currency_id': currency.id,
            #             'payment_type': 'inbound',
            #             'payment_method_id': method.id,
            #             'payment_transaction_id': tx.id,
            #         }
            #         acc_payment = request.env['account.payment'].sudo().create(account_payment)
            #         acc_payment.sudo().post()
            #     sale_order_id = request.session.get('sale_last_order_id')
            #     sale_order_data = request.env['sale.order'].sudo().browse(sale_order_id)
            #     # if sale_order_data.project_project_id:
            #     #     request.session['last_project_id'] = sale_order_data.project_project_id.id
            if response_state:
                # sale_order_data.message_post(subject="T&C's Privacy Policy",
                #                              body="%s accepted T&C's and Privacy Policy." % sale_order_data.partner_id.name)
                return werkzeug.utils.redirect('/pay/thankyou')
                # return werkzeug.utils.redirect('/shop/confirmation')
            else:
                return werkzeug.utils.redirect('/exam/unsuccessful')
        except Exception as e:
            return werkzeug.utils.redirect('/exam/unsuccessful')

    @http.route(['/exam/unsuccessful'], type='http', auth="public", website=True)
    def exam_unsuccessful(self, **post):

        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        cr, uid, context = request.cr, request.uid, request.context
        #
        # sale_order_id = request.session.get('sale_last_order_id')
        # if sale_order_id:
        #     order = request.env['sale.order'].sudo().browse(sale_order_id)
        # else:
        #     return request.redirect('/enrolment_book')
        # request.website.sale_reset()
        return request.render("cfo_snr_jnr.exam_unsuccessful")

    @http.route('/exam/payment/payu_com/cancel', type='http', auth="none", methods=['POST', 'GET'])
    def exam_payu_com_cancel(self, **post):
        """ When the user cancels its Payu payment: GET on this route """
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        return werkzeug.utils.redirect('/exam/unsuccessful')

