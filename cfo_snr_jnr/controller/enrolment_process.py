import base64
import hashlib
import time
from urllib.parse import urljoin

import werkzeug
from dateutil.relativedelta import relativedelta
from pkg_resources import require
from odoo import http
from odoo.http import request
from datetime import date, datetime
from odoo import http, SUPERUSER_ID, _
import PyPDF2
import json, base64
from odoo.addons.payment_payu_com.controllers.main import PayuController
from odoo.addons.cfo_snr_jnr.models.payment_transaction import PaymentTransactionCus
import odoo.addons.website_sale.controllers.main as website_sale
from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery

_logger = logging.getLogger(__name__)

# from CharterQuest.payment_payu_com.controllers.main import PayuController


class WebsiteSaleDelivery(WebsiteSaleDelivery):

    @http.route(['/shop/update_carrier'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_eshop_carrier(self, **post):
        order = request.website.sale_get_order()
        if request.session.get('sale_last_order_id'):
            order = request.env['sale.order'].sudo().browse([request.session.get('sale_last_order_id')])
        carrier_id = int(post['carrier_id'])
        delivery_carrier_id = request.env['delivery.carrier'].sudo().browse(carrier_id)
        if delivery_carrier_id:
            if delivery_carrier_id.warehouse_id:
                order.warehouse_id = delivery_carrier_id.warehouse_id.id
        if order:
            order._check_carrier_quotation(force_carrier_id=carrier_id)

            return {'status': order.delivery_rating_success,
                    'error_message': order.delivery_message,
                    'carrier_id': carrier_id,
                    'new_amount_delivery': '%.2f' % order.currency_id.round(order.delivery_price),
                    'new_amount_untaxed': '%.2f' % order.amount_untaxed,
                    'new_amount_tax': '%.2f' % order.amount_tax,
                    'new_amount_total': '%.2f' % order.amount_total,
                    }


class WebsiteSale(website_sale.WebsiteSale):

    def _get_shop_payment_values(self, order, **kwargs):
        shipping_partner_id = False
        if order:
            shipping_partner_id = order.partner_shipping_id.id or order.partner_invoice_id.id

        values = dict(
            website_sale_order=order,
            errors=[],
            partner=order.partner_id.id,
            order=order,
            payment_action_id=request.env.ref('payment.action_payment_acquirer').id,
            return_url='/shop/payment/validate',
            bootstrap_formatting=True
        )

        acquirers = request.env['payment.acquirer'].search(
            [('website_published', '=', True), ('company_id', '=', order.company_id.id)], order='id desc'
        )

        values['access_token'] = order.access_token
        values['form_acquirers'] = [acq for acq in acquirers if acq.payment_flow == 'form' and acq.view_template_id]
        values['s2s_acquirers'] = [acq for acq in acquirers if
                                   acq.payment_flow == 's2s' and acq.registration_view_template_id]
        values['tokens'] = request.env['payment.token'].search(
            [('partner_id', '=', order.partner_id.id),
             ('acquirer_id', 'in', acquirers.ids)])

        for acq in values['form_acquirers']:
            acq.form = acq.with_context(submit_class='btn btn-primary', submit_txt=_('Pay Now')).sudo().render(
                '/',
                order.amount_total,
                order.pricelist_id.currency_id.id,
                values={
                    'return_url': '/shop/payment/validate',
                    'partner_id': shipping_partner_id,
                    'billing_partner_id': order.partner_invoice_id.id,
                }
            )
        if not order._get_delivery_methods():
            values['errors'].append(
                (_('Sorry, we are unable to ship your order'),
                 _('No shipping method is available for your current order and shipping address. '
                   'Please contact us for more information.')))

        has_stockable_products = any(line.product_id.type in ['consu', 'product'] for line in order.order_line)
        if has_stockable_products:
            if order.carrier_id and not order.delivery_rating_success:
                values['errors'].append(
                    (_("Ouch, you cannot choose this carrier!"),
                     _("%s does not ship to your address, please choose another one.\n(Error: %s)" % (
                         order.carrier_id.name, order.delivery_message))))
                order._remove_delivery_line()

            delivery_carriers = order._get_delivery_methods()
            values['deliveries'] = delivery_carriers.sudo()

        values['delivery_action_id'] = request.env.ref('delivery.action_delivery_carrier_form').id

        return values

    @http.route(['/shop/addpayment/<uuid>'], type='http', auth="public", methods=['POST', 'GET'], website=True,
                csrf=False)
    def shop_addpayment(self, uuid=False, **post):
        order_id = request.env['sale.order'].sudo().search([('sale_link', '=', uuid)])
        if order_id:
            request.session['sale_last_order_id'] = order_id.id
            render_values = self._get_shop_payment_values(order_id, **post)
            if render_values['errors']:
                render_values.pop('acquirers', '')
                render_values.pop('tokens', '')

            return request.render('cfo_snr_jnr.shop_payment', render_values)

    @http.route(['/shop/payment/transaction/',
                 '/shop/payment/transaction/<int:so_id>',
                 '/shop/payment/transaction/<int:so_id>/<string:access_token>'], type='json', auth="public",
                website=True)
    def payment_transaction(self, acquirer_id, save_token=False, so_id=None, access_token=None, token=None, **kwargs):
        tx_type = 'form'
        if save_token:
            tx_type = 'form_save'

        request.session['shop_do_invoice'] = kwargs.get('do_invoice')
        request.session['shop_company_name'] = kwargs.get('company_name') if kwargs.get('company_name') else ''
        request.session['shop_vat_number'] = kwargs.get('vat_no') if kwargs.get('vat_no') else ''

        # In case the route is called directly from the JS (as done in Stripe payment method)
        if so_id and access_token:
            order = request.env['sale.order'].sudo().search([('id', '=', so_id), ('access_token', '=', access_token)])
        elif so_id:
            order = request.env['sale.order'].search([('id', '=', so_id)])
        else:
            order = request.website.sale_get_order()
            if request.session.get('sale_last_order_id'):
                order = request.env['sale.order'].sudo().browse([request.session.get('sale_last_order_id')])
        if not order or not order.order_line or acquirer_id is None:
            return False

        assert order.partner_id.id != request.website.partner_id.id

        # find or create transaction
        tx = request.website.sale_get_transaction() or request.env['payment.transaction'].sudo()
        acquirer = request.env['payment.acquirer'].browse(int(acquirer_id))
        payment_token = request.env['payment.token'].sudo().browse(int(token)) if token else None
        tx = tx._check_or_create_sale_tx(order, acquirer, payment_token=payment_token, tx_type=tx_type)
        request.session['sale_transaction_id'] = tx.id
        return tx.render_sale_button(order, '/shop/payment/validate')

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        request.website.sale_get_order(force_create=1)._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            attributes=self._filter_attributes(**kw),
            warehouse_id=kw.get('warehouse_id'),
        )
        return request.redirect("/shop/cart")

    def _get_mandatory_billing_fields(self):
        return ["name", "email", "street", "city", "country_id", "zip"]

    def _get_mandatory_shipping_fields(self):
        return ["name", "street", "city", "country_id", "zip"]


class EnrolmentProcess(http.Controller):

    @http.route(['/check_product_stock'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def check_product_stock(self, **post):
        if post.get('warehouse_id') and post.get('product_id'):
            product_id = request.env['product.product'].sudo().browse(int(post.get('product_id')))
            if product_id:
                ctx = {'warehouse': int(post.get('warehouse_id')), 'product_id': product_id.id}
                stock = product_id.with_context(ctx)._compute_quantities_dict(lot_id=False, owner_id=False,
                                                                              package_id=False, from_date=False,
                                                                              to_date=False)
                if stock.get(product_id.id).get('qty_available'):
                    return {'product_stock_qty': stock.get(product_id.id).get('qty_available')}
        return {'product_stock_qty': ''}

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        sale_order_id = request.session.get('sale_last_order_id')
        email_obj = request.env['mail.template']
        mail_obj = request.env['mail.mail'].sudo()
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            m = hashlib.md5()
            m.update(order.name.encode())
            decoded_quote_name = m.hexdigest()

            config_para = request.env['ir.config_parameter'].sudo().search([('key', 'ilike', 'web.base.url')])
            if config_para:
                link = config_para.value + "/shop/addpayment/" + decoded_quote_name
                order.sale_order_link = link
                order.sale_link = decoded_quote_name

            if order.payment_acquirer_id:
                acquirer_id = request.env['payment.acquirer'].sudo().browse(int(order.payment_acquirer_id))
                if acquirer_id.provider == 'transfer' and request.session.get(
                        'shop_do_invoice') and request.session.get('shop_do_invoice') == 'yes':
                    order.quote_type = 'CharterBooks'
                    order.partner_id.vat_no_comp = request.session.get('shop_vat_number') if request.session.get(
                        'shop_vat_number') else ''
                    order.partner_id.student_company = request.session.get('shop_company_name') if request.session.get(
                        'shop_company_name') else ''
                    inv_line_data = []
                    for each_line in order.order_line:
                        if each_line.product_id:
                            product_id = each_line.product_id.sudo()
                            if product_id:
                                inv_line_data.append((0, 0, {
                                    'account_id': product_id.property_account_income_id.id or product_id.categ_id.property_account_income_categ_id.id,
                                    'name': each_line.name,
                                    'origin': order.name,
                                    'price_unit': each_line.price_unit,
                                    'quantity': each_line.product_uom_qty,
                                    'discount': 0.0,
                                    'product_id': product_id.id,
                                    'sale_line_ids': [(6, 0, [each_line.id])],
                                    'account_analytic_id': order.analytic_account_id.id or False,
                                }))
                    invoice_details = request.env['account.invoice'].sudo().create({
                        'name': order.client_order_ref or order.name,
                        'origin': order.name,
                        'type': 'out_invoice',
                        'sale_order_id': order.id,
                        'reference': False,
                        'account_id': order.partner_id.property_account_receivable_id.id,
                        'partner_id': order.partner_invoice_id.id,
                        'partner_shipping_id': order.partner_shipping_id.id,
                        'invoice_line_ids': inv_line_data,
                        'currency_id': order.pricelist_id.currency_id.id,
                        'payment_term_id': order.payment_term_id.id,
                        'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
                        'team_id': order.team_id.id,
                        'user_id': order.user_id.id,
                        'comment': order.note,
                    })
                    invoice_details.compute_taxes()
                    if invoice_details:
                        order._get_invoiced()
                    invoice_details.action_invoice_open()

                    order.sudo().action_confirm()
                    for line in order.order_line:
                        line.write({
                            'qty_invoiced': line.product_uom_qty
                        })
                    template_id = email_obj.sudo().search([('name', '=', "CharterBooks Saleorder Confirm Email")])
                    if template_id:
                        attchment_list = []
                        pdf_data_invoice = request.env.ref(
                            'event_price_kt.report_invoice_book').sudo().render_qweb_pdf(invoice_details.id)
                        if pdf_data_invoice:
                            pdfvals = {'name': 'Charterbooks Invoice',
                                       'db_datas': base64.b64encode(pdf_data_invoice[0]),
                                       'datas': base64.b64encode(pdf_data_invoice[0]),
                                       'datas_fname': 'Charterbooks Invoice.pdf',
                                       'res_model': 'account.invoice',
                                       'type': 'binary'}
                            pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                            attchment_list.append(pdf_create)

                        agreement_id = request.env.ref('cfo_snr_jnr.charterbook_term_and_condition_pdf')
                        if agreement_id:
                            attchment_list.append(agreement_id)

                        email_data = template_id.generate_email(order.id)

                        mail_values = {
                            'email_from': email_data.get('email_from'),
                            'email_cc': email_data.get('email_cc'),
                            'reply_to': email_data.get('reply_to'),
                            'email_to': email_data.get('email_to'),
                            'subject': email_data.get('subject'),
                            'body_html': email_data.get('body_html'),
                            'notification': True,
                            'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                            'auto_delete': False,
                            'model': 'account.invoice',
                            'res_id': invoice_details.id
                        }
                        msg_id = mail_obj.create(mail_values)
                        msg_id.send()
                elif acquirer_id.provider == 'transfer' and request.session.get(
                        'shop_do_invoice') and request.session.get('shop_do_invoice') == 'no':
                    order.quote_type = 'CharterBooks'
                    attchment_list = []
                    template_id = email_obj.sudo().search([('name', '=', "CharterBooks Saleorder Confirm Email")])
                    if template_id:
                        pdf_data_order = request.env.ref(
                            'event_price_kt.report_sale_book').sudo().render_qweb_pdf(order.id)
                        if pdf_data_order:
                            pdfvals = {'name': 'Charterbooks Proforma',
                                       'db_datas': base64.b64encode(pdf_data_order[0]),
                                       'datas': base64.b64encode(pdf_data_order[0]),
                                       'datas_fname': 'Charterbooks_Proforma.pdf',
                                       'res_model': 'sale.order',
                                       'type': 'binary'}
                            pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                            attchment_list.append(pdf_create)

                        agreement_id = request.env.ref('cfo_snr_jnr.charterbook_term_and_condition_pdf')
                        if agreement_id:
                            attchment_list.append(agreement_id)
                        email_data = template_id.generate_email(order.id)
                        mail_values = {
                            'email_from': email_data.get('email_from'),
                            'email_cc': email_data.get('email_cc'),
                            'reply_to': email_data.get('reply_to'),
                            'email_to': email_data.get('email_to'),
                            'subject': email_data.get('subject'),
                            'body_html': email_data.get('body_html'),
                            'notification': True,
                            'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                            'auto_delete': False,
                            'model': 'sale.order',
                            'res_id': order.id
                        }
                        msg_id = mail_obj.create(mail_values)
                        msg_id.send()
                else:
                    attchment_list = []
                    order.quote_type = 'CharterBooks'
                    # template_id = email_obj.sudo().search([('name', '=', "CharterBooks Saleorder Confirm Email")])
                    template_id = email_obj.sudo().search([('name', '=', "Delivery Order Created")])
                    if template_id:
                        pdf_data_order = request.env.ref(
                            'event_price_kt.report_invoice_book').sudo().render_qweb_pdf(order.invoice_ids.id)
                        if pdf_data_order:
                            pdfvals = {'name': 'Invoice Report',
                                       'db_datas': base64.b64encode(pdf_data_order[0]),
                                       'datas': base64.b64encode(pdf_data_order[0]),
                                       'datas_fname': 'Invoice Report.pdf',
                                       'res_model': 'account.invoice',
                                       'type': 'binary'}
                            pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                            attchment_list.append(pdf_create)

                        agreement_id = request.env.ref('cfo_snr_jnr.charterbook_term_and_condition_pdf')
                        if agreement_id:
                            attchment_list.append(agreement_id)
                        email_data = template_id.generate_email(order.picking_ids[0].id)
                        mail_values = {
                            'email_from': email_data.get('email_from'),
                            'email_cc': email_data.get('email_cc'),
                            'reply_to': email_data.get('reply_to'),
                            'email_to': email_data.get('email_to'),
                            'subject': email_data.get('subject'),
                            'body_html': email_data.get('body_html'),
                            'notification': True,
                            'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                            'auto_delete': False,
                            'model': 'sale.order',
                            'res_id': order.id
                        }
                        msg_id = mail_obj.create(mail_values)
                        msg_id.send()
                        # mail_message = template_id.send_mail(
                        #     order.id)
                        # email_obj.sudo().send_mail(template_id[0],order.id)
            return request.render("website_sale.confirmation", {'order': order})
        else:
            return request.redirect('/shop')

    @http.route(['/enrolment_reg'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def enrolment_reg(self):
        reg_and_enrol = request.session['reg_and_enrol'] if request.session.get('reg_and_enrol') else ''
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        request.session['reg_and_enrol'] = ''
        return request.render('cfo_snr_jnr.enrolment_process_registration', {'page_name': 'registration',
                                                                             'self_or_cmp': user_select[
                                                                                 'self_or_company'] if user_select and user_select.get(
                                                                                 'self_or_company') else ''})

    @http.route(['/registration_form', '/registration_form/<uuid>'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def registration_form(self,uuid=False, **post):
        sale_order_id = False
        if uuid:
            sale_order_id = request.env['sale.order'].sudo().search([('debit_link', '=', uuid)])
        user_select = request.session['user_selection_type'] if request.session and request.session.get('user_selection_type') else ''
        return request.render('cfo_snr_jnr.enrolment_process_registration_and_enroll', {'page_name': 'registration',
                                                                                        'self_or_cmp': user_select[
                                                                                            'self_or_company'] if user_select and user_select and user_select.get(
                                                                                            'self_or_company') else '',
                                                                                            'uuid': uuid,
                                                                                            'sale_order_id': sale_order_id if sale_order_id else False
                                                                                        })

    @http.route(['/enrolment_book'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def enrolment_book(self):
        request.session['reg_and_enrol'] = ''
        return request.render('cfo_snr_jnr.get_free_quote_email_tmp', {'page_name': 'book'})

    @http.route(['/dynamic_login'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def dynamic_login(self):
        request.session['reg_and_enrol'] = ''
        return request.render('cfo_snr_jnr.dynamic_login_buttons')

    @http.route(['/max_discount_ready'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def max_discount_ready(self, **post):
        # if post.get('discount'):
        request.session['reg_and_enrol'] = ''
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        today_date = datetime.today()
        str_today_date = datetime.strftime(today_date, '%Y-%m-%d')
        max_discount_detail = request.env['event.max.discount'].sudo().search(
            [('prof_body', '=', int(user_select['Select Prof Body']) if user_select else '')],
            limit=1, order="id desc")

        return {'discount': max_discount_detail.max_discount}

    @http.route(['/max_discount'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def max_discount(self, **post):
        # if post.get('discount'):
        request.session['discount_id'] = post.get('discount') if post.get('discount') else ''
        request.session['reg_and_enrol'] = ''
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        today_date = datetime.today()
        str_today_date = datetime.strftime(today_date, '%Y-%m-%d')
        max_discount_detail = request.env['event.max.discount'].sudo().search([('prof_body', '=',
                                                                                int(user_select[
                                                                                        'Select Prof Body']) if user_select else '')],
                                                                              limit=1, order="id desc")
        return {'discount': max_discount_detail.max_discount}

    @http.route(['/check_email'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def check_email(self, **post):
        if post:
            res_partner_detail = request.env['res.partner'].sudo().search([('email', '=', post['email'])])
            if res_partner_detail:
                return True
        return False

    @http.route(['/get_free_email'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def get_free_email(self, **post):
        value_grand_tot = float(post['grand_tot'].replace(',', '')) if post.get('grand_tot') else 0
        value_product_tot = float(post['product_tot'].replace(',', '')) if post.get('product_tot') else 0
        request.session['grand_tot'] = format(value_grand_tot, '.2f')
        request.session['product_tot'] = format(value_product_tot, '.2f')
        request.session['reg_and_enrol'] = ''
        return True

    @http.route(['/reg_enroll'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def reg_enroll(self, **post):
        request.session['reg_enrol_btn'] = True
        request.session['sale_order'] = False
        return True

    @http.route(['/free_quote'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def free_quote(self, **post):
        request.session['reg_enrol_btn'] = False
        request.session['sale_order'] = False
        return True

    @http.route(['/registration'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def registration(self, **post):
        request.session['grand_tot'] = float(post['grand_tot'].replace(',', '')) if post.get('grand_tot') else 0
        request.session['product_tot'] = float(post['product_tot'].replace(',', '')) if post.get('product_tot') else 0
        request.session['reg_and_enrol'] = ''
        return True

    @http.route(['/check_number'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def check_number(self, **post):
        if post:
            res_partner_detail = request.env['res.partner'].sudo().search([('mobile', '=', post['number'])])
            if res_partner_detail:
                return True
        return False

    @http.route(['/get_event_data'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def get_event_data(self, **post):
        event_dict = {'location': [], 'semester': []}
        if post.get('professional_body'):
            events = request.env['event.event'].sudo().search(
                [('event_type_id', '=', int(post.get('professional_body')))])

            for each_event in events:
                if event_dict['semester']:
                    if not any(each['id'] == each_event.semester_id.id for each in event_dict['semester']):
                        event_dict['semester'].append({'id': each_event.semester_id.id,
                                                       'name': each_event.semester_id.name})
                else:
                    event_dict['semester'].append(
                        {'id': each_event.semester_id.id, 'name': each_event.semester_id.name})

                if event_dict['location']:
                    for each in each_event.address_ids:
                        if not any(each_location['id'] == each.id for each_location in event_dict['location']):
                            event_dict['location'].append({'id': each.id, 'name': each.name})
                else:
                    for each in each_event.address_ids:
                        event_dict['location'].append({'id': each.id, 'name': each.name})
        return event_dict

    @http.route(['/enrolment_book_prof'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def enrolment_book_prof(self, **post):
        today_date = datetime.today()
        str_today_date = datetime.strftime(today_date, '%Y-%m-%d 00:00:00')
        # str_today_end_date = datetime.strftime(today_date, '%Y-%m-%d 23:59:59')
        request.session['user_selection_type'] = post
        request.session['return_student'] = post.get('return_student')
        if post.get('Select Prof Body') and post.get('campus'):
            event_details = request.env['event.event'].sudo().search([('event_type_id', '=',
                                                                       int(post.get('Select Prof Body'))),
                                                                      ('address_ids', 'in', int(post.get('campus'))),
                                                                      ('semester_id', '=', int(post.get('Semester'))) if post.get('Semester') else False,
                                                                      ('state', '!=', 'cancel'),
                                                                      ('date_end', '>=', str_today_date)])
            event_details_dict = {}
            duplicate_event_detail_dict = {}
            for each in event_details:
                if each.qualification and each.event_ticket_ids:
                    if each.qualification.order in event_details_dict:
                        if any(each.qualification.name == each_dict for each_dict in
                               event_details_dict[each.qualification.order]):
                            if not any(each == each_dict for each_dict in
                                       event_details_dict[each.qualification.order][each.qualification.name]['event']):
                                event_details_dict[each.qualification.order][each.qualification.name]['event'].append(
                                    each)
                            for each_ticket in each.event_ticket_ids:
                                if each_ticket.product_id not in \
                                        event_details_dict[each.qualification.order][each.qualification.name][
                                            'ticket_product']:
                                    event_details_dict[each.qualification.order][each.qualification.name][
                                        'ticket_product'].append(each_ticket.product_id)
                        else:
                            if not each.qualification.name in duplicate_event_detail_dict:
                                if each.event_ticket_ids:
                                    duplicate_event_detail_dict[each.qualification.name] = {'ticket_product': [],
                                                                                            'event': []}
                                    for each_ticket in each.event_ticket_ids:
                                        if each_ticket.product_id not in \
                                                duplicate_event_detail_dict[each.qualification.name]['ticket_product']:
                                            duplicate_event_detail_dict[each.qualification.name][
                                                'ticket_product'].append(each_ticket.product_id)
                                        if each not in duplicate_event_detail_dict[each.qualification.name]['event']:
                                            duplicate_event_detail_dict[each.qualification.name]['event'].append(each)
                            else:
                                if any(each.qualification.name == each_dict for each_dict in
                                       duplicate_event_detail_dict):
                                    if not any(each == each_dict for each_dict in
                                               duplicate_event_detail_dict[each.qualification.name]['event']):
                                        duplicate_event_detail_dict[each.qualification.name]['event'].append(each)
                                    for each_ticket in each.event_ticket_ids:
                                        if each_ticket.product_id not in \
                                                duplicate_event_detail_dict[each.qualification.name]['ticket_product']:
                                            duplicate_event_detail_dict[each.qualification.name][
                                                'ticket_product'].append(each_ticket.product_id)
                    else:
                        if each.event_ticket_ids:
                            event_details_dict[each.qualification.order] = {
                                each.qualification.name: {'ticket_product': [], 'event': []}}
                            for each_ticket in each.event_ticket_ids:
                                if each_ticket.product_id not in \
                                        event_details_dict[each.qualification.order][each.qualification.name][
                                            'ticket_product']:
                                    event_details_dict[each.qualification.order][each.qualification.name][
                                        'ticket_product'].append(each_ticket.product_id)
                                if each not in event_details_dict[each.qualification.order][each.qualification.name][
                                    'event']:
                                    event_details_dict[each.qualification.order][each.qualification.name][
                                        'event'].append(each)
            if duplicate_event_detail_dict:
                for each_duplicate in duplicate_event_detail_dict:
                    event_keys = sorted(list(event_details_dict.keys()))
                    event_details_dict[event_keys[-1] + 1] = {
                        each_duplicate: duplicate_event_detail_dict[each_duplicate]}

            for each in event_details_dict:
                for each_level in event_details_dict[each]:
                    event_order_list = []
                    for each_event in event_details_dict[each][each_level]['event']:
                        event_order_list.append(each_event.id)
                    event_details = request.env['event.event'].sudo().search([('id', 'in', event_order_list)],
                                                                             order="name ASC")
                    event_details_dict[each][each_level]['event'] = event_details
            return request.render('cfo_snr_jnr.enrolment_process_form_2',
                                  {'enrolment_data': dict(sorted(event_details_dict.items())),
                                   'page_name': post.get('page_name'),
                                   'self_or_cmp': post['self_or_company'] if post.get('self_or_company') else ''})
        return request.render('cfo_snr_jnr.enrolment_process_form')

    @http.route(['/prof_body_form_render'], type='http', auth="public", methods=['POST', 'GET'], website=True,
                csrf=False)
    def prof_body_form_render(self):
        return request.render('cfo_snr_jnr.enrolment_process_form', {'page_name': 'campus'})

    @http.route(['/fees_level'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def course_level(self, **post):
        request.session['event_id'] = post
        request.session['reg_and_enrol'] = ''
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        course_level = []
        event_type = []
        fees_dict = {}
        if user_select:
            #     for each_value in post.values():
            #         event_ticket_id = request.env['event.event.ticket'].search([('id', '=', int(each_value))])
            #         event_detail = request.env['event.event'].sudo().search([('id', '=', event_ticket_id.event_id.id)])
            #         if event_detail.qualification.id not in course_level:
            #             course_level.append(event_detail.qualification.id)
            #         if event_detail.event_type_id.id not in event_type:
            #             event_type.append(event_detail.event_type_id.id)
            # if request.session['return_student'] == 'Yes':
            #     product_detail = request.env['product.product'].sudo().search([('event_type_rem', 'in', event_type),
            #                                                                    ('event_qual_rem', 'in', course_level),
            #                                                                    ('does_not_apply', '=', 'return_student')])
            # else:
            #     product_detail = request.env['product.product'].sudo().search([('event_type_rem', 'in', event_type),
            #                                                                    ('event_qual_rem', 'in', course_level),
            #                                                                    ('does_not_apply', '=', 'new_student')])
            product_detail = request.env['product.product'].sudo().search([('event_type_rem', '=', int(
                user_select['Select Prof Body']) if user_select.get('Select Prof Body') else '')])
            if product_detail:
                for each_product in product_detail:
                    if each_product.event_qual_rem.order not in fees_dict:
                        fees_dict[each_product.event_qual_rem.order] = {
                            each_product.event_qual_rem: {each_product.event_feetype_rem: [each_product]}}
                    else:
                        if each_product.event_feetype_rem in fees_dict[each_product.event_qual_rem.order][
                            each_product.event_qual_rem]:
                            fees_dict[each_product.event_qual_rem.order][each_product.event_qual_rem][
                                each_product.event_feetype_rem].append(each_product)
                        else:
                            fees_dict[each_product.event_qual_rem.order][each_product.event_qual_rem][
                                each_product.event_feetype_rem] = [each_product]
                return request.render('cfo_snr_jnr.enrolment_process_form3',
                                      {'fees_detail': dict(sorted(fees_dict.items())),
                                       'page_name': 'fees',
                                       'return_student': user_select['return_student'] if user_select.get(
                                           'self_or_company') else '',
                                       'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                           'self_or_company') else ''})
            return request.render('cfo_snr_jnr.enrolment_process_form3', {'page_name': 'fees',
                                                                          'self_or_cmp': user_select[
                                                                              'self_or_company'] if user_select.get(
                                                                              'self_or_company') else ''})
        return request.render('cfo_snr_jnr.enrolment_process_form3')

    @http.route(['/discount'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def discount(self, **post):
        request.session['product_id'] = post
        request.session['reg_and_enrol'] = ''
        event_tickets = request.session['event_id'] if request.session.get('event_id') else ''
        event_type = []
        discount_detail_list = []
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        if user_select:
            if user_select['self_or_company'] == 'cmp_sponosored':
                request.session['discount_id'] = ''
                request.session['discount_add'] = ''
                return request.redirect('/price')
            else:
                if post:
                    for each in post.values():
                        product_detail = request.env['product.product'].sudo().search([('id', '=', each)])
                        if product_detail.event_type_rem.id not in event_type:
                            event_type.append(product_detail.event_type_rem.id)
                if user_select:
                    event_count = []
                    if event_tickets:
                        for key, value in event_tickets.items():
                            event_ticket_details = request.env['event.event.ticket'].sudo().search(
                                [('id', '=', int(value))])
                            if event_ticket_details:
                                if not event_ticket_details.event_id in event_count:
                                    event_count.append(event_ticket_details.event_id)
                    discount_detail = request.env['event.discount'].sudo().search([('event_type_id', '=', int(
                        user_select['Select Prof Body']) if user_select.get('Select Prof Body') else '')])
                    for each_discount in discount_detail:
                        if each_discount not in discount_detail_list:
                            discount_detail_list.append(each_discount)
                    request.session['event_count'] = len(event_count) if event_count else 0
                    return request.render('cfo_snr_jnr.enrolment_process_discount_form_1',
                                          {'discount_detail': discount_detail_list,
                                           'select_prof': user_select['Select Prof Body'],
                                           'page_name': 'discounts',
                                           'event_len': len(event_count) if event_count else 0})
                return request.render('cfo_snr_jnr.enrolment_process_discount_form_1')

    @http.route(['/price'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def price(self, **post):
        display_btn = request.session['reg_enrol_btn'] if request.session.get('reg_enrol_btn') else False
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        if post:
            request.session['discount_id'] = request.session['discount_id'] if request.session.get(
                'discount_id') else ''
            request.session['discount_add'] = post.get('discount_add') if post.get('discount_add') else 0
            return request.render('cfo_snr_jnr.enrolment_process_price', {'product_id': request.session['product_id'],
                                                                          'event_id': request.session['event_id'],
                                                                          'page_name': 'price',
                                                                          'discount': float(
                                                                              post.get('discount_add')) if post.get(
                                                                              'discount_add') else 0.0,
                                                                          'btn_display': display_btn,
                                                                          'self_or_cmp': user_select[
                                                                              'self_or_company'] if user_select.get(
                                                                              'self_or_company') else ''})
        else:
            request.session['discount_add'] = 0.0
            return request.render('cfo_snr_jnr.enrolment_process_price', {'product_id': request.session['product_id'],
                                                                          'event_id': request.session['event_id'],
                                                                          'page_name': 'price',
                                                                          'discount': 0.0,
                                                                          'btn_display': display_btn,
                                                                          'self_or_cmp': user_select[
                                                                              'self_or_company'] if user_select.get(
                                                                              'self_or_company') else ''})

    @http.route(['/debitorder', '/debitorder/<uuid>'], type='http', auth="public", methods=['POST', 'GET'],
                website=True,
                csrf=False)
    def debitorder(self, uuid=False, **post):
        if uuid:
            sale_order_id = request.env['sale.order'].sudo().search([('debit_link', '=', uuid)])
            product_tot = 0.00
            grand_tot = 0.00
            if sale_order_id:
                for each in sale_order_id.order_line:
                    if each.product_id.fee_ok:
                        product_tot += each.price_subtotal
                    if each.product_id.event_ok:
                        grand_tot += each.price_subtotal
                if sale_order_id.quote_type == 'enrolment':
                    return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                                    'product_tot': round(product_tot,
                                                                                                         2),
                                                                                    'grand_tot': round(grand_tot, 2),
                                                                                    'sale_order_id': sale_order_id if sale_order_id else '',
                                                                                    'mandate_link': 'mandate_link_find',
                                                                                    'bank_detail': True if sale_order_id.affiliation==1 else False})
                if sale_order_id.quote_type == 'freequote':
                    return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                                    'product_tot': round(product_tot,
                                                                                                         2),
                                                                                    'grand_tot': round(grand_tot, 2),
                                                                                    'sale_order_id': sale_order_id if sale_order_id else '',
                                                                                    'mandate_link': 'mandate_link_find',
                                                                                    'bank_detail': True if sale_order_id.affiliation==1 else False})
        return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                        'product_tot': round(product_tot),
                                                                        'grand_tot': round(grand_tot)
                                                                        })

    @http.route(['/payment','/payment/<uuid>','/payment/<uuid>/<uuid2>'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def payment(self,**post):
        if post.get('uuid'):
            sale_order_id = request.env['sale.order'].sudo().search([('debit_link', '=', post.get('uuid'))])
            if sale_order_id and sale_order_id.debit_order_mandate:
                return request.render('cfo_snr_jnr.debit_order_submitted')
            else:
                product_tot = 0.00
                grand_tot = 0.00
                if sale_order_id:
                    for each in sale_order_id.order_line:
                        if each.product_id.fee_ok:
                            product_tot += each.price_subtotal
                        if each.product_id.event_ok:
                            grand_tot += each.price_subtotal

                    name = ''
                    res_partner_obj = request.env['res.partner'].sudo()
                    if post.get('inputFirstName'):
                        name = post.get('inputFirstName') or ''
                    else:
                        name += ''
                    if post.get('inputLastName'):
                        name += ' ' + post.get('inputLastName') or ''

                    account_rec_type_id = request.env['account.account.type'].sudo().search(
                        [('name', 'ilike', 'Receivable')])
                    account_pay_type_id = request.env['account.account.type'].sudo().search(
                        [('name', 'ilike', 'Payable')])
                    if account_rec_type_id:
                        account_rec_id = request.env['account.account'].sudo().search(
                            [('user_type_id', '=', account_rec_type_id.id)], limit=1)

                    if account_pay_type_id:
                        account_pay_id = request.env['account.account'].sudo().search(
                            [('user_type_id', '=', account_pay_type_id.id)], limit=1)
                    partner_id = request.env['res.partner'].sudo().search([('email', '=', post.get('inputEmail'))], limit=1,
                                                                          order="id desc")
                    print("\n\n\n\n=======cmpny=========",post.get('inputCompany'));
                    print("\n\n\n\n=======inputVat=======", post.get('inputVat'));
                    partner_id.write({'name': name,
                                          'student_company': post.get('inputCompany') if post.get('inputCompany') else '',
                                          'email': post.get('inputEmail') if post.get('inputEmail') else '',
                                          'vat_no_comp': post.get('inputVat') if post.get('inputVat') else '',
                                          'idpassport': post.get('inputID_PassportNo.') if post.get(
                                              'inputID_PassportNo.') else '',
                                          'cq_password': post.get('inputPassword') if post.get('inputPassword') else '',
                                          'mobile': post.get('inputContactNumber') if post.get(
                                              'inputContactNumber') else '',
                                          'street': post.get('inputStreet') if post.get('inputStreet') else '',
                                          'street2': post.get('inputStreet2') if post.get('inputStreet2') else '',
                                          'city': post.get('inputCity') if post.get('inputCity') else '',
                                          'country_id': int(post.get('country_id')) if post.get('country_id') else '',
                                          'state_id': int(post.get('inputState')) if post.get('inputState') else '',
                                          'zip': post.get('inputZip') if post.get('inputZip') else '',
                                          'findout': post.get('inputFindout') if post.get('inputFindout') else '',
                                          'prof_body_id': post.get('inputId') if post.get('inputId') else '',
                                          'property_account_receivable_id': account_rec_id.id,
                                          'property_account_payable_id': account_pay_id.id,
                                          'dob': post.get('inputDOB') if post.get('inputDOB') else ''})


                    if sale_order_id.quote_type == 'enrolment':
                        if sale_order_id.affiliation == '2':
                            if (sale_order_id.invoice_status == 'invoiced' or sale_order_id.invoice_count >= 1):
                                return request.render('cfo_snr_jnr.fully_invoiced')
                            else:
                                request.session['discount_id'] = ''
                                request.session['discount_add'] = ''
                                request.session['sale_order'] = sale_order_id.id if sale_order_id else ''
                                request.session['do_invoice'] = 'yes' if post.get('do_invoice') == 'Yes' else 'no'
                                sale_order_id.write({'diposit_selected': 100})
                                return request.redirect('/thank-you')
                        else:
                            request.session['discount_id'] = ''
                            request.session['discount_add'] = ''
                            request.session['sale_order'] = ''
                            request.session['do_invoice'] = ''

                        return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                                        'product_tot': round(product_tot,
                                                                                                             2),
                                                                                        'grand_tot': round(grand_tot, 2),
                                                                                        'sale_order_id': sale_order_id if sale_order_id else False,
                                                                                        'mandate_link': 'mandate_link_find',
                                                                                        'page_confirm': 'yes' if sale_order_id.affiliation in ['1','2'] else 'no',
                                                                                        'bank_detail': True if sale_order_id.affiliation in ['1','2'] else False,
                                                                                        'uuid': post.get('uuid'),
                                                                                        'uuid2':post.get('uuid2') if post.get('uuid2') else False,
                                                                                        })
                    if sale_order_id.quote_type == 'freequote':
                            if sale_order_id.affiliation == '2':
                                if (sale_order_id.invoice_status == 'invoiced' or sale_order_id.invoice_count >= 1):
                                    return request.render('cfo_snr_jnr.fully_invoiced')
                                else:
                                    request.session['discount_id'] = ''
                                    request.session['discount_add'] = ''
                                    request.session['sale_order'] = sale_order_id.id if sale_order_id else ''
                                    request.session['do_invoice'] = 'yes' if post.get('do_invoice') == 'Yes' else 'no'
                                    sale_order_id.write({'diposit_selected': 100})
                                    return request.redirect('/thank-you')
                            else:
                                request.session['discount_id'] = ''
                                request.session['discount_add'] = ''
                                request.session['sale_order'] = ''
                                request.session['do_invoice'] = ''

                            return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                                        'product_tot': round(product_tot,
                                                                                                             2),
                                                                                        'grand_tot': round(grand_tot, 2),
                                                                                        'sale_order_id': sale_order_id if sale_order_id else False,
                                                                                        'mandate_link': 'mandate_link_find',
                                                                                        'page_confirm':  'yes' if sale_order_id.affiliation == '1' else 'no',
                                                                                        'bank_detail': True if sale_order_id.affiliation == '1' else False,
                                                                                        'uuid': post.get('uuid'),
                                                                                        'uuid2': post.get('uuid2') if post.get('uuid2') else False,
                                                                                        })



        sale_order_id = False
        display_btn = request.session['reg_enrol_btn'] if request.session.get('reg_enrol_btn') else False
        product_ids = request.session['product_id'] if request.session.get('product_id') else ''
        reg_and_enrol = request.session['reg_and_enrol'] if request.session.get('reg_and_enrol') else ''
        # user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        discount_id = request.session['discount_id'] if request.session.get('discount_id') else ''
        discount_add = request.session['discount_add'] if request.session.get('discount_add') else 0
        event_tickets = request.session['event_id'] if request.session.get('event_id') else ''
        sale_obj = request.env['sale.order'].sudo()
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        order_line = []
        warehouse_id = False
        if user_select and user_select.get('campus'):
            campus_id = request.env['res.partner'].sudo().search([('id', '=', user_select.get('campus'))])
            warehouse_id = request.env['stock.warehouse'].sudo().search([('name', '=', campus_id.name)])
        for each_event_ticket in event_tickets:
            event_ticket = request.env['event.event.ticket'].sudo().search(
                [('id', '=', int(event_tickets[each_event_ticket]))])
            event_full_name = False
            if event_ticket and event_ticket.event_id:
                if event_ticket.event_id.event_course_code:
                    event_full_name = event_ticket.event_id.event_course_code + " - " + event_ticket.event_id.name + " - " + event_ticket.product_id.name
                else:
                    event_full_name = event_ticket.event_id.name + " - " + event_ticket.product_id.name
            order_line.append([0, 0, {'product_id': event_ticket.product_id.id,
                                      'event_id': event_ticket.event_id.id if event_ticket.product_id.event_ok else '',
                                      'event_type_id': event_ticket.product_id.event_type_id.id if event_ticket.product_id.event_type_id else '',
                                      'event_ticket_id': event_ticket.id if event_ticket.event_id else '',
                                      'name': event_full_name,
                                      'product_uom_qty': 1.0,
                                      'product_uom': 1.0,
                                      'price_unit': event_ticket.price,
                                      'discount': float(discount_add) if discount_add else 0}])

        for each_product in product_ids:
            product_id = request.env['product.product'].sudo().search([('id', '=', int(product_ids[each_product]))])
            order_line.append([0, 0, {'product_id': product_id.id,
                                      'product_uom_qty': 1.0,
                                      'product_uom': 1,
                                      'price_unit': product_id.lst_price}])
        if post:
            print("\n\n\n\n\n================post==========",post)
            _logger.info("\n\n\n post==========",post)
            if post.get('register_and_enrollment'):
                account_rec_id = False
                account_pay_id = False
                name = False
                res_partner_obj = request.env['res.partner'].sudo()
                if post.get('inputFirstName'):
                    name = post.get('inputFirstName')
                else:
                    name += ''
                if post.get('inputLastName'):
                    name += ' ' + post.get('inputLastName')

                account_rec_type_id = request.env['account.account.type'].sudo().search(
                    [('name', 'ilike', 'Receivable')])
                account_pay_type_id = request.env['account.account.type'].sudo().search(
                    [('name', 'ilike', 'Payable')])
                if account_rec_type_id:
                    account_rec_id = request.env['account.account'].sudo().search(
                        [('user_type_id', '=', account_rec_type_id.id)], limit=1)

                if account_pay_type_id:
                    account_pay_id = request.env['account.account'].sudo().search(
                        [('user_type_id', '=', account_pay_type_id.id)], limit=1)

                partner_id = request.env['res.partner'].sudo().search([('email', '=', post.get('inputEmail'))], limit=1,
                                                                      order="id desc")
                request.session['do_invoice'] = 'yes' if post.get('do_invoice') == 'Yes' else 'no'
                if not partner_id:
                    partner_id = res_partner_obj.create({'name': name,
                                            'student_company': post.get('inputCompany') if post.get(
                                                'inputCompany') else '',
                                            'email': post.get('inputEmail') if post.get('inputEmail') else '',
                                            'vat_no_comp': post.get('inputVat') if post.get('inputVat') else '',
                                            'idpassport': post.get('inputID_PassportNo.') if post.get(
                                                'inputID_PassportNo.') else '',
                                            'cq_password': post.get('inputPassword') if post.get(
                                                'inputPassword') else '',
                                            'mobile': post.get('inputContactNumber') if post.get(
                                                'inputContactNumber') else '',
                                            'street': post.get('inputStreet') if post.get('inputStreet') else '',
                                            'street2': post.get('inputStreet2') if post.get('inputStreet2') else '',
                                            'city': post.get('inputCity') if post.get('inputCity') else '',
                                            'country_id': int(post.get('country_id')) if post.get('country_id') else '',
                                            'state_id': int(post.get('inputState')) if post.get('inputState') else '',
                                            'zip': post.get('inputZip') if post.get('inputZip') else '',
                                            'findout': post.get('inputFindout') if post.get('inputFindout') else '',
                                            'prof_body_id': post.get('inputId') if post.get('inputId') else '',
                                            'property_account_receivable_id': account_rec_id.id,
                                            'property_account_payable_id': account_pay_id.id})
                else:
                    partner_id.write({'name': name,
                                      'student_company': post.get('inputCompany') if post.get('inputCompany') else '',
                                      'email': post.get('inputEmail') if post.get('inputEmail') else '',
                                      'vat_no_comp': post.get('inputVat') if post.get('inputVat') else '',
                                      'idpassport': post.get('inputID_PassportNo.') if post.get(
                                          'inputID_PassportNo.') else '',
                                      'cq_password': post.get('inputPassword') if post.get('inputPassword') else '',
                                      'mobile': post.get('inputContactNumber') if post.get(
                                          'inputContactNumber') else '',
                                      'street': post.get('inputStreet') if post.get('inputStreet') else '',
                                      'street2': post.get('inputStreet2') if post.get('inputStreet2') else '',
                                      'city': post.get('inputCity') if post.get('inputCity') else '',
                                      'country_id': int(post.get('country_id')) if post.get('country_id') else '',
                                      'state_id': int(post.get('inputState')) if post.get('inputState') else '',
                                      'zip': post.get('inputZip') if post.get('inputZip') else '',
                                      'findout': post.get('inputFindout') if post.get('inputFindout') else '',
                                      'prof_body_id': post.get('inputId') if post.get('inputId') else '',
                                      'property_account_receivable_id': account_rec_id.id,
                                      'property_account_payable_id': account_pay_id.id})

                if partner_id:
                    sale_order_id = sale_obj.sudo().create({'partner_id': partner_id.id,
                                                     'affiliation': '1' if user_select.get(
                                                         'self_or_company') and user_select.get(
                                                         'self_or_company') == 'self' else '2',
                                                     'campus': user_select['campus'] if user_select.get(
                                                         'campus') else '',
                                                     'prof_body': user_select.get('Select Prof Body') if user_select.get(
                                                         'Select Prof Body') else False,
                                                     'quote_type': 'enrolment',
                                                     'semester_id': user_select.get('Semester') if user_select.get(
                                                         'Semester') else False,
                                                     'warehouse_id': warehouse_id.id,
                                                     'discount_type_ids': [(6, 0, [each for each in discount_id])],
                                                     'order_line': order_line})
                    # sale_order_id.write({'name': sale_order_id.name + 'WEB'})
                    quote_name = "SO{0}WEB".format(str(sale_order_id.id).zfill(3))
                    m = hashlib.md5(quote_name.encode())
                    decoded_quote_name = m.hexdigest()
                    config_para = request.env['ir.config_parameter'].sudo().search([('key', 'ilike', 'web.base.url')])
                    if config_para:
                        link = config_para.value + "/registration_form/" + decoded_quote_name
                        sale_order_id.write(
                            {'name': quote_name, 'link_portal': link, 'debit_link': decoded_quote_name})
                    else:
                        sale_order_id.write({'name': quote_name})
                    for each_line in sale_order_id.order_line:
                        if each_line.event_id:
                            each_line.discount = float(discount_add) if discount_add else 0

                if user_select:
                    if user_select['self_or_company'] == 'cmp_sponosored':
                        request.session['discount_id'] = ''
                        request.session['discount_add'] = ''
                        request.session['sale_order'] = sale_order_id.id if sale_order_id else ''
                        sale_order_id.write({'diposit_selected': 100})
                        return request.redirect('/thank-you')
                    else:
                        request.session['discount_id'] = ''
                        request.session['discount_add'] = ''
                        request.session['sale_order'] = ''
                        request.session['do_invoice'] = ''
                        
                return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                                'product_tot': request.session[
                                                                                    'product_tot'],
                                                                                'grand_tot': request.session[
                                                                                    'grand_tot'],
                                                                                'page_confirm': 'yes',
                                                                                'sale_order': sale_order_id.id,
                                                                                'sale_order_id':sale_order_id if sale_order_id else False,
                                                                                'register_enrol': True,
                                                                                'uuid': post.get('uuid') if post.get('uuid') else False,
                                                                                 })
            else:
                if post.get('email'):
                    account_rec_id = False
                    account_pay_id = False
                    name = False
                    res_partner_obj = request.env['res.partner'].sudo()
                    if post.get('firstName'):
                        name = post.get('firstName')
                    else:
                        name += ''
                    if post.get('lastName'):
                        name += ' ' + post.get('lastName')

                    account_rec_type_id = request.env['account.account.type'].sudo().search(
                        [('name', 'ilike', 'Receivable')])
                    account_pay_type_id = request.env['account.account.type'].sudo().search(
                        [('name', 'ilike', 'Payable')])
                    if account_rec_type_id:
                        account_rec_id = request.env['account.account'].sudo().search(
                            [('user_type_id', '=', account_rec_type_id.id)], limit=1)

                    if account_pay_type_id:
                        account_pay_id = request.env['account.account'].sudo().search(
                            [('user_type_id', '=', account_pay_type_id.id)], limit=1)
                    partner_detail = request.env['res.partner'].sudo().search([('email', '=', post.get('email'))],
                                                                              limit=1)

                    if not partner_detail:
                        partner_detail = request.env['res.partner'].sudo().create({'name': name,
                                                                                   'email': post['email'] if post.get(
                                                                                       'email') else '',
                                                                                   'student_company': post.get('inputCompany') if post.get('inputCompany') else '',
                                                                                   'vat_no_comp': post.get('inputVat') if post.get('inputVat') else '',
                                                                                   'mobile': post['phoneNumber'] if post.get(
                                                                                       'phoneNumber') else '',
                                                                                   'property_account_receivable_id': account_rec_type_id.id,
                                                                                   'property_account_payable_id': account_pay_type_id.id})
                    else:
                        partner_detail.write({'name': name,
                                              'email': post['email'] if post.get(
                                                  'email') else '',
                                              'student_company': post.get('inputCompany') if post.get('inputCompany') else '',
                                              'vat_no_comp': post.get('inputVat') if post.get('inputVat') else '',
                                              'mobile': post[
                                                  'phoneNumber'] if post.get(
                                                  'phoneNumber') else '',
                                              'property_account_receivable_id': account_rec_type_id.id,
                                              'property_account_payable_id': account_pay_type_id.id})

                    if partner_detail:
                        sale_order_id = sale_obj.create({'partner_id': partner_detail.id,
                                                         'affiliation': '1' if user_select and user_select.get(
                                                             'self_or_company') and user_select.get(
                                                             'self_or_company') == 'self' else '2',
                                                         'campus': user_select[
                                                             'campus'] if user_select and user_select.get(
                                                             'campus') else '',
                                                         'prof_body': user_select[
                                                             'Select Prof Body'] if user_select and user_select.get(
                                                             'Select Prof Body') else '',
                                                         'quote_type': 'enrolment' if display_btn else 'freequote',
                                                         'semester_id': user_select[
                                                             'Semester'] if user_select and user_select.get(
                                                             'Semester') else '',
                                                         'warehouse_id': warehouse_id.id if warehouse_id else False,
                                                         'discount_type_ids': [(6, 0, [each for each in discount_id])],
                                                         'order_line': order_line})
                        # quote_name = sale_order_id.name + 'WEB'
                        quote_name = "SO{0}WEB".format(str(sale_order_id.id).zfill(3))
                        m = hashlib.md5(quote_name.encode())
                        decoded_quote_name = m.hexdigest()
                        config_para = request.env['ir.config_parameter'].sudo().search(
                            [('key', 'ilike', 'web.base.url')])
                        if config_para:
                            link = config_para.value + "/registration_form/" + decoded_quote_name
                            sale_order_id.write({'name': quote_name, 'link_portal': link,
                                                 'debit_link': decoded_quote_name})
                        else:
                            sale_order_id.write({'name': quote_name})
                        for each_line in sale_order_id.order_line:
                            if each_line.event_id:
                                each_line.discount = float(discount_add) if discount_add else 0
                    # else:
                    #     account_rec_type_id = request.env['account.account.type'].sudo().search(
                    #         [('name', 'ilike', 'Receivable')])
                    #     account_pay_type_id = request.env['account.account.type'].sudo().search(
                    #         [('name', 'ilike', 'Payable')])
                    #     if account_rec_type_id:
                    #         account_id = request.env['account.account'].sudo().search(
                    #             [('user_type_id', '=', account_rec_type_id.id)], limit=1)
                    #
                    #     if account_pay_type_id:
                    #         account_id = request.env['account.account'].sudo().search(
                    #             [('user_type_id', '=', account_pay_type_id.id)], limit=1)
                    #
                    #         partner_id = request.env['res.partner'].sudo().create({'name': post['firstName'] + ' ' +
                    #                                                                        post['lastName'] if post.get(
                    #             'firstName') and post.get('lastName') else '',
                    #                                                                'email': post['email'] if post.get(
                    #                                                                    'email') else '',
                    #                                                                'mobile': post[
                    #                                                                    'phoneNumber'] if post.get(
                    #                                                                    'phoneNumber') else '',
                    #                                                                'property_account_receivable_id': account_rec_type_id.id,
                    #                                                                'property_account_payable_id': account_pay_type_id.id})
                    #
                    #     sale_order_id = sale_obj.create({'partner_id': partner_id.id,
                    #                                      'campus': user_select['campus'] if user_select.get(
                    #                                          'campus') else '',
                    #                                      'prof_body': user_select[
                    #                                          'Select Prof Body'] if user_select.get(
                    #                                          'Select Prof Body') else '',
                    #                                      'quote_type': 'enrolment',
                    #                                      'semester_id': user_select['Semester'] if user_select.get(
                    #                                          'Semester') else '',
                    #                                      'warehouse_id': warehouse_id.id,
                    #                                      'discount_type_ids': [(6, 0, [each for each in discount_id])],
                    #                                      'order_line': order_line})
                    #     quote_name = sale_order_id.name + 'WEB'
                    #     m = hashlib.md5()
                    #     m.update(quote_name.encode())
                    #     decoded_quote_name = m.hexdigest()
                    #     config_para = request.env['ir.config_parameter'].sudo().search(
                    #         [('key', 'ilike', 'web.base.url')])
                    #     if config_para:
                    #
                    #         link = config_para.value + "/debitorder/" + decoded_quote_name
                    #         # link = "http://enrolments.charterquest.co.za/debitordermandate/" + decoded_quote_name
                    #         sale_order_id.write(
                    #             {'name': quote_name, 'debit_order_mandate_link': link, 'debit_link': link})
                    #     else:
                    #         sale_order_id.write({'name': quote_name})
                    #     for each_line in sale_order_id.order_line:
                    #         if each_line.event_id:
                    #             each_line.discount = float(discount_add) if discount_add else 0
                    if user_select:
                        if user_select['self_or_company'] == 'cmp_sponosored':
                            request.session['discount_id'] = ''
                            request.session['discount_add'] = ''
                            request.session['sale_order'] = sale_order_id.id if sale_order_id else ''
                            request.session['do_invoice'] = 'yes' if post.get('do_invoice') == 'Yes' else 'no'
                            sale_order_id.write({'diposit_selected': 100})
                            return request.redirect('/page/thank-you')
                        else:
                            request.session['discount_id'] = ''
                            request.session['discount_add'] = ''
                            request.session['sale_order'] = ''
                            request.session['do_invoice'] = ''
                    return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                                    'product_tot': request.session[
                                                                                        'product_tot'],
                                                                                    'grand_tot': request.session[
                                                                                        'grand_tot'],
                                                                                    'sale_order': sale_order_id.id if sale_order_id else '',
                                                                                    'sale_order_id': sale_order_id if sale_order_id else False,
                                                                                    'invoice_generate': 'yes',
                                                                                    'page_confirm': 'yes' if sale_order_id.affiliation == 1 else 'no',
                                                                                    'bank_detail': True if sale_order_id.affiliation == 1 else False,
                                                                                'register_enrol': False})

    @http.route(['/page/thank-you'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def page_thank_you(self, **post):
        # request.session['']
        attchment_list = []
        sale_order = False
        sale_order_id = False
        invoice_id = False
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        event_tickets = request.session['event_id'] if request.session.get('event_id') else ''
        mail_obj = request.env['mail.mail'].sudo()
        invoice_obj = request.env['account.invoice'].sudo()
        invoice_line = []
        if post.get('sale_order'):
            sale_order = post.get('sale_order')
        if request.session.get('sale_order'):
            sale_order = request.session['sale_order']
        if post.get('sale_order_id'):
            sale_order = post.get('sale_order_id')

        event_tickets = request.session['event_id'] if request.session.get('event_id') else ''

        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))

        if sale_order_id:
            if post.get('sale_order') or post.get('sale_order_id') or request.session.get('sale_order') :
                if not post.get('eft'):
                    sale_order_id.write(
                        {'diposit_selected': int(post.get('inputPaypercentage')) if post.get('inputPaypercentage') else 0,
                         'due_amount':float(post.get('inputTotalDue')) if post.get('inputTotalDue') else 0,
                         'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                         'out_standing_balance_incl_vat': post.get('inputtotalandInterest') if post.get(
                             'inputtotalandInterest') else 0,
                         'monthly_amount': post.get('inputpaymentpermonth') if post.get('inputpaymentpermonth') else 0,
                         'outstanding_amount': post.get('inputOutstanding') if post.get('inputOutstanding') else 0,
                         'interest_amount': post.get('inputInterest') if post.get('inputInterest') else 0
                         })
                    if request.session.get('do_invoice') == 'yes':

                        for each_order_line in sale_order_id.order_line:
                            invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                                                        'name': each_order_line.name,
                                                        'quantity': 1.0,
                                                        'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
                                                        'invoice_line_tax_ids': [
                                                            (6, 0, [each_tax.id for each_tax in each_order_line.tax_id])],
                                                        'price_unit': each_order_line.price_unit,
                                                        'discount': each_order_line.discount}])
                        invoice_id = invoice_obj.create({'partner_id': sale_order_id.partner_id.id,
                                                         'campus': sale_order_id.campus.id,
                                                         'prof_body': sale_order_id.prof_body.id,
                                                         'sale_order_id': sale_order_id.id,
                                                         'semester_id': sale_order_id.semester_id.id,
                                                         'invoice_line_ids': invoice_line,
                                                         'residual': sale_order_id.out_standing_balance_incl_vat,
                                                         })
                        invoice_id.action_invoice_open()
            # sale_order_id.write({'state': 'sale'})
            # sale_order_id.action_confirm()

            # stock_warehouse = request.env['stock.warehouse'].sudo().search([('name', '=', sale_order_id.campus.name)])
            # stock_location = request.env['stock.location'].sudo().search(
            #     [('parent_left', 'in', [sale_order_id.warehouse_id.id])])
            picking_type_id = request.env['stock.picking.type'].sudo().search([('name', '=', 'Delivery Orders'),
                                                                               ('warehouse_id', '=', sale_order_id.warehouse_id.id)])
            line_list = []
            for each_event_ticket in event_tickets:
                event_ticket = request.env['event.event.ticket'].sudo().search(
                    [('id', '=', int(event_tickets[each_event_ticket]))])
                book_combination = request.env['course.material'].sudo().search(
                    [('event_id', '=', event_ticket.event_id.id),
                     ('study_option_id', '=', event_ticket.product_id.id)])
                if book_combination:
                    for each_combination in book_combination.material_ids:
                        line_list.append((0, 0, {
                            'name': 'move out',
                            'product_id': each_combination.material_product_id.id,
                            'product_uom': each_combination.material_product_id.uom_id.id,
                            'product_uom_qty': 1,
                            'procure_method': 'make_to_stock',
                            'location_id': picking_type_id.default_location_src_id.id,
                            'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                        }))
            customer_picking = request.env['stock.picking'].sudo().create({
                'partner_id': sale_order_id.partner_id.id,
                'campus_id': sale_order_id.campus.id,
                'prof_body_id': sale_order_id.prof_body.id,
                'sale_order_id': sale_order_id.id,
                'sale_id': sale_order_id.id,
                'semester': sale_order_id.semester_id.id,
                'delivery_order_source': sale_order_id.quote_type,
                'location_id': picking_type_id.default_location_src_id.id,
                'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                'picking_type_id': picking_type_id.id,
                'move_lines': line_list
            })
            customer_picking.sale_id = sale_order_id.id
            # sale_order_id.write({'picking_ids', (0,0, [])})
            # customer_move = request.env['stock.move'].create((0,0,{
            #     'name': 'move out',
            #     'product_id': each_combination.material_product_id.id,
            #     'product_uom': each_combination.material_product_id.uom_id.id,
            #     'product_uom_qty': 1,
            #     'procure_method': 'make_to_order',
            #     'location_id': each_combination.material_product_id.property_stock_production.id,
            #     'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
            #     'picking_id': customer_picking.id,
            # })

            event_tickets = request.session['event_id'] if request.session.get('event_id') else ''
            event_count = request.session['event_count'] if request.session.get('event_count') else 0
            discount_detail_list = []
            email_discount_list = []
            user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
            today_date = datetime.today()
            str_today_date = datetime.strftime(today_date, '%Y-%m-%d')
            max_discount_detail = 0
            if user_select:
                discount_detail = request.env['event.discount'].sudo().search([('event_type_id', '=', int(
                    user_select['Select Prof Body']) if user_select.get('Select Prof Body') else '')])
                for each_discount in discount_detail:
                    if each_discount not in discount_detail_list:
                        discount_detail_list.append(each_discount)
                max_discount_detail = request.env['event.max.discount'].sudo().search([('date', '=', str_today_date),
                                                                                       ('prof_body', '=',
                                                                                        int(user_select[
                                                                                                'Select Prof Body']) if user_select else '')],
                                                                                      limit=1, order="id desc")

            template_id = request.env['mail.template'].sudo().search([('name', '=', 'Paid Fees Email')])
            if template_id:
                sale_order_id = sale_order_id.sudo()
                if sale_order_id.affiliation == '1':
                    pdf_data_enroll = request.env.ref('event_price_kt.report_sale_enrollment').sudo().render_qweb_pdf(
                        sale_order_id.id)
                    enroll_file_name = "Pro-Forma " + sale_order_id.name
                    if pdf_data_enroll:
                        pdfvals = {'name': enroll_file_name,
                                   'db_datas': base64.b64encode(pdf_data_enroll[0]),
                                   'datas': base64.b64encode(pdf_data_enroll[0]),
                                   'datas_fname': enroll_file_name + ".pdf",
                                   'res_model': 'sale.order',
                                   'type': 'binary'}
                        pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                        attchment_list.append(pdf_create)
                    # cr, uid, context = request.cr, request.uid, request.context
                    # payment_acquire = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payu')])
                    # transactionDetails = {}
                    # transactionDetails['store'] = {}
                    # transactionDetails['store']['soapUsername'] = payment_acquire.payu_api_username
                    # transactionDetails['store']['soapPassword'] = payment_acquire.payu_api_password
                    # transactionDetails['store']['safekey'] = payment_acquire.payu_seller_account
                    # transactionDetails['store']['environment'] = payment_acquire.environment
                    # transactionDetails['additionalInformation'] = {}
                    # transactionDetails['additionalInformation']['payUReference'] = post['PayUReference']
                    # try:
                    #     result = PayuController.payuMeaGetTransactionApiCall('', transactionDetails)
                    #     payment_transation_id = request.env['payment.transaction'].sudo().search(
                    #         [('reference', '=', result['merchantReference'])])
                    #     payu_response = {}
                    #     if result:
                    #         payu_response['TRANSACTION_STATUS'] = result['transactionState']
                    #         # payu_response['SUCCESSFUL'] = result['successful']
                    #         payu_response[
                    #             'AMOUNT'] = payment_transation_id.amount * 100 if payment_transation_id else 0.00
                    #         payu_response['CURRENCYCODE'] = result['basket']['currencyCode']
                    #         payu_response['PAYUREFERENCE'] = result['payUReference']
                    #         payu_response['REFERENCE'] = result['merchantReference']
                    #         payu_response['RESULTMESSAGE'] = result['resultMessage']
                    #     response_state = request.env['payment.transaction'].sudo().form_feedback(payu_response, 'payu')
                    #     sale_order_id = request.env['sale.order'].sudo().search(
                    #         [('name', '=', result['merchantReference'])])
                    #     sale_order_data = sale_order_id
                    #     request.session['sale_last_order_id'] = sale_order_id.id
                    #
                    #     tx_id = request.env['payment.transaction'].sudo().search(
                    #         [('reference', '=', result['merchantReference'])])
                    #     tx = tx_id
                    #     if not sale_order_id or (sale_order_id.amount_total and not tx):
                    #         return request.redirect('/shop')
                    #     if (not sale_order_id.amount_total and not tx) or tx.state in ['pending']:
                    #         if sale_order_id.state in ['draft', 'sent']:
                    #             if (not sale_order_id.amount_total and not tx):
                    #                 sale_order_id.action_button_confirm()
                    #             email_act = sale_order_id.action_quotation_send()
                    #     elif tx and tx.state == 'cancel':
                    #         sale_order_id.action_cancel()
                    #     elif tx and (tx.state == 'draft' or tx.state == 'sent' or tx.state == 'done'):
                    #         #             if result and payu_response['successful'] and payu_response['TRANSACTION_STATUS'] in ['SUCCESSFUL', 'PARTIAL_PAYMENT', 'OVER_PAYMENT']:
                    #         if result and payu_response['TRANSACTION_STATUS'] in ['SUCCESSFUL', 'PARTIAL_PAYMENT',
                    #                                                               'OVER_PAYMENT']:
                    #             transaction = tx.sudo().write(
                    #                 {'state': 'done', 'date_validate': datetime.now(),
                    #                  'acquirer_reference': result['payUReference']})
                    #             email_act = sale_order_id.action_quotation_send()
                    #             action_confirm_res = sale_order_id.action_confirm()
                    #             sale_order = sale_order_id.read([])


                    agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                    if agreement_id:
                        attchment_list.append(agreement_id)

                    if post.get('eft'):
                        banking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                        if banking_detail_id:
                            attchment_list.append(banking_detail_id)
                        body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                        body_html += "<br>"
                        body_html += "Dear " + sale_order_id.partner_id.name + ","
                        body_html += "<br><br>"
                        body_html += "Thank you for your Enrolment Application."
                        body_html += "<br><br>"
                        body_html += "Please find attached Invoice as well as copy of the Student Agreement you just accepted during enrolment."
                        body_html += "<br><br>"
                        body_html += "Your sponsor/company can pay using the Invoice no. as reference and return proof of payment to: accounts@charterquest.co.za"
                        body_html += " to process your enrolment. You can email accounts should you wish to make special payment arrangements."
                        body_html += "<br><br>"
                        body_html += "We look forward to seeing	you	during our course and helping you, in achieving	a 1st Time Pass!"
                        body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Institute<br> CENTRAL CONTACT INFORMATION:<br>"
                        body_html += "Tel: +27 (0)11 234 9223 [SA & Intl]<br> Tel: +27 (0)11 234 9238 [SA & Intl]<br> Tel: 0861 131 137 [SA ONLY]<br> Fax: 086 218 8713 [SA ONLY]<br>"
                        body_html += "Email:enquiries@charterquest.co.za<br><br/> <div>"
                        mail_values = {
                            'email_from': template_id.email_from,
                            'reply_to': template_id.reply_to,
                            'email_to': sale_order_id.partner_id.email if sale_order_id.partner_id.email else '',
                            'email_cc': 'enquiries@charterquest.co.za; accounts@charterquest.co.za; cqops@charterquest.co.za',
                            'subject': "Charterquest FreeQuote/Enrolment  " + sale_order_id.name,
                            'body_html': body_html,
                            'notification': True,
                            'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                            'auto_delete': False,
                        }
                        msg_id = mail_obj.sudo().create(mail_values)
                        msg_id.sudo().send()
                    else:
                        self_spo_free_quote = request.env.ref('cfo_snr_jnr.self_sponsored_free_quote_email_template')
                        ctx = {
                                'model': 'sale.order',
                                'res_id': sale_order_id.id,
                                'use_template': True,
                                'template_id': self_spo_free_quote.id,
                                'mark_so_as_sent': True,
                                'force_email': True
                            }
                        mail_compose_id = request.env['mail.compose.message'].sudo().generate_email_for_composer(self_spo_free_quote.id,sale_order_id.id)
                        bodies = request.env['mail.template'].render_template(self_spo_free_quote, 'sale.order', sale_order_id.id, post_process=True)
                        mail_compose_id.update({'email_to': sale_order_id.partner_id.email})
                        mail_values = {
                            'email_from': self_spo_free_quote.sudo().email_from,
                            'reply_to': self_spo_free_quote.sudo().reply_to,
                            'email_to': mail_compose_id.get('email_to'),
                            'email_cc': self_spo_free_quote.sudo().email_cc,
                            'subject': mail_compose_id.get('subject'),
                            'body_html': mail_compose_id.get('body'),
                            'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                            'auto_delete': self_spo_free_quote.sudo().auto_delete,
                        }

                        msg_id = mail_obj.sudo().create(mail_values)
                        msg_id.sudo().send()
                    if user_select and user_select.get('self_or_company') == 'cmp_sponosored':
                        return request.sudo().render('cfo_snr_jnr.enrolment_process_page_thankyou',
                                              {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                                  'self_or_company') else ''})
                elif sale_order_id.affiliation == '2':
                    if request.session.get('sale_order') and request.session.get('do_invoice') == 'yes':
                        pdf_data = request.env.ref('event_price_kt.report_enrollment_invoice').sudo().render_qweb_pdf(
                            invoice_id.id)
                        pdf_data_statement_invoice = request.env.ref(
                            'event_price_kt.report_statement_enrollment').sudo().render_qweb_pdf(invoice_id.id)

                        if pdf_data:
                            pdfvals = {'name': 'Invoice',
                                       'db_datas': base64.b64encode(pdf_data[0]),
                                       'datas': base64.b64encode(pdf_data[0]),
                                       'datas_fname': 'Invoice.pdf',
                                       'res_model': 'account.invoice',
                                       'type': 'binary'}
                            pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                            attchment_list.append(pdf_create)

                        if pdf_data_statement_invoice:
                            pdfvals = {'name': 'Enrolment Statement',
                                       'db_datas': base64.b64encode(pdf_data_statement_invoice[0]),
                                       'datas': base64.b64encode(pdf_data_statement_invoice[0]),
                                       'datas_fname': 'Enrolment Statement.pdf',
                                       'res_model': 'account.invoice',
                                       'type': 'binary'}
                            pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                            attchment_list.append(pdf_create)

                        agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                        if agreement_id:
                            attchment_list.append(agreement_id)

                        banking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                        if banking_detail_id:
                            attchment_list.append(banking_detail_id)
                        body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                        body_html += "<br>"
                        body_html += "Dear " + sale_order_id.partner_id.name + ","
                        body_html += "<br><br>"
                        body_html += "Thank you for your Enrolment Application."
                        body_html += "<br><br>"
                        body_html += "Please find attached Invoice as well as copy of the Student Agreement you just accepted during enrolment."
                        body_html += "<br><br>"
                        body_html += "Your sponsor/company can pay using the Invoice no. as reference and return proof of payment to: accounts@charterquest.co.za"
                        body_html += " to process your enrolment. You can email accounts should you wish to make special payment arrangements."
                        body_html += "<br><br>"
                        body_html += "We look forward to seeing	you	during our course and helping you, in achieving	a 1st Time Pass!"
                        body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Institute<br> CENTRAL CONTACT INFORMATION:<br>"
                        body_html += "Tel: +27 (0)11 234 9223 [SA & Intl]<br> Tel: +27 (0)11 234 9238 [SA & Intl]<br> Tel: 0861 131 137 [SA ONLY]<br> Fax: 086 218 8713 [SA ONLY]<br>"
                        body_html += "Email:enquiries@charterquest.co.za<br><br/> <div>"
                        mail_values = {
                            'email_from': template_id.email_from,
                            'reply_to': template_id.reply_to,
                            'email_to': sale_order_id.partner_id.email if sale_order_id.partner_id.email else '',
                            'subject': "Charterquest FreeQuote/Enrolment  " + sale_order_id.name,
                            'body_html': body_html,
                            'notification': True,
                            'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                            'auto_delete': False,
                        }
                        msg_id = mail_obj.sudo().create(mail_values)
                        msg_id.sudo().send()
                        if user_select.get('self_or_company') == 'cmp_sponosored':
                            return request.render('cfo_snr_jnr.enrolment_process_page_thankyou',
                                                  {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                                      'self_or_company') else ''})

                    if request.session.get('sale_order') and request.session.get('do_invoice') == 'no':
                        com_spo_free_quote = request.env.ref('cfo_snr_jnr.company_sponsored_free_quote_email_template')
                        pdf_data_enroll = request.env.ref(
                            'event_price_kt.report_sale_enrollment').sudo().render_qweb_pdf(
                            sale_order_id.id)
                        enroll_file_name = "Pro-Forma " + sale_order_id.name
                        if pdf_data_enroll:
                            pdfvals = {'name': enroll_file_name,
                                       'db_datas': base64.b64encode(pdf_data_enroll[0]),
                                       'datas': base64.b64encode(pdf_data_enroll[0]),
                                       'datas_fname': enroll_file_name + '.pdf',
                                       'res_model': 'sale.order',
                                       'type': 'binary'}
                            pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                            attchment_list.append(pdf_create)

                        agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')

                        if agreement_id:
                            attchment_list.append(agreement_id)
#                         body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
#                         body_html += "<br>"
#                         body_html += "Dear " + sale_order_id.partner_id.name + ","
#                         body_html += "<br><br>"
#                         body_html += "Thank you for your course fee/price enquiry."
#                         body_html += "<br><br>"
#                         body_html += "Kindly review the attached and secure your place by:"
#                         body_html += "<br><br>"
#                         body_html += "<div>"
#                         body_html += "<a href='https://charterquest.odoo.com/registration_form' style='border-radius: 3px;display: inline-block;font-size: 14px;font-weight: 700;line-height: 24px;padding: 13px 35px 12px 35px;text-align: center;text-decoration: none !important;transition: opacity 0.2s ease-in;color: #fff;font-family: &quot;Open Sans&quot;,sans-serif;background-color: #ff0000;margin-right: 10px;margin-bottom: 10px;'>CONVERT TO INVOICE</a>"
#                         body_html += "<a href='https://charterquest.odoo.com/registration_form' style='border-radius: 3px;display: inline-block;font-size: 14px;font-weight: 700;line-height: 24px;padding: 13px 35px 12px 35px;text-align: center;text-decoration: none !important;transition: opacity 0.2s ease-in;color: #fff;font-family: &quot;Open Sans&quot;,sans-serif;background-color: #ff0000;margin-right: 10px;margin-bottom: 10px;'>PAY NOW</a>"
#                         body_html += "<a href='https://charterquest.odoo.com/registration_form' style='border-radius: 3px;display: inline-block;font-size: 14px;font-weight: 700;line-height: 24px;padding: 13px 35px 12px 35px;text-align: center;text-decoration: none !important;transition: opacity 0.2s ease-in;color: #fff;font-family: &quot;Open Sans&quot;,sans-serif;background-color: #ff0000;margin-right: 10px;margin-bottom: 10px;'>GET BANKING DETAILS & PAY LATER</a>"
#                         body_html += "</div>"
#                         body_html += "<br><br>"
#                         body_html += "We look forward to seeing you during our course and helping you, in achieving a 1st Time Pass!"
#                         body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Institute<br> CENTRAL CONTACT INFORMATION:<br>"
#                         body_html += "Tel: +27 (0)11 234 9223 [SA & Intl]<br> Tel: +27 (0)11 234 9238 [SA & Intl]<br> Tel: 0861 131 137 [SA ONLY]<br> Fax: 086 218 8713 [SA ONLY]<br>"
#                         body_html += "Email:enquiries@charterquest.co.za<br><br/> <div>"
#                         print ("\n\n\n------2222-->>>>>>>>>>>>",template_id.reply_to, template_id.email_from)
                        
                        ir_model_data = request.env['ir.model.data'].sudo()
                        try:
                            template_id = ir_model_data.get_object_reference('cfo_snr_jnr', 'company_sponsored_free_quote_email_template')[1]
                        except ValueError:
                            template_id = False
                       
                        ctx = {
                            'model': 'sale.order',
                            'res_id': sale_order_id.id,
                            'use_template': True,
                            'template_id': com_spo_free_quote.id,
                            'mark_so_as_sent': True,
                            'force_email': True
                        }
                        mail_compose_id = request.env['mail.compose.message'].sudo().generate_email_for_composer(com_spo_free_quote.id,sale_order_id.id)
                        bodies = request.env['mail.template'].render_template(com_spo_free_quote, 'sale.order', sale_order_id.id, post_process=True)
                        
                        mail_compose_id.update({'email_to': sale_order_id.partner_id.email})
                        mail_values = {
                            'email_from': com_spo_free_quote.sudo().email_from,
                            'reply_to': com_spo_free_quote.sudo().reply_to,
                            'email_to': mail_compose_id.get('email_to'),
                            'email_cc': com_spo_free_quote.sudo().email_cc,
                            'subject': mail_compose_id.get('subject'),
                            'body_html': mail_compose_id.get('body'),
                            'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                            'auto_delete': com_spo_free_quote.sudo().auto_delete,
                        }
                        msg_id = mail_obj.sudo().create(mail_values)
                        msg_id.sudo().send()
                        if user_select.get('self_or_company') == 'cmp_sponosored':
                            return request.render('cfo_snr_jnr.enrolment_process_page_thankyou',
                                                  {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                                      'self_or_company') else ''})

                # template_id.send_mail(sale_order_id.id, force_send=True)
        return request.render('cfo_snr_jnr.enrolment_process_page_thankyou')

    @http.route(['/pay/bank/thankyou'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def pay_bank_thankyou(self, **post):
        invoice_obj = request.env['account.invoice'].sudo()
        debit_order_obj = request.env['debit.order.details'].sudo()
        mail_obj = request.env['mail.mail'].sudo()
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        attchment_list = []
        invoice_line = []

        if post.get('sale_order'):
            sale_order = post.get('sale_order')
        if request.session.get('sale_order'):
            sale_order = request.session['sale_order']

        event_tickets = request.session['event_id'] if request.session.get('event_id') else ''
        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
        if sale_order_id:
            for each_order_line in sale_order_id.order_line:
                invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                                            'name': each_order_line.name,
                                            'quantity': 1.0,
                                            'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
                                            'invoice_line_tax_ids': [
                                                (6, 0, [each_tax.id for each_tax in each_order_line.tax_id])],
                                            'price_unit': each_order_line.price_unit,
                                            'discount': each_order_line.discount}])
            # invoice_id = invoice_obj.create({'partner_id': sale_order_id.partner_id.id,
            #                                  'campus': sale_order_id.campus.id,
            #                                  'prof_body': sale_order_id.prof_body.id,
            #                                  'sale_order_id': sale_order_id.id,
            #                                  'semester_id': sale_order_id.semester_id.id,
            #                                  'invoice_line_ids': invoice_line,
            #                                  'residual': sale_order_id.out_standing_balance_incl_vat,
            #                                  })
            # print ("\n\n\n\ninvoice",invoice_id)
            stock_warehouse = request.env['stock.warehouse'].sudo().search([('name', '=', sale_order_id.campus.name)])
            # stock_location = request.env['stock.location'].sudo().search(
            #     [('location_id', '=', sale_order_id.warehouse_id.id)])
            picking_type_id = request.env['stock.picking.type'].sudo().search([('name', '=', 'Delivery Orders'),
                                                                               ('warehouse_id', '=',
                                                                                sale_order_id.warehouse_id.id)])

            line_list = []
            for each_event_ticket in event_tickets:
                event_ticket = request.env['event.event.ticket'].sudo().search(
                    [('id', '=', int(event_tickets[each_event_ticket]))])
                book_combination = request.env['course.material'].sudo().search(
                    [('event_id', '=', event_ticket.event_id.id),
                     ('study_option_id', '=', event_ticket.product_id.id)])
                if book_combination:
                    for each_combination in book_combination.material_ids:
                        line_list.append((0, 0, {
                            'name': 'move out',
                            'product_id': each_combination.material_product_id.id,
                            'product_uom': each_combination.material_product_id.uom_id.id,
                            'product_uom_qty': 1,
                            'procure_method': 'make_to_stock',
                            'location_id': picking_type_id.id,
                            'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                        }))
            customer_picking = request.env['stock.picking'].sudo().create({
                'partner_id': sale_order_id.partner_id.id,
                'campus_id': sale_order_id.campus.id,
                'prof_body_id': sale_order_id.prof_body.id,
                'sale_order_id': sale_order_id.id,
                'sale_id': sale_order_id.id,
                'semester': sale_order_id.semester_id.id,
                'delivery_order_source': sale_order_id.quote_type,
                'location_id': picking_type_id.id,
                'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                'picking_type_id': picking_type_id.id,
                'move_lines': line_list
            })
            customer_picking.sale_id = sale_order_id.id
            # invoice_id.action_invoice_open()
        if sale_order_id.debit_order_mandat and post.get('dbo_date') :
            date_day = int(post.get('dbo_date'))
            dbo_date = date(year=datetime.now().year, month=datetime.now().month, day=date_day)

            for each_debit_order in sale_order_id.debit_order_mandat:
                for i in range(sale_order_id.months):
                    deb_interest = each_debit_order.interest/float(sale_order_id.months)
                    debit_order_obj.sudo().create({'partner_id': sale_order_id.partner_id.id,
                                            'student_number': '',
                                            'dbo_amount': sale_order_id.monthly_amount,
                                            'interest': deb_interest,
                                            'course_fee': each_debit_order.dbo_amount - deb_interest,
                                            'dbo_date':dbo_date,
                                            'acc_holder': sale_order_id.partner_id.name,
                                            'bank_name': each_debit_order.bank_name.id,
                                            'bank_acc_no': each_debit_order.bank_acc_no,
                                            'bank_code': each_debit_order.bank_name.bic,
                                            'state': 'pending',
                                            'bank_type_id': each_debit_order.bank_type_id.id
                                            # 'invoice_id': invoice_id.id
                                            })
                    dbo_date = dbo_date + relativedelta(months=+1)

        template_id = request.env['mail.template'].sudo().search([('name', '=', 'Fees Pay Later Email')])
        if template_id:
            # template_id.send_mail(sale_order_id.id, force_send=True)

            sale_order_id = sale_order_id.sudo()
            if sale_order_id.affiliation == '1':
                pdf_data_enroll = request.env.ref('event_price_kt.report_sale_enrollment').sudo().render_qweb_pdf(
                    sale_order_id.id)
                enroll_file_name = "Pro-Forma " + sale_order_id.name
                if pdf_data_enroll:
                    pdfvals = {'name': enroll_file_name,
                               'db_datas': base64.b64encode(pdf_data_enroll[0]),
                               'datas': base64.b64encode(pdf_data_enroll[0]),
                               'datas_fname': enroll_file_name + '.pdf',
                               'res_model': 'sale.order',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                    attchment_list.append(pdf_create)

                agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                if agreement_id:
                    attchment_list.append(agreement_id)
                banking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                if banking_detail_id:
                    attchment_list.append(banking_detail_id)
                body_html = "<div>"
                body_html += "<br>"
                body_html += "Dear " + sale_order_id.partner_id.name + ","
                body_html += "<br><br>"
                body_html += "Thank you for your Enrolment Application"
                body_html += "<br><br>"
                body_html += "Please find attached Invoice as well as copy of the Student Agreement you just accepted during enrolment."
                body_html += "<br><br>"
                body_html += "Your sponsor/company can pay using the Invoice no. as reference and return proof of payment to: accounts@charterquest.co.za"
                body_html += " to process your enrolment. You can email accounts should you wish to make special payment arrangements."
                body_html += "<br><br>"
                body_html += "We look forward to seeing	you	during our course and helping you, in achieving	a 1st Time Pass!"
                body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Institute<br> CENTRAL CONTACT INFORMATION:<br>"
                body_html += "Tel: +27 (0)11 234 9223 [SA & Intl]<br> Tel: +27 (0)11 234 9238 [SA & Intl]<br> Tel: 0861 131 137 [SA ONLY]<br> Fax: 086 218 8713 [SA ONLY]<br>"
                body_html += "Email:enquiries@charterquest.co.za<br><br/> <div>"
                mail_values = {
                    'email_from': template_id.email_from,
                    'reply_to': template_id.reply_to,
                    'email_to': sale_order_id.partner_id.email if sale_order_id.partner_id.email else '',
                    'email_cc': 'enquiries@charterquest.co.za,accounts@charterquest.co.za,cqops@charterquest.co.za',
                    'subject': "Charterquest FreeQuote/Enrolment  " + sale_order_id.name,
                    'body_html': body_html,
                    'notification': True,
                    'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                    'auto_delete': False,
                }
                msg_id = mail_obj.sudo().create(mail_values)
                msg_id.send()
                if user_select and user_select.get('self_or_company') == 'cmp_sponosored':
                    return request.render('cfo_snr_jnr.enrolment_process_page_thankyou_bank',
                                          {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                              'self_or_company') else ''})

        return request.render('cfo_snr_jnr.enrolment_process_page_thankyou_bank')

    @http.route(['/event/redirect_payu'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def event_redirect(self, **post):

        sale_order_id = False
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return_url = urljoin(base_url, '/event/payment/payu_com/dpn/')
        cancel_url = urljoin(base_url, '/event/payment/payu_com/cancel/')
        currency = request.env.ref('base.main_company').currency_id
        invoice_obj = request.env['account.invoice'].sudo()
        debit_order_obj = request.env['debit.order.details'].sudo()
        invoice_line=[]
        debit_order_mandet = []
        if post.get('sale_order'):
            sale_order_id = request.env['sale.order'].sudo().search([('id', '=', int(post.get('sale_order')))])
        payu_tx_values = dict(post)
        payment_acquire = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payu')])
        amount = post.get('inputTotalDue') if post.get('inputTotalDue') else post.get('toalamount')
        # convert amount to cent
        if post.get('sale_order'):
            sale_order = post.get('sale_order')
        if request.session.get('sale_order'):
            sale_order = request.session['sale_order']
        if post.get('sale_order_id'):
            sale_order_id=post.get('sale_order_id')

        event_tickets = request.session['event_id'] if request.session.get('event_id') else ''
        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
        account_id = request.env['account.account'].sudo().search([('code', '=', '200000')], limit=1)
        product_id = request.env['product.product'].sudo().search([('name', '=', 'Interest Amount')], limit=1)
        interest_amount_line = [
            [0, 0, {'price_unit': post.get('inputInterest') if post.get('inputInterest') else 0,
                    'name': 'Interest Amount',
                    'product_id': product_id.id,
                    'product_uom_qty': 1,
                    'invoice_lines': [0, 0, {'name': 'Interest Amount',
                                             'account_id': account_id.id if account_id else False,
                                             'quantity': 1,
                                             'price_unit': post.get('inputInterest') if post.get(
                                                 'inputInterest') else 0,
                                             'price_subtotal': post.get(
                                                 'inputInterest') if post.get(
                                                 'inputInterest') else 0}],
                    'price_subtotal': post.get('inputInterest') if post.get(
                        'interest_amount') else 0}]]
        sale_order_id.write({'order_line': interest_amount_line})
        if amount:
            if len(amount.split('.')[1]) == 1:
                amount = amount + '0'
                amount = amount.replace('.', '')
            elif len(amount.split('.')[1]) == 2:
                amount = amount.replace('.', '')
        elif sale_order_id:
            amount = str(sale_order_id.amount_total) + '0'
            amount = amount.replace('.', '')
        for each_order_line in sale_order_id.order_line:
            invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                                        'name': each_order_line.name,
                                        'quantity': 1.0,
                                        'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
                                        'invoice_line_tax_ids': [
                                            (6, 0, [each_tax.id for each_tax in each_order_line.tax_id])],
                                        'price_unit': each_order_line.price_unit,
                                        'discount': each_order_line.discount}])

        invoice_id = invoice_obj.sudo().create({'partner_id': sale_order_id.partner_id.id,
                                                'campus': sale_order_id.campus.id,
                                                'prof_body': sale_order_id.prof_body.id,
                                                'sale_order_id': sale_order_id.id,
                                                'semester_id': sale_order_id.semester_id.id,
                                                'invoice_line_ids': invoice_line,
                                                'residual': sale_order_id.out_standing_balance_incl_vat,
                                                })

        if sale_order_id:
            debit_order_mandet = []
            res_bank_detail = False
            account_type = False

            if post.get('inputBankName'):
                res_bank_detail = request.env['res.bank'].sudo().search([('id', '=', int(post['inputBankName']))])
            if post.get('inputAtype'):
                account_type = request.env['account.account.type'].sudo().search([('id', '=', int(post['inputAtype']))])
            debit_order_mandet.append([0, 0, {'partner_id': sale_order_id.partner_id.id,
                                              'dbo_amount': post.get('inputtotalandInterest') if post.get(
                                                  'inputtotalandInterest') else 0,
                                              'course_fee': post.get('inputOutstanding') if post.get(
                                                  'inputOutstanding') else 0,
                                              'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                                              'interest': post.get('inputInterest') if post.get('inputInterest') else 0,
                                              'dbo_date':sale_order_id.confirmation_date,
                                              'acc_holder': sale_order_id.partner_id.name,
                                              'bank_name': res_bank_detail.id if res_bank_detail else '',
                                              'bank_acc_no': post.get('inputAccount') if post.get(
                                                  'inputAccount') else '',
                                              'bank_code': res_bank_detail.bic if res_bank_detail else '',
                                              'bank_type_id': int(post['inputAtype']) if post.get(
                                                  'inputAtype') else ''}])
            account_id = request.env['account.account'].sudo().search([('code', '=', '200000')], limit=1)
            product_id = request.env['product.product'].sudo().search([('name', '=', 'Interest Amount')], limit=1)

            sale_order_id.write(
                    {'diposit_selected': post.get('inputPaypercentage') if post.get('inputPaypercentage') else 0,
                     'due_amount': post.get('inputTotalDue') if post.get('inputTotalDue') else 0,
                     'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                     'out_standing_balance_incl_vat': post.get('inputtotalandInterest') if post.get(
                         'inputtotalandInterest') else 0,
                     'monthly_amount': post.get('inputpaymentpermonth') if post.get('inputpaymentpermonth') else 0,
                     'outstanding_amount': post.get('inputOutstanding') if post.get('inputOutstanding') else 0,
                   })

            if int(post.get('inputPaypercentage')) < 100:
                interest_amount_line = [
                    [0, 0, {'price_unit': post.get('interest_amount') if post.get('interest_amount') else 0,
                            'name': 'Interest Amount',
                            'product_id': product_id.id,
                            'product_uom_qty': 1,
                            'invoice_lines': [0, 0, {'name': 'Interest Amount',
                                                     'account_id': account_id.id if account_id else False,
                                                     'quantity': 1,
                                                     'price_unit': post.get('interest_amount') if post.get(
                                                         'interest_amount') else 0,
                                                     'price_subtotal': post.get(
                                                         'interest_amount') if post.get(
                                                         'interest_amount') else 0}],
                            'price_subtotal': post.get('interest_amount') if post.get(
                                'interest_amount') else 0}]]
                sale_order_id.write({'interest_amount': post.get('inputInterest') if post.get('inputInterest') else 0,
                                     'due_day': int(post.get('inputPaydate')) if int(post.get('inputPaydate')) else 0,
                                     'debit_order_mandate':True,
                                     'debit_order_mandat': debit_order_mandet})
                if sale_order_id:
                    quote_name = sale_order_id.name
                    m = hashlib.md5()
                    m.update(quote_name.encode())
                    decoded_quote_name = m.hexdigest()
                    config_para = request.env['ir.config_parameter'].sudo().search(
                        [('key', 'ilike', 'web.base.url')])
                    if config_para:
                        link = config_para.value + "/debitorder/" + decoded_quote_name
                        # link = "http://enrolments.charterquest.co.za/debitordermandate/" + decoded_quote_name
                        sale_order_id.write(
                            {'name': quote_name, 'debit_order_mandate_link': link, 'debit_link': link})
            stock_warehouse = request.env['stock.warehouse'].sudo().search([('name', '=', sale_order_id.campus.name)])

            picking_type_id = request.env['stock.picking.type'].sudo().search([('name', '=', 'Delivery Orders'),
                                                                               ('warehouse_id', '=',
                                                                                sale_order_id.warehouse_id.id)])

            line_list = []
            for each_event_ticket in event_tickets:
                event_ticket = request.env['event.event.ticket'].sudo().search(
                    [('id', '=', int(event_tickets[each_event_ticket]))])
                book_combination = request.env['course.material'].sudo().search(
                    [('event_id', '=', event_ticket.event_id.id),
                     ('study_option_id', '=', event_ticket.product_id.id)])
                if book_combination:
                    for each_combination in book_combination.material_ids:
                        line_list.append((0, 0, {
                            'name': 'move out',
                            'product_id': each_combination.material_product_id.id,
                            'product_uom': each_combination.material_product_id.uom_id.id,
                            'product_uom_qty': 1,
                            'procure_method': 'make_to_stock',
                            'location_id': picking_type_id.id,
                            'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                        }))
            customer_picking = request.env['stock.picking'].sudo().create({
                'partner_id': sale_order_id.partner_id.id,
                'campus_id': sale_order_id.campus.id,
                'prof_body_id': sale_order_id.prof_body.id,
                'sale_order_id': sale_order_id.id,
                'sale_id': sale_order_id.id,
                'semester': sale_order_id.semester_id.id,
                'delivery_order_source': sale_order_id.quote_type,
                'location_id': picking_type_id.id,
                'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                'picking_type_id': picking_type_id.id,
                'move_lines': line_list
            })
            customer_picking.sale_id = sale_order_id.id
            # invoice_id.action_invoice_open()
            # payment_id.action_validate_invoice_payment()

            if sale_order_id.debit_order_mandat:
                date_day = int(post.get('inputPaydate')) if post.get('inputPaydate') else False
                if date_day:
                    dbo_date = date(year=datetime.now().year, month=datetime.now().month, day=date_day)
                    debit_order_mandat_id = sale_order_id.debit_order_mandat[-1]
                    deb_interest = debit_order_mandat_id.interest / debit_order_mandat_id.months
                    for i in range(sale_order_id.months):
                        res = debit_order_obj.create({'partner_id': sale_order_id.partner_id.id,
                                                      'student_number': '',
                                                      'dbo_amount': sale_order_id.monthly_amount,
                                                      'dbo_date': dbo_date,
                                                      'course_fee': sale_order_id.monthly_amount - deb_interest,
                                                      'interest': deb_interest,
                                                      'acc_holder': sale_order_id.partner_id.name,
                                                      'bank_name': debit_order_mandat_id.bank_name.id,
                                                      'bank_acc_no': debit_order_mandat_id.bank_acc_no,
                                                      'bank_code': debit_order_mandat_id.bank_name.bic,
                                                      'state': 'pending',
                                                      'bank_type_id': debit_order_mandat_id.bank_type_id.id,
                                                      'invoice_id': invoice_id.id if invoice_id else False
                                                      })
                        dbo_date = dbo_date + relativedelta(months=+1)

            first_name = ''
            last_name = ''
            if ' ' in sale_order_id.partner_id.name:
                first_name,last_name = sale_order_id.partner_id.name.split(' ', 1)
            else:
                first_name = sale_order_id.partner_id.name
            transactionDetails = {}
            transactionDetails['store'] = {}
            transactionDetails['store']['soapUsername'] = payment_acquire.payu_api_username
            transactionDetails['store']['soapPassword'] = payment_acquire.payu_api_password
            transactionDetails['store']['safekey'] = payment_acquire.payu_seller_account
            transactionDetails['store']['environment'] = payment_acquire.environment
            transactionDetails['store']['TransactionType'] = 'PAYMENT'
            transactionDetails['basket'] = {}
            transactionDetails['basket']['description'] = 'CFO'
            transactionDetails['basket']['amountInCents'] = amount
            transactionDetails['basket']['currencyCode'] = currency.name
            transactionDetails['additionalInformation'] = {}
            transactionDetails['additionalInformation']['merchantReference'] = sale_order_id.name
            transactionDetails['additionalInformation']['returnUrl'] = return_url
            transactionDetails['additionalInformation']['cancelUrl'] = cancel_url
            transactionDetails['additionalInformation']['supportedPaymentMethods'] = 'CREDITCARD'
            transactionDetails['additionalInformation']['demoMode'] = False
            transactionDetails['Stage'] = False
            transactionDetails['customer'] = {}
            transactionDetails['customer']['email'] = sale_order_id.partner_id.email
            transactionDetails['customer']['firstName'] = first_name if first_name else ''
            transactionDetails['customer']['lastName'] = last_name if last_name else ''
            transactionDetails['customer']['mobile'] = sale_order_id.partner_id.mobile

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
            'amount': "{0:.2f}".format(sale_order_id.due_amount or 0),
            'currency_id': sale_order_id.pricelist_id.currency_id.id,
            'partner_id': sale_order_id.partner_id.id,
            'partner_country_id': sale_order_id.partner_id.country_id.id if sale_order_id.partner_id.country_id else 1,
            'reference': request.env['payment.transaction'].get_next_reference(sale_order_id.name),
            'sale_order_id': sale_order_id.id,
        }

        tx = request.env['payment.transaction'].sudo().create(tx_values)
        url = PayuController.payuMeaSetTransactionApiCall('', transactionDetails)
        return werkzeug.utils.redirect(url)

    @http.route('/event/payment/payu_com/cancel', type='http', auth="none", methods=['POST', 'GET'])
    def payu_com_cancel(self, **post):
        """ When the user cancels its Payu payment: GET on this route """
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        return werkzeug.utils.redirect('/event/unsuccessful')

    @http.route(['/event/unsuccessful'], type='http', auth="public", website=True)
    def unsuccessful(self, **post):

        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        cr, uid, context = request.cr, request.uid, request.context

        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
        else:
            return request.redirect('/enrolment_book')
        request.website.sale_reset()
        return request.render("cfo_snr_jnr.event_unsuccessful", {'order': order})

    @http.route('/event/payment/payu_com/dpn', type='http', auth="public", methods=['POST', 'GET'], website=True)
    def event_payu_com_dpn(self, **post):
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

            sale_order_id = request.env['sale.order'].sudo().search([('name', '=', result['merchantReference'])])
            sale_order_data = sale_order_id
            request.session['sale_last_order_id'] = sale_order_id.id

            tx_id = request.env['payment.transaction'].sudo().search([('reference', '=', result['merchantReference'])])
            tx = tx_id
            if not sale_order_id or (sale_order_id.amount_total and not tx):
                return request.redirect('/shop')
            if (not sale_order_id.amount_total and not tx) or tx.state in ['pending']:
                if sale_order_id.state in ['draft', 'sent']:
                    if (not sale_order_id.amount_total and not tx):
                        sale_order_id.action_button_confirm()
                    email_act = sale_order_id.action_quotation_send()
            elif tx and tx.state == 'cancel':
                sale_order_id.action_cancel()
            elif tx and (tx.state == 'draft' or tx.state == 'sent' or tx.state == 'done'):
                #             if result and payu_response['successful'] and payu_response['TRANSACTION_STATUS'] in ['SUCCESSFUL', 'PARTIAL_PAYMENT', 'OVER_PAYMENT']:
                if result and payu_response['TRANSACTION_STATUS'] in ['SUCCESSFUL', 'PARTIAL_PAYMENT', 'OVER_PAYMENT']:
                    transaction = tx.sudo().write(
                        {'state': 'done', 'date_validate': datetime.now(),
                         'acquirer_reference': result['payUReference']})
                    email_act = sale_order_id.action_quotation_send()
                    action_confirm_res = sale_order_id.action_confirm()
                    sale_order = sale_order_id.read([])
                #             if sale_order_id.state == 'sale':
                #                 journal_ids = request.env['account.journal'].sudo().search([('name', '=', 'FNB 62085815143')], limit=1)
                #                 journal = journal_ids.read([])
                currency = request.env['res.currency'].sudo().search([('name', '=', 'ZAR')], limit=1)
                method = request.env['account.payment.method'].sudo().search([('name', '=', 'Manual')], limit=1)
                journal_id = request.env['account.journal'].sudo().search(
                    [('name', '=', 'FNB - Cheque Account 6208585815143')], limit=1, order="id desc")
                if journal_id:
                    account_payment = {
                        'partner_id': sale_order[0]['partner_id'][0],
                        'partner_type': 'customer',
                        'journal_id': journal_id.id,
                        # 'invoice_ids':[(4,inv_obj.id,0)],
                        'amount': sale_order[0]['amount_total'],
                        'communication': sale_order_id.name,
                        'currency_id': currency.id,
                        'payment_type': 'inbound',
                        'payment_method_id': method.id,
                        'payment_transaction_id': tx.id,
                    }
                    acc_payment = request.env['account.payment'].sudo().create(account_payment)
                    acc_payment.sudo().post()
                sale_order_id = request.session.get('sale_last_order_id')
                sale_order_data = request.env['sale.order'].sudo().browse(sale_order_id)
                # if sale_order_data.project_project_id:
                #     request.session['last_project_id'] = sale_order_data.project_project_id.id
            if response_state:
                sale_order_data.message_post(subject="T&C's Privacy Policy",
                                             body="%s accepted T&C's and Privacy Policy." % sale_order_data.partner_id.name)
                return werkzeug.utils.redirect('/pay/thankyou')
                # return werkzeug.utils.redirect('/shop/confirmation')
            else:
                return werkzeug.utils.redirect('/event/unsuccessful')
        except Exception as e:
            return werkzeug.utils.redirect('/event/unsuccessful')

    @http.route(['/pay/thankyou'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def pay_thankyou(self, **post):
        invoice_obj = request.env['account.invoice'].sudo()
        debit_order_obj = request.env['debit.order.details'].sudo()
        mail_obj = request.env['mail.mail'].sudo()
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        attachment_list = []
        invoice_line = []
        if post.get('sale_order'):
            sale_order = post.get('sale_order')
        if request.session.get('sale_order'):
            sale_order = request.session['sale_order']
        if request.session.get('sale_last_order_id'):
            sale_order = request.session.get('sale_last_order_id')

        event_tickets = request.session['event_id'] if request.session.get('event_id') else ''

        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
        if sale_order_id and sale_order_id.quote_type == 'freequote':
            for each_order_line in sale_order_id.order_line:
                invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                                            'name': each_order_line.name,
                                            'quantity': 1.0,
                                            'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
                                            'invoice_line_tax_ids': [
                                                (6, 0, [each_tax.id for each_tax in each_order_line.tax_id])],
                                            'price_unit': each_order_line.price_unit,
                                            'discount': each_order_line.discount}])
            invoice_id = invoice_obj.sudo().create({'partner_id': sale_order_id.partner_id.id,
                                                    'campus': sale_order_id.campus.id,
                                                    'prof_body': sale_order_id.prof_body.id,
                                                    'sale_order_id': sale_order_id.id,
                                                    'semester_id': sale_order_id.semester_id.id,
                                                    'invoice_line_ids': invoice_line,
                                                    'residual': sale_order_id.out_standing_balance_incl_vat,
                                                    })
            sale_order_id._action_confirm()
            sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
            for debit_line in sale_order_id.debit_order_mandat:
                debit_line.write({'dbo_date': sale_order_id.confirmation_date})
            ctx = {'default_type':'out_invoice', 'type':'out_invoice', 'journal_type':'sale', 'company_id':sale_order_id.company_id.id}
            inv_default_vals = request.env['account.invoice'].with_context(ctx).sudo().default_get(['journal_id'])
            ctx.update({'journal_id': inv_default_vals.get('journal_id')})
            invoice_id = sale_order_id.with_context(ctx).sudo().action_invoice_create()
            invoice_id = request.env['account.invoice'].sudo().browse(invoice_id[0])
            journal_id = request.env['account.journal'].sudo().browse(inv_default_vals.get('journal_id'))
            payment_methods = journal_id.inbound_payment_method_ids or journal_id.outbound_payment_method_ids
            payment_id = request.env['account.payment'].sudo().create({
                        'partner_id': sale_order_id.partner_id.id,
                        'amount': sale_order_id.due_amount if sale_order_id.due_amount else sale_order_id.amount_total,
                        'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'invoice_ids': [(6, 0, invoice_id.ids)],
                        'payment_date': datetime.today(),
                        'journal_id': journal_id.id,
                        'payment_method_id': payment_methods[0].id
                    })
            # invoice_id._onchange_partner_id()

        if sale_order_id and sale_order_id.quote_type == 'enrolment':
            sale_order_id._action_confirm()
            sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
            ctx = {'default_type': 'out_invoice', 'type': 'out_invoice', 'journal_type': 'sale',
                   'company_id': sale_order_id.company_id.id}
            inv_default_vals = request.env['account.invoice'].with_context(ctx).sudo().default_get(['journal_id'])
            ctx.update({'journal_id': inv_default_vals.get('journal_id')})
            invoice_id = sale_order_id.with_context(ctx).sudo().action_invoice_create()
            invoice_id = request.env['account.invoice'].sudo().browse(invoice_id[0])
            journal_id = request.env['account.journal'].sudo().browse(inv_default_vals.get('journal_id'))
            payment_methods = journal_id.inbound_payment_method_ids or journal_id.outbound_payment_method_ids
            payment_id = request.env['account.payment'].sudo().create({
                'partner_id': sale_order_id.partner_id.id,
                'amount': sale_order_id.due_amount if sale_order_id.due_amount else sale_order_id.amount_total,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'invoice_ids': [(6, 0, invoice_id.ids)],
                'payment_date': datetime.today(),
                'journal_id': journal_id.id,
                'payment_method_id': payment_methods[0].id
            })

        stock_warehouse = request.env['stock.warehouse'].sudo().search([('name', '=', sale_order_id.campus.name)])
        # stock_location = request.env['stock.location'].sudo().search(
        #     [('location_id', '=', sale_order_id.warehouse_id.id)])
        picking_type_id = request.env['stock.picking.type'].sudo().search([('name', '=', 'Delivery Orders'),
                                                                           ('warehouse_id', '=',
                                                                            sale_order_id.warehouse_id.id)])

        line_list = []
        for each_event_ticket in event_tickets:
            event_ticket = request.env['event.event.ticket'].sudo().search(
                [('id', '=', int(event_tickets[each_event_ticket]))])
            book_combination = request.env['course.material'].sudo().search(
                [('event_id', '=', event_ticket.event_id.id),
                 ('study_option_id', '=', event_ticket.product_id.id)])
            if book_combination:
                for each_combination in book_combination.material_ids:
                    line_list.append((0, 0, {
                        'name': 'move out',
                        'product_id': each_combination.material_product_id.id,
                        'product_uom': each_combination.material_product_id.uom_id.id,
                        'product_uom_qty': 1,
                        'procure_method': 'make_to_stock',
                        'location_id': picking_type_id.id,
                        'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                    }))
        customer_picking = request.env['stock.picking'].sudo().create({
            'partner_id': sale_order_id.partner_id.id,
            'campus_id': sale_order_id.campus.id,
            'prof_body_id': sale_order_id.prof_body.id,
            'sale_order_id': sale_order_id.id,
            'sale_id': sale_order_id.id,
            'semester': sale_order_id.semester_id.id,
            'delivery_order_source': sale_order_id.quote_type,
            'location_id': picking_type_id.id,
            'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
            'picking_type_id': picking_type_id.id,
            'move_lines': line_list
        })
        customer_picking.sale_id = sale_order_id.id
        invoice_id.action_invoice_open()
        payment_id.action_validate_invoice_payment()
        if sale_order_id.debit_order_mandat:
            date_day = sale_order_id.due_day
            if date_day:
                dbo_date = date(year=datetime.now().year, month=datetime.now().month, day=date_day)
                debit_order_mandat_id = sale_order_id.debit_order_mandat[-1]
                deb_interest = debit_order_mandat_id.interest / debit_order_mandat_id.months
                for i in range(sale_order_id.months):
                    res = debit_order_obj.create({'partner_id': sale_order_id.partner_id.id,
                                                  'student_number': '',
                                                  'dbo_amount': sale_order_id.monthly_amount,
                                                  'dbo_date': dbo_date,
                                                  'course_fee': sale_order_id.monthly_amount - deb_interest,
                                                  'interest': deb_interest,
                                                  'acc_holder': sale_order_id.partner_id.name,
                                                  'bank_name': debit_order_mandat_id.bank_name.id,
                                                  'bank_acc_no': debit_order_mandat_id.bank_acc_no,
                                                  'bank_code': debit_order_mandat_id.bank_name.bic,
                                                  'state': 'pending',
                                                  'bank_type_id': debit_order_mandat_id.bank_type_id.id,
                                                  'invoice_id': invoice_id.id if invoice_id else False
                                                  })
                    dbo_date = dbo_date + relativedelta(months=+1)
        template_id = request.env['mail.template'].sudo().search([('name', '=', 'Fees Pay Later Email')])
        if template_id:
            # template_id.send_mail(sale_order_id.id, force_send=True)
            if sale_order_id.affiliation == '1':
                pdf_data = request.env.ref('event_price_kt.report_enrollment_invoice').sudo().render_qweb_pdf(
                    invoice_id.id)
                pdf_data_statement_invoice = request.env.ref(
                    'event_price_kt.report_statement_enrollment').sudo().render_qweb_pdf(invoice_id.id)
                if pdf_data:
                    pdfvals = {'name': 'Invoice',
                               'db_datas': base64.b64encode(pdf_data[0]),
                               'datas': base64.b64encode(pdf_data[0]),
                               'datas_fname': 'Invoice.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                    attachment_list.append(pdf_create)

                if pdf_data_statement_invoice:
                    pdfvals = {'name': 'Enrolment Statement',
                               'db_datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas_fname': 'Enrolment Statement.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                    attachment_list.append(pdf_create)

                agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                if agreement_id:
                    attachment_list.append(agreement_id)

                banking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                if banking_detail_id:
                    attachment_list.append(banking_detail_id)
                body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                body_html += "<br>"
                body_html += "Dear " + sale_order_id.partner_id.name + ","
                body_html += "<br><br>"
                body_html += "Thank	you	for	your enrolment and payment received!"
                body_html += "<br><br>"
                body_html += "For your records,	please find	attached invoice/Full Statement, copy of the Student Agreement as well as the Debit	Order Mandate you just accepted	Online during enrolment."
                body_html += "<br><br>"
                body_html += "The Student Agreement inter alia covers:"
                body_html += "<br><br>"
                body_html += "1. Exam fee remmittances. <br> 2. How to access your learning materials. <br> 3. Cancellations, change of bookings and postponements."
                body_html += "<br> 4. Refunds and students complaints. <br> 5. 1st Time Pass Guarantee scheme and other incidental matters."
                body_html += "<br><br> We look forward to seeing you during our course and helping you, in achieving a 1st Time Pass!"
                body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Professional Education Institute<br>"
                body_html += "CENTRAL CONTACT INFORMATION:<br> Tel: +27 (0)11 234 9223 [SA & Intl]<br> Cell: +27 (0)73 174 5454 [SA & Intl]<br> <br/><div>"
                
                mail_values = {
                    'email_from': template_id.email_from,
                    'reply_to': template_id.reply_to,
                    'email_to': sale_order_id.partner_id.email if sale_order_id.partner_id.email else '',
                    'subject': "Charterquest FreeQuote/Enrolment  " + sale_order_id.name,
                    'body_html': body_html,
                    'notification': True,
                    'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])],
                    'auto_delete': False,
                }
                msg_id = mail_obj.create(mail_values)
                msg_id.send()
                if user_select.get('self_or_company') == 'cmp_sponosored':
                    return request.render('cfo_snr_jnr.enrolment_process_page_thankyou_creditcard',
                                          {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                              'self_or_company') else ''})
        return request.render('cfo_snr_jnr.enrolment_process_page_thankyou_creditcard')

    @http.route(['/thank-you'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def thank_you(self, **post):
        res_bank_detail=False
        debit_order_mandet = []
        invoice_obj = request.env['account.invoice'].sudo()
        debit_order_obj = request.env['debit.order.details'].sudo()
        mail_obj = request.env['mail.mail'].sudo()
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        attchment_list = []
        invoice_line = []
        invoice_id = False

        if post.get('sale_order'):
            sale_order = post.get('sale_order')
        if request.session.get('sale_order'):
            sale_order = request.session['sale_order']
        if post.get('sale_order_id'):
            sale_order_id=post.get('sale_order_id')

        event_tickets = request.session['event_id'] if request.session.get('event_id') else ''
        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))

        sale_order_id.write({'state': 'sale'})
        for each_order_line in sale_order_id.order_line:
            invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                                        'name': each_order_line.name,
                                        'quantity': 1.0,
                                        'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
                                        'invoice_line_tax_ids': [
                                            (6, 0, [each_tax.id for each_tax in each_order_line.tax_id])],
                                        'price_unit': each_order_line.price_unit,
                                        'discount': each_order_line.discount}])
        invoice_id = invoice_obj.sudo().create({'partner_id': sale_order_id.partner_id.id,
                                         'campus': sale_order_id.campus.id,
                                         'prof_body': sale_order_id.prof_body.id,
                                         'sale_order_id': sale_order_id.id,
                                         'semester_id': sale_order_id.semester_id.id,
                                         'invoice_line_ids': invoice_line,
                                         'residual': sale_order_id.out_standing_balance_incl_vat,
                                         })
        if request.session.get('do_invoice') == 'yes':
            sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
            ctx = {'default_type': 'out_invoice', 'type': 'out_invoice', 'journal_type': 'sale',
                   'company_id': sale_order_id.company_id.id}
            inv_default_vals = request.env['account.invoice'].with_context(ctx).sudo().default_get(['journal_id'])
            ctx.update({'journal_id': inv_default_vals.get('journal_id')})
            invoice_id = sale_order_id.with_context(ctx).sudo().action_invoice_create()
            invoice_id = request.env['account.invoice'].sudo().browse(invoice_id[0])
            invoice_id.action_invoice_open()

        if request.session.get('do_invoice') == 'no':
            invoice_id.action_invoice_cancel()
            sale_order_id.write({'state': 'draft'})

        if post.get('sale_order'):
            sale_order_id = request.env['sale.order'].sudo().browse(int(post.get('sale_order')))
            debit_order_mandet = []
            debit_order_mandet.append([0, 0, {'partner_id': sale_order_id.partner_id.id,
                                              'dbo_amount': post.get('dbo_amount') if post.get(
                                                  'dbo_amount') else 0,
                                              'course_fee': post.get('course_fee') if post.get(
                                                  'course_fee') else 0,
                                              'months': post.get('months') if post.get('months') else 0,
                                              'interest': post.get('interest') if post.get('interest') else 0,
                                              'dbo_date': sale_order_id.confirmation_date,
                                              'acc_holder': sale_order_id.partner_id.name,
                                              'bank_name':post.get('bank_name') if post.get('bank_name')else '',
                                              'bank_acc_no': post.get('bank_acc_no') if post.get(
                                                  'bank_acc_no') else '',
                                              'bank_code': res_bank_detail.bic if res_bank_detail else '',
                                              'bank_type_id': int(post['bank_type_id']) if post.get(
                                                  'bank_type_id') else ''}])
            account_id = request.env['account.account'].sudo().search([('code', '=', '200000')], limit=1)
            product_id = request.env['product.product'].sudo().search([('name', '=', 'Interest Amount')], limit=1)
            interest_amount_line = [[0, 0, {'price_unit': post.get('interest_amount') if post.get('interest_amount') else 0,
                                            'name': 'Interest Amount',
                                            'product_id': product_id.id,
                                            'product_uom_qty': 1,
                                            'invoice_lines': [0, 0, {'name': 'Interest Amount',
                                                                     'account_id': account_id.id if account_id else False,
                                                                     'quantity': 1,
                                                                     'price_unit': post.get('interest_amount') if post.get(
                                                                         'interest_amount') else 0,
                                                                     'price_subtotal': post.get(
                                                                         'interest_amount') if post.get(
                                                                         'interest_amount') else 0}],
                                            'price_subtotal': post.get('interest_amount') if post.get(
                                                'interest_amount') else 0}]]
            sale_order_id.write({'due_amount': post.get('payment_amount') if post.get('payment_amount') else 0,
                                 'months': post.get('months') if post.get('months') else 0,
                                 'out_standing_balance_incl_vat': post.get('dbo_amount') if post.get(
                                     'dbo_amount') else 0,
                                 'interest_amount': post.get('interest') if post.get('interest') else 0,
                                 'debit_order_mandate':True,
                                'debit_order_mandat': debit_order_mandet,
                                 'order_line':interest_amount_line})
            sale_order_id = request.env['sale.order'].sudo().browse(int(post.get('sale_order')))
            ctx = {'default_type': 'out_invoice', 'type': 'out_invoice', 'journal_type': 'sale',
                   'company_id': sale_order_id.company_id.id}
            inv_default_vals = request.env['account.invoice'].with_context(ctx).sudo().default_get(['journal_id'])
            ctx.update({'journal_id': inv_default_vals.get('journal_id')})
            invoice_id = sale_order_id.with_context(ctx).sudo().action_invoice_create()
            invoice_id = request.env['account.invoice'].sudo().browse(invoice_id[0])
            invoice_id.action_invoice_open()
            journal_id = request.env['account.journal'].sudo().browse(inv_default_vals.get('journal_id'))
            payment_methods = journal_id.inbound_payment_method_ids or journal_id.outbound_payment_method_ids

            payment_id = request.env['account.payment'].sudo().create({
                'partner_id': sale_order_id.partner_id.id,
                'amount': sale_order_id.due_amount if sale_order_id.due_amount else sale_order_id.amount_total,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'invoice_ids': [(6, 0, invoice_id.ids)],
                'payment_date': datetime.today(),
                'journal_id': journal_id.id,
                'payment_method_id': payment_methods[0].id,
                'amount':post.get('payment_amount') if post.get('payment_amount') else sale_order_id.payment_amount,
            })

            if sale_order_id:
                quote_name = sale_order_id.name
                m = hashlib.md5()
                m.update(quote_name.encode())
                decoded_quote_name = m.hexdigest()
                config_para = request.env['ir.config_parameter'].sudo().search(
                    [('key', 'ilike', 'web.base.url')])
                if config_para:
                    link = config_para.value + "/debitorder/" + decoded_quote_name
                    # link = "http://enrolments.charterquest.co.za/debitordermandate/" + decoded_quote_name
                    sale_order_id.write(
                        {'name': quote_name, 'debit_order_mandate_link': link, 'debit_link': link})
            stock_warehouse = request.env['stock.warehouse'].sudo().search([('name', '=', sale_order_id.campus.name)])
            # stock_location = request.env['stock.location'].sudo().search(
            #     [('location_id', '=', sale_order_id.warehouse_id.id)])
            picking_type_id = request.env['stock.picking.type'].sudo().search([('name', '=', 'Delivery Orders'),
                                                                               ('warehouse_id', '=',
                                                                                sale_order_id.warehouse_id.id)])

            line_list = []
            for each_event_ticket in event_tickets:
                event_ticket = request.env['event.event.ticket'].sudo().search(
                    [('id', '=', int(event_tickets[each_event_ticket]))])
                book_combination = request.env['course.material'].sudo().search(
                    [('event_id', '=', event_ticket.event_id.id),
                     ('study_option_id', '=', event_ticket.product_id.id)])
                if book_combination:
                    for each_combination in book_combination.material_ids:
                        line_list.append((0, 0, {
                            'name': 'move out',
                            'product_id': each_combination.material_product_id.id,
                            'product_uom': each_combination.material_product_id.uom_id.id,
                            'product_uom_qty': 1,
                            'procure_method': 'make_to_stock',
                            'location_id': picking_type_id.id,
                            'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                        }))
            customer_picking = request.env['stock.picking'].sudo().create({
                'partner_id': sale_order_id.partner_id.id,
                'campus_id': sale_order_id.campus.id,
                'prof_body_id': sale_order_id.prof_body.id,
                'sale_order_id': sale_order_id.id,
                'sale_id': sale_order_id.id,
                'semester': sale_order_id.semester_id.id,
                'delivery_order_source': sale_order_id.quote_type,
                'location_id': picking_type_id.id,
                'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                'picking_type_id': picking_type_id.id,
                'move_lines': line_list
            })
            customer_picking.sale_id = sale_order_id.id
            invoice_id.action_invoice_open()
            payment_id.action_validate_invoice_payment()

            if sale_order_id.debit_order_mandat:
                date_day = int(post.get('dbo_date'))
                dbo_date = date(year=datetime.now().year, month=datetime.now().month, day=date_day)
                debit_order_mandat_id = sale_order_id.debit_order_mandat[-1]
                for i in range(sale_order_id.months):
                    res = debit_order_obj.create({'partner_id': sale_order_id.partner_id.id,
                                                  'student_number': '',
                                                  'dbo_amount': sale_order_id.monthly_amount,
                                                  'dbo_date': dbo_date,
                                                  'course_fee': debit_order_mandat_id.course_fee,
                                                  'interest': debit_order_mandat_id.interest,
                                                  'acc_holder': sale_order_id.partner_id.name,
                                                  'bank_name': debit_order_mandat_id.bank_name.id,
                                                  'bank_acc_no': debit_order_mandat_id.bank_acc_no,
                                                  'bank_code': debit_order_mandat_id.bank_name.bic,
                                                  'state': 'pending',
                                                  'bank_type_id': debit_order_mandat_id.bank_type_id.id,
                                                  'invoice_id': invoice_id.id if invoice_id else False
                                                  })
                    dbo_date = dbo_date + relativedelta(months=+1)
        template_id = request.env['mail.template'].sudo().search([('name', '=', 'Fees Pay Later Email')])
        if template_id:
            # template_id.send_mail(sale_order_id.id, force_send=True)
            if sale_order_id.affiliation == '1':
                pdf_data = request.env.ref('event_price_kt.report_enrollment_invoice').sudo().render_qweb_pdf(
                    invoice_id.id)
                pdf_data_statement_invoice = request.env.ref(
                    'event_price_kt.report_statement_enrollment').sudo().render_qweb_pdf(invoice_id.id)
                if pdf_data:
                    pdfvals = {'name': 'Invoice',
                               'db_datas': base64.b64encode(pdf_data[0]),
                               'datas': base64.b64encode(pdf_data[0]),
                               'datas_fname': 'Invoice.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                    attchment_list.append(pdf_create)

                if pdf_data_statement_invoice:
                    pdfvals = {'name': 'Enrolment Statement',
                               'db_datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas_fname': 'Enrolment Statement.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                    attchment_list.append(pdf_create)

                agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                if agreement_id:
                    attchment_list.append(agreement_id)

                banking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                if banking_detail_id:
                    attchment_list.append(banking_detail_id)
                body_html = "<div>"
                body_html += "<br>"
                body_html += "Dear " + sale_order_id.partner_id.name + ","
                body_html += "<br><br>"
                body_html += "Thank you for your enrolment"
                body_html += "<br>"
                body_html += "Please find attached Proforma Invoice, Banking details and copy of Student Agreement you just accepted!"
                body_html += "<br>"
                body_html += "You can pay using the invoice number as reference and return proof of payment to: accounts@charterquest.co.za to process your enrolment." 
                body_html += "<br><br> We look forward to seeing you during our course and helping you, in achieving a 1st Time Pass!"
                body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Professional Education Institute<br>"
                body_html += "CENTRAL CONTACT INFORMATION:<br> Tel: +27 (0)11 234 9223 [SA & Intl]<br> Cell: +27 (0)73 174 5454 [SA & Intl]<br> <br/><div>"
                mail_values = {
                    'email_from': template_id.email_from,
                    'reply_to': template_id.reply_to,
                    'email_to': sale_order_id.partner_id.email if sale_order_id.partner_id.email else '',
                    'email_cc': 'enquiries@charterquest.co.za,accounts@charterquest.co.za,cqops@charterquest.co.za',
                    'subject': "Charterquest FreeQuote/Enrolment  " + sale_order_id.name,
                    'body_html': body_html,
                    'notification': True,
                    'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                    'auto_delete': False,
                }
                msg_id = mail_obj.create(mail_values)
                msg_id.send()

                if user_select and user_select.get('self_or_company') == 'cmp_sponosored':
                    return request.render('cfo_snr_jnr.enrolment_process_page_thankyou',
                                          {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                              'self_or_company') else ''})

            if sale_order_id.affiliation == '2' and request.session.get('sale_order') and request.session.get(
                    'do_invoice') == 'yes':
                com_spo_reg_enrol = request.env.ref('cfo_snr_jnr.company_sponsored_regist_enrol_email_template')
                pdf_data = request.env.ref('event_price_kt.report_enrollment_invoice').sudo().render_qweb_pdf(invoice_id.id)
                pdf_data_statement_invoice = request.env.ref(
                    'event_price_kt.report_statement_enrollment').sudo().render_qweb_pdf(invoice_id.id)

                if pdf_data:
                    pdfvals = {'name': 'Invoice',
                               'db_datas': base64.b64encode(pdf_data[0]),
                               'datas': base64.b64encode(pdf_data[0]),
                               'datas_fname': 'Invoice.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                    attchment_list.append(pdf_create)

                if pdf_data_statement_invoice:
                    pdfvals = {'name': 'Enrolment Statement',
                               'db_datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas_fname': 'Enrolment Statement.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                    attchment_list.append(pdf_create)

                agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                if agreement_id:
                    attchment_list.append(agreement_id)

                banking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                if banking_detail_id:
                    attchment_list.append(banking_detail_id)

#                 body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
#                 body_html += "<br>"
#                 body_html += "Dear " + sale_order_id.partner_id.name + ","
#                 body_html += "<br><br>"
#                 body_html += "Thank you for your Enrolment Application."
#                 body_html += "<br><br>"
#                 body_html += "Please find attached Invoice as well as copy of the Student Agreement you just accepted during enrolment."
#                 body_html += "<br><br>"
#                 body_html += "Your sponsor/company can pay using the Invoice no. as reference and return proof of payment to: accounts@charterquest.co.za"
#                 body_html += " to process your enrolment. You can email accounts should you wish to make special payment arrangements."
#                 body_html += "<br><br>"
#                 body_html += "To avoid delays in gaining access to your materials and classes, kindly present a valid pre-authorisation on your company’s letterhead, addressed to us: CharterQuest, stating this invoice number, amount and an irrevocable commitment to settle the payment within 30 days. "
#                 body_html += "<br><br>"
#                 body_html += "Should obtaining a valid pre-authorisation not be feasible, you could in the interim pay 20% deposit and sign debit order for the balance to get started; once your company pays us in full, we will refund to you all payments received!"
#                 body_html += "<br><br>"
#                 body_html += "Please note that in any event above, should your company not honour its commitment, we may require you to settle the payment in full! "
#                 body_html += "<br><br>"
#                 body_html += "We look forward to seeing	you	during our course and helping you, in achieving	a 1st Time Pass!"
#                 body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Institute<br> CENTRAL CONTACT INFORMATION:<br>"
#                 body_html += "Tel: +27 (0)11 234 9223 [SA & Intl]<br> Tel: +27 (0)11 234 9238 [SA & Intl]<br> Tel: 0861 131 137 [SA ONLY]<br> Fax: 086 218 8713 [SA ONLY]<br>"
#                 body_html += "Email:enquiries@charterquest.co.za<br><br/> <div>"
                
                
                ctx = {
                        'model': 'sale.order',
                        'res_id': sale_order_id.id,
                        'use_template': True,
                        'template_id': com_spo_reg_enrol.id,
                        'mark_so_as_sent': True,
                        'force_email': True
                    }
                mail_compose_id = request.env['mail.compose.message'].sudo().generate_email_for_composer(com_spo_reg_enrol.id,sale_order_id.id)
                bodies = request.env['mail.template'].sudo().render_template(com_spo_reg_enrol, 'sale.order', sale_order_id.id, post_process=True)
                
                mail_compose_id.update({'email_to': sale_order_id.partner_id.email})
                mail_values = {
                    'email_from': com_spo_reg_enrol.sudo().email_from,
                    'reply_to': com_spo_reg_enrol.sudo().reply_to,
                    'email_to': mail_compose_id.get('email_to'),
                    'email_cc': com_spo_reg_enrol.sudo().email_cc,
                    'subject': mail_compose_id.get('subject'),
                    'body_html': mail_compose_id.get('body'),
                    'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                    'auto_delete': com_spo_reg_enrol.sudo().auto_delete,
                }

                msg_id = mail_obj.create(mail_values)
                msg_id.send()
                if user_select.get('self_or_company') == 'cmp_sponosored':
                    return request.render('cfo_snr_jnr.enrolment_process_page_thankyou',
                                          {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                              'self_or_company') else ''})
            if sale_order_id.affiliation == '2' and request.session.get('sale_order') and request.session.get(
                    'do_invoice') == 'no':
                pdf_data_enroll = request.env.ref('event_price_kt.report_sale_enrollment').sudo().render_qweb_pdf(
                    sale_order_id.id)
                enroll_file_name = "Pro-Forma " + sale_order_id.name
                if pdf_data_enroll:
                    pdfvals = {'name': enroll_file_name,
                               'db_datas': base64.b64encode(pdf_data_enroll[0]),
                               'datas': base64.b64encode(pdf_data_enroll[0]),
                               'datas_fname': enroll_file_name + '.pdf',
                               'res_model': 'sale.order',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                    attchment_list.append(pdf_create)

                agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                
                if agreement_id:
                    attchment_list.append(agreement_id)
                    
                banking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                if banking_detail_id:
                    attchment_list.append(banking_detail_id)
                body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                body_html += "<br>"
                body_html += "Dear " + sale_order_id.partner_id.name + ","
                body_html += "<br><br>"
                body_html += "Thank you for your Enrolment Application."
                body_html += "<br><br>"
                body_html += "Please find attached Invoice, Banking details and copy of Student Agreement you just accepted!"
                body_html += "<br><br>"
                body_html += "Your sponsor/company can pay using the Invoice no. as reference and return proof of payment to: accounts@charterquest.co.za"
                body_html += "<br><br>"
                body_html += "To avoid delays in gaining access to your materials and classes, kindly present a valid pre-authorisation on your company’s letter head, addressed to us: CharterQuest, stating this invoice number, amount and an irrevocable commitment to settle the payment within 30 days." 
                body_html += "<br><br>"
                body_html += "Should obtaining a valid pre-authorisation not be feasible, you could in the interim pay 20% deposit and sign debit order for the balance to get started; once your company pays us in full, we will refund to you all payments received!"
                body_html += "<br><br>"
                body_html += "Please note that in any event above, should your company not honour its commitment, we may require you to settle the payment in full!"
                body_html += "<br><br>" 
                body_html += "We look forward to seeing you during our course and helping you, in achieving a 1st Time Pass!"
                body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Institute<br> CENTRAL CONTACT INFORMATION:<br>"
                body_html += "Tel: +27 (0)11 234 9223 [SA & Intl]<br> Tel: +27 (0)11 234 9238 [SA & Intl]<br> Tel: 0861 131 137 [SA ONLY]<br> Fax: 086 218 8713 [SA ONLY]<br>"
                body_html += "Email:enquiries@charterquest.co.za<br><br/> <div>"
                mail_values = {
                    'email_from': template_id.email_from,
                    'reply_to': template_id.reply_to,
                    'email_to': sale_order_id.partner_id.email if sale_order_id.partner_id.email else '',
                    'email_cc': 'enquiries@charterquest.co.za,accounts@charterquest.co.za,cqops@charterquest.co.za',
                    'subject': "Charterquest FreeQuote/Enrolment  " + sale_order_id.name,
                    'body_html': body_html,
                    'notification': True,
                    'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                    'auto_delete': False,
                }
                msg_id = mail_obj.sudo().create(mail_values)
                msg_id.send()
                print("\n\n\n\n\n=============user select===========",user_select)
                if user_select.get('self_or_company') == 'cmp_sponosored':
                    return request.render('cfo_snr_jnr.enrolment_process_page_thankyou',
                                          {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                              'self_or_company') else ''})

        return request.render('cfo_snr_jnr.enrolment_process_reg_and_enrol_thankyou')

    @http.route(['/validate_payment'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def validate_payment(self, **post):
        debit_order_mandet = []
        res_bank_detail = False
        account_type = False

        if post.get('inputBankName'):
            res_bank_detail = request.env['res.bank'].sudo().search([('id', '=', int(post['inputBankName']))])
        if post.get('inputAtype'):
            account_type = request.env['account.account.type'].sudo().search([('id', '=', int(post['inputAtype']))])
        if post.get('sale_order'):
            sale_order_id = request.env['sale.order'].sudo().browse(int(post.get('sale_order')))
            debit_order_mandet.append([0, 0, {'partner_id': sale_order_id.partner_id.id,
                                              'dbo_amount': post.get('inputtotalandInterest') if post.get(
                                                  'inputtotalandInterest') else 0,
                                              'course_fee': post.get('inputOutstanding') if post.get(
                                                  'inputOutstanding') else 0,
                                              'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                                              'interest': post.get('inputInterest') if post.get('inputInterest') else 0,
                                              'dbo_date': sale_order_id.confirmation_date,
                                              'acc_holder': sale_order_id.partner_id.name,
                                              'bank_name': res_bank_detail.id if res_bank_detail else '',
                                              'bank_acc_no': post.get('inputAccount') if post.get(
                                                  'inputAccount') else '',
                                              'bank_code': res_bank_detail.bic if res_bank_detail else '',
                                              'bank_type_id': int(post['inputAtype']) if post.get(
                                                  'inputAtype') else ''}])


            dict1={'diposit_selected':int(post.get('inputPaypercentage')) if int(post.get('inputPaypercentage')) else 0,
                 'due_amount': post.get('inputTotalDue') if post.get('inputTotalDue') else 0,
                 'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                 'out_standing_balance_incl_vat': post.get('inputtotalandInterest') if post.get(
                     'inputtotalandInterest') else 0,
                 'monthly_amount': post.get('inputpaymentpermonth') if post.get('inputpaymentpermonth') else 0,
                 'outstanding_amount': post.get('inputOutstanding') if post.get('inputOutstanding') else 0,
                 'interest_amount': post.get('inputInterest') if post.get('inputInterest') else 0,
                 # 'order_line': interest_amount_line
                 }
            sale_order_id.write(dict1)
            # sale_order_id.action_confirm()

        if post.get('Pay Via Bank Deposit'):
            return request.render('cfo_snr_jnr.enrolment_process_validate_payment', {'post_data': post if post else '',
                                                                                     'button_hide': True,
                                                                                     'hide_bank_detail': True,
                                                                                     'dbo_date':post.get('inputPaydate') if post.get('inputPaydate') else 0,})
        else:
            return request.render('cfo_snr_jnr.enrolment_process_validate_payment', {'post_data': post if post else '',
                                                                                     'button_hide': False,
                                                                                     'hide_bank_detail': False,
                                                                                     'interest_amount':post.get('inputInterest') if post.get('inputInterest') else 0,
                                                                                     'sale_order_id':sale_order_id if sale_order_id else False,
                                                                                     'payment_amount': post.get('inputTotalDue') if post.get('inputTotalDue') else 0,
                                                                                     'dbo_date': post.get('inputPaydate') if post.get('inputPaydate') else 0,
                                                                                     'dbo_amount': post.get('inputtotalandInterest') if post.get('inputtotalandInterest') else 0,
                                                                                     'course_fee': post.get('inputOutstanding') if post.get('inputOutstanding') else 0,
                                                                                     'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                                                                                     'interest': post.get('inputInterest') if post.get('inputInterest') else 0,
                                                                                     'bank_acc_no': post.get('inputAccount') if post.get('inputAccount') else '',
                                                                                     'bank_name': post.get('inputBankName') if post.get('inputBankName') else '',
                                                                                     'bank_type_id': int(post['inputAtype']) if post.get('inputAtype') else '',
                                                                                     'eft':True})


    @http.route(['/Page/Thank-you'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def validate_payment1(self, **post):
        debit_order_mandet = []
        res_bank_detail = False
        account_type = False

        if post.get('inputBankName'):
            res_bank_detail = request.env['res.bank'].sudo().search([('id', '=', int(post['inputBankName']))])
        if post.get('inputAtype'):
            account_type = request.env['account.account.type'].sudo().search([('id', '=', int(post['inputAtype']))])
        if post.get('sale_order'):
            sale_order_id = request.env['sale.order'].sudo().browse(int(post.get('sale_order')))
            debit_order_mandet = []
            debit_order_mandet.append([0, 0, {'partner_id': sale_order_id.partner_id.id,
                                              'dbo_amount': post.get('inputtotalandInterest') if post.get(
                                                  'inputtotalandInterest') else 0,
                                              'course_fee': post.get('inputOutstanding') if post.get(
                                                  'inputOutstanding') else 0,
                                              'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                                              'interest': post.get('inputInterest') if post.get('inputInterest') else 0,
                                              'dbo_date':sale_order_id.confirmation_date,
                                              'acc_holder': sale_order_id.partner_id.name,
                                              'bank_name': res_bank_detail.id if res_bank_detail else '',
                                              'bank_acc_no': post.get('inputAccount') if post.get(
                                                  'inputAccount') else '',
                                              'bank_code': res_bank_detail.bic if res_bank_detail else '',
                                              'bank_type_id': int(post['inputAtype']) if post.get(
                                                  'inputAtype') else ''}])

            account_id=request.env['account.account'].sudo().search([('name','=','200000 Product Sales')],limit=1)
            product_id = request.env['product.product'].sudo().search([('name', '=', 'Interest Amount')], limit=1)
            interest_amount_line=[[0,0,{'price_unit': post.get('inputInterest') if post.get('inputInterest') else 0,
                                  'name':'Interest Amount',
                                  'product_id':product_id.id,
                                  'product_uom_qty':1,
                                  'invoice_lines':[0,0,{'name':'Interest Amount',
                                                     'account_id':account_id.id,
                                                     'quantity':1,
                                                     'price_unit':post.get('inputInterest') if post.get('inputInterest') else 0,
                                                     'price_subtotal':post.get('inputInterest') if post.get('inputInterest') else 0}],
                                  'price_subtotal':post.get('inputInterest') if post.get('inputInterest') else 0}]]

            sale_order_id.write(
                {'diposit_selected': post.get('inputPaypercentage') if post.get('inputPaypercentage') else 0,
                 'due_amount': post.get('inputTotalDue') if post.get('inputTotalDue') else 0,
                 'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                 'out_standing_balance_incl_vat': post.get('inputtotalandInterest') if post.get(
                     'inputtotalandInterest') else 0,
                 'monthly_amount': post.get('inputpaymentpermonth') if post.get('inputpaymentpermonth') else 0,
                 'outstanding_amount': post.get('inputOutstanding') if post.get('inputOutstanding') else 0,
                 'debit_order_mandate': True,
                 'interest_amount': post.get('inputInterest') if post.get('inputInterest') else 0,
                 'debit_order_mandat': debit_order_mandet,
                 'order_line':interest_amount_line if interest_amount_line else 0})

            invoice_obj = request.env['account.invoice'].sudo()
            debit_order_obj = request.env['debit.order.details'].sudo()
            mail_obj = request.env['mail.mail'].sudo()
            # user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
            attachment_list = []
            invoice_line = []
            if post.get('sale_order'):
                sale_order = post.get('sale_order')
            if request.session.get('sale_order'):
                sale_order = request.session['sale_order']
            if request.session.get('sale_last_order_id'):
                sale_order = request.session.get('sale_last_order_id')

            event_tickets = request.session['event_id'] if request.session.get('event_id') else ''

            sale_order_id = request.env['sale.order'].sudo().browse(int(post.get('sale_order')))

            # if sale_order_id and sale_order_id.quote_type == 'freequote':

            ctx = {'default_type': 'out_invoice', 'type': 'out_invoice', 'journal_type': 'sale',
                   'company_id': sale_order_id.company_id.id}
            inv_default_vals = request.env['account.invoice'].with_context(ctx).sudo().default_get(['journal_id'])
            ctx.update({'journal_id': inv_default_vals.get('journal_id')})
            invoice_id = sale_order_id.with_context(ctx).sudo().action_invoice_create()
            invoice_id = request.env['account.invoice'].sudo().browse(invoice_id[0])
            invoice_id.action_invoice_open()
            journal_id = request.env['account.journal'].sudo().browse(inv_default_vals.get('journal_id'))
            payment_methods = journal_id.inbound_payment_method_ids or journal_id.outbound_payment_method_ids
            payment_id = request.env['account.payment'].sudo().create({
                'partner_id': sale_order_id.partner_id.id,
                'amount': sale_order_id.due_amount if sale_order_id.due_amount else sale_order_id.amount_total,
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'invoice_ids': [(6, 0, invoice_id.ids)],
                'payment_date': datetime.today(),
                'journal_id': journal_id.id,
                'payment_method_id': payment_methods[0].id,
                'amount':sale_order_id.payment_amount,
            })


            # if sale_order_id and sale_order_id.quote_type == 'enrolment':

                # for each_order_line in sale_order_id.order_line:
                #     invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                #                                 'name': each_order_line.name,
                #                                 'quantity': 1.0,
                #                                 'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
                #                                 'invoice_line_tax_ids': [
                #                                     (6, 0, [each_tax.id for each_tax in each_order_line.tax_id])],
                #                                 'price_unit': each_order_line.price_unit,
                #                                 'discount': each_order_line.discount}])
                # invoice_id = invoice_obj.sudo().create({'partner_id': sale_order_id.partner_id.id,
                #                                         'campus': sale_order_id.campus.id,
                #                                         'prof_body': sale_order_id.prof_body.id,
                #                                         'sale_order_id': sale_order_id.id,
                #                                         'semester_id': sale_order_id.semester_id.id,
                #                                         'invoice_line_ids': invoice_line,
                #                                         'residual': sale_order_id.out_standing_balance_incl_vat,
                #                                         })

            #     invoice_id=sale_order_id.sudo().action_invoice_create()
            #     invoice_id = request.env['account.invoice'].sudo().browse(invoice_id[0])
            #     print ("\n\n--------------invoice_id--->>>>>>>>>>>>>>>>>>>>>>>>",invoice_id,sale_order_id)
            # #         sale_order_id.invoice_ids = [(4,invoice_id.id)]
            stock_warehouse = request.env['stock.warehouse'].sudo().search([('name', '=', sale_order_id.campus.name)])
            # stock_location = request.env['stock.location'].sudo().search(
            #     [('location_id', '=', sale_order_id.warehouse_id.id)])
            picking_type_id = request.env['stock.picking.type'].sudo().search([('name', '=', 'Delivery Orders'),
                                                                               ('warehouse_id', '=',
                                                                                sale_order_id.warehouse_id.id)])

            line_list = []
            for each_event_ticket in event_tickets:
                event_ticket = request.env['event.event.ticket'].sudo().search(
                    [('id', '=', int(event_tickets[each_event_ticket]))])
                book_combination = request.env['course.material'].sudo().search(
                    [('event_id', '=', event_ticket.event_id.id),
                     ('study_option_id', '=', event_ticket.product_id.id)])
                if book_combination:
                    for each_combination in book_combination.material_ids:
                        line_list.append((0, 0, {
                            'name': 'move out',
                            'product_id': each_combination.material_product_id.id,
                            'product_uom': each_combination.material_product_id.uom_id.id,
                            'product_uom_qty': 1,
                            'procure_method': 'make_to_stock',
                            'location_id': picking_type_id.id,
                            'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                        }))
            customer_picking = request.env['stock.picking'].sudo().create({
                'partner_id': sale_order_id.partner_id.id,
                'campus_id': sale_order_id.campus.id,
                'prof_body_id': sale_order_id.prof_body.id,
                'sale_order_id': sale_order_id.id,
                'sale_id': sale_order_id.id,
                'semester': sale_order_id.semester_id.id,
                'delivery_order_source': sale_order_id.quote_type,
                'location_id': picking_type_id.id,
                'location_dest_id': sale_order_id.partner_id.property_stock_customer.id,
                'picking_type_id': picking_type_id.id,
                'move_lines': line_list
            })
            customer_picking.sale_id = sale_order_id.id
            invoice_id.action_invoice_open()
            # if sale_order_id and sale_order_id.quote_type == 'freequote':
            payment_id.action_validate_invoice_payment()

            if sale_order_id.debit_order_mandat:
                date_day = int(post.get('inputPaydate'))
                dbo_date = date(year=datetime.now().year, month=datetime.now().month, day=date_day)
                debit_order_mandat_id = sale_order_id.debit_order_mandat[-1]
                debit_intrest = debit_order_mandat_id.interest/int(sale_order_id.months)
                for i in range(sale_order_id.months):
                    res = debit_order_obj.create({'partner_id': sale_order_id.partner_id.id,
                                                  'student_number': '',
                                                  'dbo_amount': sale_order_id.monthly_amount,
                                                  'dbo_date': dbo_date,
                                                  'course_fee': sale_order_id.monthly_amount - debit_intrest,
                                                  'interest': debit_intrest,
                                                  'acc_holder': sale_order_id.partner_id.name,
                                                  'bank_name': debit_order_mandat_id.bank_name.id,
                                                  'bank_acc_no': debit_order_mandat_id.bank_acc_no,
                                                  'bank_code': debit_order_mandat_id.bank_name.bic,
                                                  'state': 'pending',
                                                  'bank_type_id': debit_order_mandat_id.bank_type_id.id,
                                                  'invoice_id': invoice_id.id if invoice_id else False
                                                  })
                    dbo_date = dbo_date + relativedelta(months=+1)

            template_id = request.env['mail.template'].sudo().search([('name', '=', 'Fees Pay Later Email')])
            if template_id:
                # template_id.send_mail(sale_order_id.id, force_send=True)
                if sale_order_id.affiliation == '1':
                    pdf_data = request.env.ref('event_price_kt.report_enrollment_invoice').sudo().render_qweb_pdf(
                        invoice_id.id)
                    pdf_data_statement_invoice = request.env.ref(
                        'event_price_kt.report_statement_enrollment').sudo().render_qweb_pdf(invoice_id.id)
                    if pdf_data:
                        pdfvals = {'name': 'Invoice',
                                   'db_datas': base64.b64encode(pdf_data[0]),
                                   'datas': base64.b64encode(pdf_data[0]),
                                   'datas_fname': 'Invoice.pdf',
                                   'res_model': 'account.invoice',
                                   'type': 'binary'}
                        pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                        attachment_list.append(pdf_create)

                    if pdf_data_statement_invoice:
                        pdfvals = {'name': 'Enrolment Statement',
                                   'db_datas': base64.b64encode(pdf_data_statement_invoice[0]),
                                   'datas': base64.b64encode(pdf_data_statement_invoice[0]),
                                   'datas_fname': 'Enrolment Statement.pdf',
                                   'res_model': 'account.invoice',
                                   'type': 'binary'}
                        pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                        attachment_list.append(pdf_create)

                    agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                    if agreement_id:
                        attachment_list.append(agreement_id)

                    banking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                    if banking_detail_id:
                        attachment_list.append(banking_detail_id)
                    body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                    body_html += "<br>"
                    body_html += "Dear " + sale_order_id.partner_id.name + ","
                    body_html += "<br><br>"
                    body_html += "<br><br>"
                    body_html += "Thank	you	for	your enrolment and payment received!"
                    body_html += "<br><br>"
                    body_html += "For your records,	please find	attached invoice/Full Statement, copy of the Student Agreement as well as the Debit	Order Mandate you just accepted	Online during enrolment."
                    body_html += "<br><br>"
                    body_html += "The Student Agreement inter alia covers:"
                    body_html += "<br><br>"
                    body_html += "1. Exam fee remmittances. <br> 2. How to access your learning materials. <br> 3. Cancellations, change of bookings and postponements."
                    body_html += "<br> 4. Refunds and students complaints. <br> 5. 1st Time Pass Guarantee scheme and other incidental matters."
                    body_html += "<br><br> We look forward to seeing you during our course and helping you, in achieving a 1st Time Pass!"
                    body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Professional Education Institute<br>"
                    body_html += "CENTRAL CONTACT INFORMATION:<br> Tel: +27 (0)11 234 9223 [SA & Intl]<br> Cell: +27 (0)73 174 5454 [SA & Intl]<br> <br/><div>"

                    mail_values = {
                        'email_from': template_id.email_from,
                        'reply_to': template_id.reply_to,
                        'email_to': sale_order_id.partner_id.email if sale_order_id.partner_id.email else '',
                        'subject': "Charterquest FreeQuote/Enrolment  " + sale_order_id.name,
                        'body_html': body_html,
                        'notification': True,
                        'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])],
                        'auto_delete': False,
                    }
                    msg_id = mail_obj.create(mail_values)
                    msg_id.send()
            return request.render('cfo_snr_jnr.enrolment_process_page_thankyou')
