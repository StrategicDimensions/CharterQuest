import base64
import hashlib

from pkg_resources import require
from odoo import http
from odoo.http import request
from datetime import date, datetime
import PyPDF2
import json, base64


class EnrolmentProcess(http.Controller):

    @http.route(['/enrolment_reg'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def enrolment_reg(self):
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        request.session['reg_and_enrol'] = ''
        return request.render('cfo_snr_jnr.enrolment_process_registration', {'page_name': 'registration',
                                                                             'self_or_cmp': user_select[
                                                                                 'self_or_company'] if user_select.get(
                                                                                 'self_or_company') else ''})

    @http.route(['/registration_form'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def registration_form(self):
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        return request.render('cfo_snr_jnr.enrolment_process_registration_and_enroll', {'page_name': 'registration',
                                                                                        'self_or_cmp': user_select[
                                                                                            'self_or_company'] if user_select.get(
                                                                                            'self_or_company') else ''
                                                                                        })

    @http.route(['/enrolment_book'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def enrolment_book(self):
        request.session['reg_and_enrol'] = ''
        return request.render('cfo_snr_jnr.get_free_quote_email', {'page_name': 'book'})

    @http.route(['/max_discount_ready'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def max_discount_ready(self, **post):
        # if post.get('discount'):
        request.session['reg_and_enrol'] = ''
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        today_date = datetime.today()
        str_today_date = datetime.strftime(today_date, '%Y-%m-%d')
        max_discount_detail = request.env['event.max.discount'].sudo().search([('date', '=', str_today_date),
                                                                               ('prof_body', '=',
                                                                                int(user_select[
                                                                                        'Select Prof Body']) if user_select else '')],
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
        max_discount_detail = request.env['event.max.discount'].sudo().search([('date', '=', str_today_date),
                                                                               ('prof_body', '=',
                                                                                int(user_select['Select Prof Body']) if user_select else '')],
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
        request.session['grand_tot'] = float(post['grand_tot'].replace(',', '')) if post.get('grand_tot') else 0
        request.session['product_tot'] = float(post['product_tot'].replace(',', '')) if post.get('product_tot') else 0
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
                                                                      ('semester_id', '=', int(post.get('Semester'))),
                                                                      ('state', '!=', 'cancel'),
                                                                      ('date_end', '>=', str_today_date)])
            event_details_dict = {}
            duplicate_event_detail_dict = {}
            for each in event_details:
                if each.qualification and each.event_ticket_ids:
                    if each.qualification.order in event_details_dict:
                        if any(each.qualification.name == each_dict for each_dict in event_details_dict[each.qualification.order]):
                            if not any(each == each_dict for each_dict in event_details_dict[each.qualification.order][each.qualification.name]['event']):
                                event_details_dict[each.qualification.order][each.qualification.name]['event'].append(each)
                            for each_ticket in each.event_ticket_ids:
                                if each_ticket.product_id not in event_details_dict[each.qualification.order][each.qualification.name]['ticket_product']:
                                    event_details_dict[each.qualification.order][each.qualification.name]['ticket_product'].append(each_ticket.product_id)
                        else:
                            if not each.qualification.name in duplicate_event_detail_dict:
                                if each.event_ticket_ids:
                                    duplicate_event_detail_dict[each.qualification.name] = {'ticket_product': [], 'event': []}
                                    for each_ticket in each.event_ticket_ids:
                                        if each_ticket.product_id not in duplicate_event_detail_dict[each.qualification.name]['ticket_product']:
                                            duplicate_event_detail_dict[each.qualification.name]['ticket_product'].append(each_ticket.product_id)
                                        if each not in duplicate_event_detail_dict[each.qualification.name]['event']:
                                            duplicate_event_detail_dict[each.qualification.name]['event'].append(each)
                            else:
                                if any(each.qualification.name == each_dict for each_dict in duplicate_event_detail_dict):
                                    if not any(each == each_dict for each_dict in duplicate_event_detail_dict[each.qualification.name]['event']):
                                        duplicate_event_detail_dict[each.qualification.name]['event'].append(each)
                                    for each_ticket in each.event_ticket_ids:
                                        if each_ticket.product_id not in duplicate_event_detail_dict[each.qualification.name]['ticket_product']:
                                            duplicate_event_detail_dict[each.qualification.name]['ticket_product'].append(each_ticket.product_id)
                    else:
                        if each.event_ticket_ids:
                            event_details_dict[each.qualification.order] = {
                                each.qualification.name: {'ticket_product': [], 'event': []}}
                            for each_ticket in each.event_ticket_ids:
                                if each_ticket.product_id not in event_details_dict[each.qualification.order][each.qualification.name]['ticket_product']:
                                    event_details_dict[each.qualification.order][each.qualification.name]['ticket_product'].append(each_ticket.product_id)
                                if each not in event_details_dict[each.qualification.order][each.qualification.name]['event']:
                                    event_details_dict[each.qualification.order][each.qualification.name]['event'].append(each)
            for each_duplicate in duplicate_event_detail_dict:
                if duplicate_event_detail_dict:
                    event_keys = sorted(list(event_details_dict.keys()))
                    event_details_dict[event_keys[-1]+1] = {each_duplicate: duplicate_event_detail_dict[each_duplicate]}
            return request.render('cfo_snr_jnr.enrolment_process_form2', {'enrolment_data': dict(sorted(event_details_dict.items())),
                                                                          'page_name': post.get('page_name'),
                                                                          'self_or_cmp': post['self_or_company'] if post.get('self_or_company') else ''})
        return request.render('cfo_snr_jnr.enrolment_process_form')

    @http.route(['/prof_body_form_render'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
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
            product_detail = request.env['product.product'].sudo().search([('event_type_rem', '=', int(user_select['Select Prof Body']) if user_select.get('Select Prof Body') else '')])
            if product_detail:
                for each_product in product_detail:
                    if each_product.event_qual_rem.order not in fees_dict:
                        fees_dict[each_product.event_qual_rem.order] = {each_product.event_qual_rem: {each_product.event_feetype_rem: [each_product]}}
                    else:
                        if each_product.event_feetype_rem in fees_dict[each_product.event_qual_rem.order][each_product.event_qual_rem]:
                            fees_dict[each_product.event_qual_rem.order][each_product.event_qual_rem][each_product.event_feetype_rem].append(each_product)
                        else:
                            fees_dict[each_product.event_qual_rem.order][each_product.event_qual_rem][each_product.event_feetype_rem] = [each_product]
                return request.render('cfo_snr_jnr.enrolment_process_form3', {'fees_detail': dict(sorted(fees_dict.items())),
                                                                              'page_name': 'fees',
                                                                              'return_student': user_select['return_student'] if user_select.get('self_or_company') else '',
                                                                              'self_or_cmp': user_select['self_or_company'] if user_select.get('self_or_company') else ''})
            return request.render('cfo_snr_jnr.enrolment_process_form3', {'page_name': 'fees',
                                                                          'self_or_cmp': user_select['self_or_company'] if user_select.get('self_or_company') else ''})
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
                            event_ticket_details = request.env['event.event.ticket'].sudo().search([('id', '=', int(value))])
                            if event_ticket_details:
                                if not event_ticket_details.event_id in event_count:
                                    event_count.append(event_ticket_details.event_id)
                    discount_detail = request.env['event.discount'].sudo().search([('event_type_id', '=', int(user_select['Select Prof Body']) if user_select.get('Select Prof Body') else '')])
                    for each_discount in discount_detail:
                        if each_discount not in discount_detail_list:
                            discount_detail_list.append(each_discount)
                    request.session['event_count'] = len(event_count) if event_count else 0
                    return request.render('cfo_snr_jnr.enrolment_process_discount_form', {'discount_detail': discount_detail_list,
                                                                                          'page_name': 'discounts',
                                                                                          'event_len': len(event_count) if event_count else 0})
                return request.render('cfo_snr_jnr.enrolment_process_discount_form')

    @http.route(['/price'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def price(self, **post):
        display_btn = request.session['reg_enrol_btn'] if request.session.get('reg_enrol_btn') else False
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        if post:
            request.session['discount_id'] = request.session['discount_id'] if request.session.get('discount_id') else ''
            request.session['discount_add'] = post.get('discount_add') if post.get('discount_add') else 0
            return request.render('cfo_snr_jnr.enrolment_process_price', {'product_id': request.session['product_id'],
                                                                          'event_id': request.session['event_id'],
                                                                          'page_name': 'price',
                                                                          'discount': float(post.get('discount_add')) if post.get('discount_add') else 0.0,
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

    @http.route(['/debitorder', '/debitorder/<uuid>'], type='http', auth="public", methods=['POST', 'GET'], website=True,
                csrf=False)
    def debitorder(self, uuid=False, **post):
        if uuid:
            sale_order_id = request.env['sale.order'].sudo().search([('debit_link', '=', uuid)])
            product_tot = 0.0
            grand_tot = 0.0
            if sale_order_id:
                for each in sale_order_id.order_line:
                    if each.product_id.fee_ok:
                        product_tot += each.price_subtotal
                    if each.product_id.event_ok:
                        grand_tot += each.price_subtotal
                print('product tot====', product_tot, grand_tot)

                if sale_order_id.quote_type == 'enrolment':
                    return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                                    'product_tot': product_tot,
                                                                                    'grand_tot': grand_tot,
                                                                                    'sale_order_id': sale_order_id if sale_order_id else '',
                                                                                    'mandate_link': 'mandate_link_find',
                                                                                    'bank_detail': 'true'})
                if sale_order_id.quote_type == 'freequote':
                    return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                                    'product_tot': product_tot,
                                                                                    'grand_tot': grand_tot,
                                                                                    'sale_order_id': sale_order_id if sale_order_id else '',
                                                                                    'mandate_link': 'mandate_link_find',
                                                                                    'bank_detail': ''})
        return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                        'product_tot': product_tot,
                                                                        'grand_tot': grand_tot})

    @http.route(['/payment'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def payment(self, **post):
        sale_order_id = False
        display_btn = request.session['reg_enrol_btn'] if request.session.get('reg_enrol_btn') else False
        product_ids = request.session['product_id'] if request.session.get('product_id') else ''
        reg_and_enrol = request.session['reg_and_enrol'] if request.session.get('reg_and_enrol') else ''
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''
        discount_id = request.session['discount_id'] if request.session.get('discount_id') else ''
        discount_add = request.session['discount_add'] if request.session.get('discount_add') else 0
        event_tickets = request.session['event_id'] if request.session.get('event_id') else ''
        sale_obj = request.env['sale.order'].sudo()
        user_select = request.session['user_selection_type'] if request.session.get('user_selection_type') else ''

        order_line = []
        for each_product in product_ids:
            product_id = request.env['product.product'].sudo().search([('id', '=', int(product_ids[each_product]))])
            order_line.append([0, 0, {'product_id': product_id.id,
                                      'product_uom_qty': 1.0,
                                      'product_uom': 1,
                                      'price_unit': product_id.lst_price}])

        for each_event_ticket in event_tickets:
            event_ticket = request.env['event.event.ticket'].sudo().search(
                [('id', '=', int(event_tickets[each_event_ticket]))])
            order_line.append([0, 0, {'product_id': event_ticket.product_id.id,
                                      'event_id': event_ticket.event_id.id if event_ticket.product_id.event_ok else '',
                                      'event_type_id': event_ticket.product_id.event_type_id.id if event_ticket.product_id.event_type_id else '',
                                      'event_ticket_id': event_ticket.id if event_ticket.event_id else '',
                                      'name': event_ticket.event_id.name,
                                      'product_uom_qty': 1.0,
                                      'product_uom': 1.0,
                                      'price_unit': event_ticket.price,
                                      'discount': float(discount_add) if discount_add else 0}])
        if request.session.get('reg_and_enrol'):
            if request.session.get('reg_and_enrol_email'):
                partner_detail = request.env['res.partner'].sudo().search([('email', '=', request.session['reg_and_enrol_email'])], limit=1)
                if partner_detail:
                    sale_order_id = sale_obj.create({'partner_id': partner_detail.id,
                                                     'affiliation': '1' if user_select.get('self_or_company') and user_select.get('self_or_company') == 'self' else '2',
                                                     'campus': user_select['campus'] if user_select.get(
                                                         'campus') else '',
                                                     'prof_body': user_select['Select Prof Body'] if user_select.get(
                                                         'Select Prof Body') else '',
                                                     'quote_type': 'enrolment',
                                                     'semester_id': user_select['Semester'] if user_select.get(
                                                         'Semester') else '',
                                                     'discount_type_ids': [(6, 0, [each for each in discount_id])],
                                                     'order_line': order_line})
                    # sale_order_id.write({'name': sale_order_id.name + 'WEB'})
                    quote_name = "SO{0}WEB".format(str(sale_order_id.id).zfill(3))
                    m = hashlib.md5(quote_name.encode())
                    decoded_quote_name = m.hexdigest()
                    config_para = request.env['ir.config_parameter'].sudo().search([('key', 'ilike', 'web.base.url')])
                    if config_para:
                        link = config_para.value + "/debitorder/" + decoded_quote_name
                        sale_order_id.write(
                            {'name': quote_name, 'debit_order_mandate_link': link, 'debit_link': decoded_quote_name})
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
                        return request.redirect('/thank-you')
                    else:
                        request.session['discount_id'] = ''
                        request.session['discount_add'] = ''
                        request.session['sale_order'] = ''
                        request.session['do_invoice'] = ''

                return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                                'product_tot': request.session[
                                                                                    'product_tot'],
                                                                                'grand_tot': request.session['grand_tot'],
                                                                                'page_confirm': 'yes',
                                                                                'sale_order': sale_order_id.id})
        else:
            if post.get('email'):
                partner_detail = request.env['res.partner'].sudo().search([('email', '=', post.get('email'))], limit=1)
                if partner_detail:
                    sale_order_id = sale_obj.create({'partner_id': partner_detail.id,
                                                     'affiliation': '1' if user_select.get('self_or_company') and user_select.get(
                                                         'self_or_company') == 'self' else '2',
                                                     'campus': user_select['campus'] if user_select.get('campus') else '',
                                                     'prof_body': user_select['Select Prof Body'] if user_select.get('Select Prof Body') else '',
                                                     'quote_type': 'enrolment' if display_btn else 'freequote',
                                                     'semester_id': user_select['Semester'] if user_select.get('Semester') else '',
                                                     'discount_type_ids':  [(6, 0, [each for each in discount_id])],
                                                     'order_line': order_line})
                    # quote_name = sale_order_id.name + 'WEB'
                    quote_name = "SO{0}WEB".format(str(sale_order_id.id).zfill(3))
                    m = hashlib.md5(quote_name.encode())
                    decoded_quote_name = m.hexdigest()
                    config_para = request.env['ir.config_parameter'].sudo().search([('key', 'ilike', 'web.base.url')])
                    if config_para:
                        link = config_para.value +"/debitorder/" + decoded_quote_name
                        sale_order_id.write({'name': quote_name, 'debit_order_mandate_link': link, 'debit_link': decoded_quote_name})
                    else:
                        sale_order_id.write({'name': quote_name})
                    for each_line in sale_order_id.order_line:
                        if each_line.event_id:
                            each_line.discount = float(discount_add) if discount_add else 0
                else:
                    account_rec_type_id = request.env['account.account.type'].sudo().search([('name', 'ilike', 'Receivable')])
                    account_pay_type_id = request.env['account.account.type'].sudo().search(
                        [('name', 'ilike', 'Payable')])
                    if account_rec_type_id:
                        account_id = request.env['account.account'].sudo().search([('user_type_id', '=', account_rec_type_id.id)], limit=1)

                    if account_pay_type_id:
                        account_id = request.env['account.account'].sudo().search([('user_type_id', '=', account_pay_type_id.id)], limit=1)

                        partner_id = request.env['res.partner'].sudo().create({'name': post['firstName'] + ' ' + post['lastName'] if post.get('firstName') and post.get('lastName') else '',
                                                                           'email': post['email'] if post.get('email') else '',
                                                                           'mobile': post['phoneNumber'] if post.get('phoneNumber') else '',
                                                                           'property_account_receivable_id': account_rec_type_id.id,
                                                                           'property_account_payable_id': account_pay_type_id.id})

                    sale_order_id = sale_obj.create({'partner_id': partner_id.id,
                                                     'campus': user_select['campus'] if user_select.get('campus') else '',
                                                     'prof_body': user_select['Select Prof Body'] if user_select.get('Select Prof Body') else '',
                                                     'quote_type': 'enrolment',
                                                     'semester_id': user_select['Semester'] if user_select.get('Semester') else '',
                                                     'discount_type_ids': [(6, 0, [each for each in discount_id])],
                                                     'order_line': order_line})
                    quote_name = sale_order_id.name + 'WEB'
                    m = hashlib.md5()
                    m.update(quote_name.encode())
                    decoded_quote_name = m.hexdigest()
                    config_para = request.env['ir.config_parameter'].sudo().search([('key', 'ilike', 'web.base.url')])
                    if config_para:
                        link = config_para.value + "/debitorder/" + decoded_quote_name
                        # link = "http://enrolments.charterquest.co.za/debitordermandate/" + decoded_quote_name
                        sale_order_id.write({'name': quote_name, 'debit_order_mandate_link': link, 'debit_link': link})
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
                    request.session['do_invoice'] = 'yes' if post.get('do_invoice') == 'Yes' else 'no'
                    return request.redirect('/page/thank-you')
                else:
                    request.session['discount_id'] = ''
                    request.session['discount_add'] = ''
                    request.session['sale_order'] = ''
                    request.session['do_invoice'] = ''

            return request.render('cfo_snr_jnr.enrolment_process_payment', {'page_name': 'payment',
                                                                            'product_tot': request.session['product_tot'],
                                                                            'grand_tot': request.session['grand_tot'],
                                                                            'sale_order': sale_order_id.id if sale_order_id else '',
                                                                            'invoice_generate': 'yes'})

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

        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
        if sale_order_id:
            if post.get('sale_order') or post.get('sale_order_id') or request.session.get('sale_order'):
                sale_order_id.write({'diposit_selected': post.get('inputPaypercentage') if post.get('inputPaypercentage') else 0,
                                     'due_amount': post.get('inputTotalDue') if post.get('inputTotalDue') else 0,
                                     'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                                     'out_standing_balance_incl_vat': post.get('inputtotalandInterest') if post.get('inputtotalandInterest') else 0,
                                     'monthly_amount': post.get('inputpaymentpermonth') if post.get('inputpaymentpermonth') else 0,
                                     'outstanding_amount': post.get('inputOutstanding') if post.get('inputOutstanding') else 0,
                                     'interest_amount':  post.get('inputInterest') if post.get('inputInterest') else 0})
                if request.session.get('do_invoice') == 'yes':
                    sale_order_id.write({'state': 'sale'})
                    for each_order_line in sale_order_id.order_line:
                        invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                                                    'name': each_order_line.name,
                                                    'quantity': 1.0,
                                                    'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
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
                if sale_order_id.affiliation == '1':
                    pdf_data_enroll = request.env.ref('event_price_kt.report_sale_enrollment').render_qweb_pdf(
                        sale_order_id.id)
                    enroll_file_name = "Pro-Forma " + sale_order_id.name
                    if pdf_data_enroll:
                        pdfvals = {'name': enroll_file_name,
                                   'db_datas': base64.b64encode(pdf_data_enroll[0]),
                                   'datas': base64.b64encode(pdf_data_enroll[0]),
                                   'datas_fname': enroll_file_name +".pdf",
                                   'res_model': 'sale.order',
                                   'type': 'binary'}
                        pdf_create = request.env['ir.attachment'].create(pdfvals)
                        attchment_list.append(pdf_create)

                    agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                    if agreement_id:
                        attchment_list.append(agreement_id)

                    body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                    body_html += "<br>"
                    body_html += "Dear " + sale_order_id.partner_id.name + ","
                    body_html += "<br><br>"
                    body_html += "Thank you for your course fee/price inquiry."
                    body_html += "<br><br>"
                    body_html += "<font size='3'>To enrol, please access banking details or pay online by clicking this link:</font>"
                    body_html += "<br><br>"
                    body_html += "" + sale_order_id.debit_order_mandate_link + ""
                    body_html += "<br><br>"
                    body_html += "Confirm discounts requirements below and double check your attached quote to ensure you have claimed all discounts applicable to you before you proceed:"
                    body_html += "<br><br>"
                    body_html += "<table border='1' style='width: 630px;max-width: 100%'> <tr style='background-color:lightgray;'> <td style='width:10%;'>Discount Category</td> <td style='width:60%;'>Requirements (All discounts must be claimed and included in the free quote or final invoice prior to making the first payment or will be forfeited).</td> <td>Discount % Available</td></tr>"

                    for each in discount_detail_list:
                        if event_count == 2:
                            if each.discount_type == 'combo_2':
                                body_html += "<tr> <td style='width:10%;'>" + each.name + "</td>"
                                if each.condition:
                                    body_html += "<td style='width:50%;'>" + each.condition + "</td>"
                                else:
                                    body_html += "<td style='width:50%;'> </td>"
                                if each.discount:
                                    body_html += "<td style='width:10%;'>" + str(each.discount) + "</td> </tr>"
                                else:
                                    body_html += "<td style='width:10%;'> " + '0.0' + "</td> </tr>"
                        if event_count == 3:
                            if each.discount_type == 'combo_3':
                                body_html += "<tr> <td style='width:10%;'>" + each.name + "</td>"
                                if each.condition:
                                    body_html += "<td style='width:50%;'>" + each.condition + "</td>"
                                else:
                                    body_html += "<td style='width:50%;'> </td>"
                                if each.discount:
                                    body_html += "<td style='width:10%;'>" + str(each.discount) + "</td> </tr>"
                                else:
                                    body_html += "<td style='width:10%;'> " + '0.0' + "</td> </tr>"
                        if event_count == 4:
                            if each.discount_type == 'combo_4':
                                body_html += "<tr> <td style='width:10%;'>" + each.name + "</td>"
                                if each.condition:
                                    body_html += "<td style='width:50%;'>" + each.condition + "</td>"
                                else:
                                    body_html += "<td style='width:50%;'> </td>"
                                if each.discount:
                                    body_html += "<td style='width:10%;'>" + str(each.discount) + "</td> </tr>"
                                else:
                                    body_html += "<td style='width:10%;'> " + '0.0' + "</td> </tr>"
                        if each.discount_type != 'combo_2' and each.discount_type != 'combo_3' and each.discount_type != 'combo_4':
                            body_html += "<tr> <td style='width:10%;'>" + each.name + "</td>"
                            if each.condition:
                                body_html += "<td style='width:50%;'>" + each.condition + "</td>"
                            else:
                                body_html += "<td style='width:50%;'> </td>"
                            if each.discount:
                                body_html += "<td style='width:10%;'>" + str(each.discount) + "</td> </tr>"
                            else:
                                body_html += "<td style='width:10%;'> "+'0.0' + "</td> </tr>"
                    body_html += "<tr><td></td><td><b>Maximum Discount Available</b></td><td>" + str(
                        max_discount_detail.max_discount) + "</td></tr>"
                    body_html += "</table><br><br>"
                    body_html += "We look forward to seeing you during our course and helping you, in achieving a 1st Time Pass!"
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
                    msg_id = mail_obj.create(mail_values)
                    msg_id.send()
                    if user_select.get('self_or_company') == 'cmp_sponosored':
                        return request.render('cfo_snr_jnr.enrolment_process_page_thankyou',
                                              {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                                  'self_or_company') else ''})
                elif sale_order_id.affiliation == '2':
                    if request.session.get('sale_order') and request.session.get('do_invoice') == 'yes':
                        pdf_data = request.env.ref('event_price_kt.report_enrollment_invoice').render_qweb_pdf(
                            invoice_id.id)
                        pdf_data_statement_invoice = request.env.ref(
                            'event_price_kt.report_statement_enrollment').render_qweb_pdf(invoice_id.id)

                        if pdf_data:
                            pdfvals = {'name': 'Invoice',
                                       'db_datas': base64.b64encode(pdf_data[0]),
                                       'datas': base64.b64encode(pdf_data[0]),
                                       'datas_fname': 'Invoice.pdf',
                                       'res_model': 'account.invoice',
                                       'type': 'binary'}
                            pdf_create = request.env['ir.attachment'].create(pdfvals)
                            attchment_list.append(pdf_create)

                        if pdf_data_statement_invoice:
                            pdfvals = {'name': 'Enrolment Statement',
                                       'db_datas': base64.b64encode(pdf_data_statement_invoice[0]),
                                       'datas': base64.b64encode(pdf_data_statement_invoice[0]),
                                       'datas_fname': 'Enrolment Statement.pdf',
                                       'res_model': 'account.invoice',
                                       'type': 'binary'}
                            pdf_create = request.env['ir.attachment'].create(pdfvals)
                            attchment_list.append(pdf_create)

                        agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                        if agreement_id:
                            attchment_list.append(agreement_id)

                        baking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                        if baking_detail_id:
                            attchment_list.append(baking_detail_id)


                        body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                        body_html += "<br>"
                        body_html += "Dear " + sale_order_id.partner_id.name + ","
                        body_html += "<br><br>"
                        body_html += "Thank you for your Enrolment Application."
                        body_html += "<br><br>"
                        body_html += "Please find attached Invoice as	well as	copy of	the	Student	Agreement you just accepted	during enrolment."
                        body_html += "<br><br>"
                        body_html += "Your sponsor/company can pay using the Invoice no. as reference and return proof of payment to: accounts@charterquest.co.za"
                        body_html += " to process your enrolment. You can email accounts should you wish to make special payment arrangements."
                        body_html += "<br><br>"
                        body_html += "Should your company require	an invoice, please forward this	proforma to	the	above email requesting its conversion into an invoice. We will need your company's details to generate an invoice for you!"
                        body_html += "<br><br>"
                        body_html += "Once we issue an invoice, this becomes binding as you will be	expected to	settle the amount in full should your company not honour the agreement. So please kindly ensure your company has pre-approved your bursary or training expenditure before you request conversion to an Invoice."
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
                        msg_id = mail_obj.create(mail_values)
                        msg_id.send()
                        if user_select.get('self_or_company') == 'cmp_sponosored':
                            return request.render('cfo_snr_jnr.enrolment_process_page_thankyou',
                                                  {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                                      'self_or_company') else ''})

                    if request.session.get('sale_order') and request.session.get('do_invoice') == 'no':
                        pdf_data_enroll = request.env.ref('event_price_kt.report_sale_enrollment').render_qweb_pdf(
                            sale_order_id.id)
                        enroll_file_name = "Pro-Forma " + sale_order_id.name
                        if pdf_data_enroll:
                            pdfvals = {'name': enroll_file_name,
                                       'db_datas': base64.b64encode(pdf_data_enroll[0]),
                                       'datas': base64.b64encode(pdf_data_enroll[0]),
                                       'datas_fname':  enroll_file_name +'.pdf',
                                       'res_model': 'sale.order',
                                       'type': 'binary'}
                            pdf_create = request.env['ir.attachment'].create(pdfvals)
                            attchment_list.append(pdf_create)

                        agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')

                        if agreement_id:
                            attchment_list.append(agreement_id)

                        body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                        body_html += "<br>"
                        body_html += "Dear " + sale_order_id.partner_id.name + ","
                        body_html += "<br><br>"
                        body_html += "Thank you for your Enrolment Application."
                        body_html += "<br><br>"
                        body_html += "Please find attached proforma Invoice as	well as	copy of	the	Student	Agreement you just accepted	during enrolment."
                        body_html += "<br><br>"
                        body_html += "Your sponsor/company can pay using the Invoice no. as reference and return proof of payment to: accounts@charterquest.co.za"
                        body_html += " to process your enrolment. You can email accounts should you wish to make special payment arrangements."
                        body_html += "<br><br>"
                        body_html += "Should your company require	an invoice, please forward this	proforma to	the	above email requesting its conversion into an invoice. We will need your company's details to generate an invoice for you!"
                        body_html += "<br><br>"
                        body_html += "Once we issue an invoice, this becomes binding as you will be	expected to	settle the amount in full should your company not honour the agreement. So please kindly ensure your company has pre-approved your bursary or training expenditure before you request conversion to an Invoice."
                        body_html += "<br><br>"
                        body_html += "We look forward to seeing you during our course and helping you, in achieving a 1st Time Pass!"
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
                        msg_id = mail_obj.create(mail_values)
                        msg_id.send()
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

        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
        for each_order_line in sale_order_id.order_line:
            invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                                        'name': each_order_line.name,
                                        'quantity': 1.0,
                                        'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
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
        if sale_order_id.debit_order_mandat:
            for each_debit_order in sale_order_id.debit_order_mandat:
                debit_order_obj.create({'partner_id': sale_order_id.partner_id.id,
                                        'student_number': '',
                                        'dbo_amount': each_debit_order.dbo_amount,
                                        'course_fee': each_debit_order.course_fee,
                                        'interest': each_debit_order.interest,
                                        'acc_holder': sale_order_id.partner_id.name,
                                        'bank_name': each_debit_order.bank_name.id,
                                        'bank_acc_no': each_debit_order.bank_acc_no,
                                        'bank_code': each_debit_order.bank_name.bic,
                                        'state': 'pending',
                                        'bank_type_id': each_debit_order.bank_type_id.id,
                                        'invoice_id': invoice_id.id
                                        })

        template_id = request.env['mail.template'].sudo().search([('name', '=', 'Fees Pay Later Email')])
        if template_id:
            # template_id.send_mail(sale_order_id.id, force_send=True)
            if sale_order_id.affiliation == '1':
                pdf_data_enroll = request.env.ref('event_price_kt.report_sale_enrollment').render_qweb_pdf(
                    sale_order_id.id)
                enroll_file_name = "Pro-Forma " + sale_order_id.name
                if pdf_data_enroll:
                    pdfvals = {'name': enroll_file_name,
                               'db_datas': base64.b64encode(pdf_data_enroll[0]),
                               'datas': base64.b64encode(pdf_data_enroll[0]),
                               'datas_fname': enroll_file_name+'.pdf',
                               'res_model': 'sale.order',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].create(pdfvals)
                    attchment_list.append(pdf_create)

                agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                if agreement_id:
                    attchment_list.append(agreement_id)

                body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                body_html += "<br>"
                body_html += "Dear " + sale_order_id.partner_id.name + ","
                body_html += "<br><br>"
                body_html += "Thank you for your Enrolment Application."
                body_html += "<br><br>"
                body_html += "Please find attached proforma invoice as well as copy of the Student Agreement and Debit Order Mandate you just accepted during enrolment."
                body_html += "<br><br>"
                body_html += "As you opted to 'pay by cash', please follow the steps below to complete your enrolment:"
                body_html += "<br><br>"
                body_html += "1. Click the link below to access our banking details;"
                body_html += "<br>http://www.charterquest.co.za/page/downloads"
                body_html += "<br><br>"
                body_html += "2. Make a cash deposit of at least 20% (taking into account your payment plan on the debit order mandate) of the course fee into our bank account with an additional R90 to cover cash deposit bank charges (use your proforma invoice no. as your pay reference to avoid delays in crediting your account, securing your place and releasing your study materials): and"
                body_html += "<br><br>"
                body_html += "3. Once the cash deposit is made email your proof of payment to accounts@charterquest.co.za. An email will be sent to you once your payment is allocated and the post-payment procedures defined in your Student Agreement attached will be activated."
                body_html += "<br><br>"
                body_html += "<table border=1 style='width: 500px;max-width: 100%'><tr><td>Bank</td><td>FNB</td></tr><tr><td>Beneficiary Name</td><td>The CharterQuest Professional Education Institute</td></tr><tr><td>Account Type</td><td>Current Account</td></tr><tr><td>Account No</td><td>62680767054</td></tr><tr><td>Branch Code</td><td>256755</td></tr></table>"
                body_html += "<br><br>"
                body_html += "We look forward seeing you during our course and helping you in achieving a 1st Time Pass!"
                body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Professional Education Institute<br>"
                body_html += "CENTRAL CONTACT INFORMATION:<br> Tel: +27 (0)11 234 9223 [SA & Intl]<br> Cell: +27 (0)73 174 5454 [SA & Intl]<br> <br/><div>"
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
                msg_id = mail_obj.create(mail_values)
                msg_id.send()
                if user_select.get('self_or_company') == 'cmp_sponosored':
                    return request.render('cfo_snr_jnr.enrolment_process_page_thankyou_bank',
                                          {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                              'self_or_company') else ''})
        return request.render('cfo_snr_jnr.enrolment_process_page_thankyou_bank')

    @http.route(['/pay/thankyou'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def pay_thankyou(self, **post):
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

        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
        for each_order_line in sale_order_id.order_line:
            invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                                        'name': each_order_line.name,
                                        'quantity': 1.0,
                                        'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
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
        if sale_order_id.debit_order_mandat:
            for each_debit_order in sale_order_id.debit_order_mandat:
                debit_order_obj.create({'partner_id': sale_order_id.partner_id.id,
                                        'student_number': '',
                                        'dbo_amount': each_debit_order.dbo_amount,
                                        'course_fee': each_debit_order.course_fee,
                                        'interest': each_debit_order.interest,
                                        'acc_holder': sale_order_id.partner_id.name,
                                        'bank_name': each_debit_order.bank_name.id,
                                        'bank_acc_no': each_debit_order.bank_acc_no,
                                        'bank_code': each_debit_order.bank_name.bic,
                                        'state': 'pending',
                                        'bank_type_id': each_debit_order.bank_type_id.id,
                                        'invoice_id': invoice_id.id
                                        })

        template_id = request.env['mail.template'].sudo().search([('name', '=', 'Fees Pay Later Email')])
        if template_id:
            # template_id.send_mail(sale_order_id.id, force_send=True)
            if sale_order_id.affiliation == '1':
                pdf_data = request.env.ref('event_price_kt.report_enrollment_invoice').render_qweb_pdf(invoice_id.id)
                pdf_data_statement_invoice = request.env.ref(
                    'event_price_kt.report_statement_enrollment').render_qweb_pdf(invoice_id.id)
                if pdf_data:
                    pdfvals = {'name': 'Invoice',
                               'db_datas': base64.b64encode(pdf_data[0]),
                               'datas': base64.b64encode(pdf_data[0]),
                               'datas_fname': 'Invoice.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].create(pdfvals)
                    attchment_list.append(pdf_create)

                if pdf_data_statement_invoice:
                    pdfvals = {'name': 'Enrolment Statement',
                               'db_datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas_fname': 'Enrolment Statement.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].create(pdfvals)
                    attchment_list.append(pdf_create)

                agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                if agreement_id:
                    attchment_list.append(agreement_id)

                baking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                if baking_detail_id:
                    attchment_list.append(baking_detail_id)

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
                    'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
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

        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
        # if request.session.get('do_invoice') == 'yes':
        sale_order_id.write({'state': 'sale'})
        for each_order_line in sale_order_id.order_line:
            invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                                        'name': each_order_line.name,
                                        'quantity': 1.0,
                                        'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
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
        if sale_order_id.debit_order_mandat:
            for each_debit_order in sale_order_id.debit_order_mandat:
                debit_order_obj.create({'partner_id': sale_order_id.partner_id.id,
                                        'student_number': '',
                                        'dbo_amount': each_debit_order.dbo_amount,
                                        'course_fee': each_debit_order.course_fee,
                                        'interest': each_debit_order.interest,
                                        'acc_holder': sale_order_id.partner_id.name,
                                        'bank_name': each_debit_order.bank_name.id,
                                        'bank_acc_no': each_debit_order.bank_acc_no,
                                        'bank_code': each_debit_order.bank_name.bic,
                                        'state': 'pending',
                                        'bank_type_id': each_debit_order.bank_type_id.id,
                                        'invoice_id': invoice_id.id
                                        })

        template_id = request.env['mail.template'].sudo().search([('name', '=', 'Fees Pay Later Email')])
        if template_id:
            # template_id.send_mail(sale_order_id.id, force_send=True)
            if sale_order_id.affiliation == '1':
                pdf_data = request.env.ref('event_price_kt.report_enrollment_invoice').render_qweb_pdf(invoice_id.id)
                pdf_data_statement_invoice = request.env.ref('event_price_kt.report_statement_enrollment').render_qweb_pdf(invoice_id.id)
                if pdf_data:
                    pdfvals = {'name': 'Invoice',
                               'db_datas': base64.b64encode(pdf_data[0]),
                               'datas': base64.b64encode(pdf_data[0]),
                               'datas_fname': 'Invoice.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].create(pdfvals)
                    attchment_list.append(pdf_create)

                if pdf_data_statement_invoice:
                    pdfvals = {'name': 'Enrolment Statement',
                               'db_datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas_fname': 'Enrolment Statement.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].create(pdfvals)
                    attchment_list.append(pdf_create)

                agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                if agreement_id:
                    attchment_list.append(agreement_id)

                baking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                if baking_detail_id:
                    attchment_list.append(baking_detail_id)

                body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                body_html += "<br>"
                body_html += "Dear " + sale_order_id.partner_id.name + ","
                body_html += "<br><br>"
                body_html += "Thank you for your enrolment and Please send your proof of payment to confirm your payment!"
                body_html += "<br><br>"
                body_html += "For your records, please find attached Invoice/Full Statement, copy of the Student Agreement as well as the Debit Order Mandate you just accepted Online during enrolment."
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
                    'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
                    'auto_delete': False,
                }
                msg_id = mail_obj.create(mail_values)
                msg_id.send()
                if user_select.get('self_or_company') == 'cmp_sponosored':
                    return request.render('cfo_snr_jnr.enrolment_process_page_thankyou',
                                          {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                              'self_or_company') else ''})

            if sale_order_id.affiliation == '2' and request.session.get('sale_order') and request.session.get('do_invoice') == 'yes':
                pdf_data = request.env.ref('event_price_kt.report_enrollment_invoice').render_qweb_pdf(
                    invoice_id.id)
                pdf_data_statement_invoice = request.env.ref(
                    'event_price_kt.report_statement_enrollment').render_qweb_pdf(invoice_id.id)

                if pdf_data:
                    pdfvals = {'name': 'Invoice',
                               'db_datas': base64.b64encode(pdf_data[0]),
                               'datas': base64.b64encode(pdf_data[0]),
                               'datas_fname': 'Invoice.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].create(pdfvals)
                    attchment_list.append(pdf_create)

                if pdf_data_statement_invoice:
                    pdfvals = {'name': 'Enrolment Statement',
                               'db_datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas': base64.b64encode(pdf_data_statement_invoice[0]),
                               'datas_fname': 'Enrolment Statement.pdf',
                               'res_model': 'account.invoice',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].create(pdfvals)
                    attchment_list.append(pdf_create)

                agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')
                if agreement_id:
                    attchment_list.append(agreement_id)

                baking_detail_id = request.env.ref('cfo_snr_jnr.banking_data_pdf')
                if baking_detail_id:
                    attchment_list.append(baking_detail_id)

                body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                body_html += "<br>"
                body_html += "Dear " + sale_order_id.partner_id.name + ","
                body_html += "<br><br>"
                body_html += "Thank you for your Enrolment Application."
                body_html += "<br><br>"
                body_html += "Please find	attached Invoice as	well as	copy of	the	Student	Agreement you just accepted	during enrolment."
                body_html += "<br><br>"
                body_html += "Your sponsor/company can pay using the Invoice no. as reference and return proof of payment to: accounts@charterquest.co.za"
                body_html += " to process your enrolment. You can email accounts should you wish to make special payment arrangements."
                body_html += "<br><br>"
                body_html += "Should your company require	an invoice, please forward this	proforma to	the	above email requesting its conversion into an invoice. We will need your company's details to generate an invoice for you!"
                body_html += "<br><br>"
                body_html += "Once we issue an invoice, this becomes binding as you will be	expected to	settle the amount in full should your company not honour the agreement. So please kindly ensure your company has pre-approved your bursary or training expenditure before you request conversion to an Invoice."
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
                msg_id = mail_obj.create(mail_values)
                msg_id.send()
                if user_select.get('self_or_company') == 'cmp_sponosored':
                    return request.render('cfo_snr_jnr.enrolment_process_page_thankyou',
                                          {'self_or_cmp': user_select['self_or_company'] if user_select.get(
                                              'self_or_company') else ''})
            if sale_order_id.affiliation == '2' and request.session.get('sale_order') and request.session.get('do_invoice') == 'no':
                pdf_data_enroll = request.env.ref('event_price_kt.report_sale_enrollment').render_qweb_pdf(
                    sale_order_id.id)
                enroll_file_name = "Pro-Forma " + sale_order_id.name
                if pdf_data_enroll:
                    pdfvals = {'name': enroll_file_name,
                               'db_datas': base64.b64encode(pdf_data_enroll[0]),
                               'datas': base64.b64encode(pdf_data_enroll[0]),
                               'datas_fname': enroll_file_name+'.pdf',
                               'res_model': 'sale.order',
                               'type': 'binary'}
                    pdf_create = request.env['ir.attachment'].create(pdfvals)
                    attchment_list.append(pdf_create)

                agreement_id = request.env.ref('cfo_snr_jnr.term_and_condition_pdf_enrolment')

                if agreement_id:
                    attchment_list.append(agreement_id)

                body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                body_html += "<br>"
                body_html += "Dear " + sale_order_id.partner_id.name + ","
                body_html += "<br><br>"
                body_html += "Thank you for your Enrolment Application."
                body_html += "<br><br>"
                body_html += "Please find attached proforma Invoice as	well as	copy of	the	Student	Agreement you just accepted	during enrolment."
                body_html += "<br><br>"
                body_html += "Your sponsor/company can pay using the Invoice no. as reference and return proof of payment to: accounts@charterquest.co.za"
                body_html += " to process your enrolment. You can email accounts should you wish to make special payment arrangements."
                body_html += "<br><br>"
                body_html += "Should your company require	an invoice, please forward this	proforma to	the	above email requesting its conversion into an invoice. We will need your company's details to generate an invoice for you!"
                body_html += "<br><br>"
                body_html += "Once we issue an invoice, this becomes binding as you will be	expected to	settle the amount in full should your company not honour the agreement. So please kindly ensure your company has pre-approved your bursary or training expenditure before you request conversion to an Invoice."
                body_html += "<br><br>"
                body_html += "We look forward to seeing you during our course and helping you, in achieving a 1st Time Pass!"
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
                msg_id = mail_obj.create(mail_values)
                msg_id.send()
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
                                              'dbo_amount': post.get('inputOutstanding') if post.get('inputOutstanding') else 0,
                                              'course_fee': post.get('inputOutstanding') if post.get('inputOutstanding') else 0,
                                              'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                                              'interest': post.get('inputInterest') if post.get('inputInterest') else 0,
                                              'acc_holder': sale_order_id.partner_id.name,
                                              'bank_name': res_bank_detail.id if res_bank_detail else '',
                                              'bank_acc_no': post.get('inputAccount') if post.get('inputAccount') else '',
                                              'bank_code': res_bank_detail.bic if res_bank_detail else '',
                                              'bank_type_id': int(post['inputAtype']) if post.get('inputAtype') else ''}])

            sale_order_id.write({'diposit_selected': post.get('inputPaypercentage') if post.get('inputPaypercentage') else 0,
                                 'due_amount': post.get('inputTotalDue') if post.get('inputTotalDue') else 0,
                                 'months': post.get('inputPaymonths') if post.get('inputPaymonths') else 0,
                                 'out_standing_balance_incl_vat': post.get('inputtotalandInterest') if post.get('inputtotalandInterest') else 0,
                                 'monthly_amount': post.get('inputpaymentpermonth') if post.get('inputpaymentpermonth') else 0,
                                 'outstanding_amount': post.get('inputOutstanding') if post.get('inputOutstanding') else 0,
                                 'interest_amount': post.get('inputInterest') if post.get('inputInterest') else 0,
                                 'debit_order_mandat': debit_order_mandet})

        if post.get('Pay Via Bank Deposit'):
            return request.render('cfo_snr_jnr.enrolment_process_validate_payment', {'post_data': post if post else '', 'button_hide':True})
        else:
            return request.render('cfo_snr_jnr.enrolment_process_validate_payment', {'post_data': post if post else '', 'button_hide':False})

    @http.route(['/registration_and_enrol'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def registration_and_enrol(self, **post):
        if post:
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

            account_rec_type_id = request.env['account.account.type'].sudo().search([('name', 'ilike', 'Receivable')])
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
            if not partner_id:
                res_partner_obj.create({'name': name,
                                        'student_company': post.get('inputCompany') if post.get('inputCompany') else '',
                                        'email': post.get('inputEmail') if post.get('inputEmail') else '',
                                        'vat_no_comp': post.get('inputVat') if post.get('inputVat') else '',
                                        'idpassport': post.get('inputID_PassportNo.') if post.get('inputID_PassportNo.') else '',
                                        'cq_password': post.get('inputPassword') if post.get('inputPassword') else '',
                                        'mobile': post.get('inputContactNumber') if post.get('inputContactNumber') else '',
                                        'street': post.get('inputStreet') if post.get('inputStreet') else '',
                                        'street2': post.get('inputStreet2') if post.get('inputStreet2') else '',
                                        'city': post.get('inputCity') if post.get('inputCity') else '',
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
                                  'idpassport': post.get('inputID_PassportNo.') if post.get('inputID_PassportNo.') else '',
                                  'cq_password': post.get('inputPassword') if post.get('inputPassword') else '',
                                  'mobile': post.get('inputContactNumber') if post.get('inputContactNumber') else '',
                                  'street': post.get('inputStreet') if post.get('inputStreet') else '',
                                  'street2': post.get('inputStreet2') if post.get('inputStreet2') else '',
                                  'city': post.get('inputCity') if post.get('inputCity') else '',
                                  'zip': post.get('inputZip') if post.get('inputZip') else '',
                                  'findout': post.get('inputFindout') if post.get('inputFindout') else '',
                                  'prof_body_id': post.get('inputId') if post.get('inputId') else '',
                                  'property_account_receivable_id': account_rec_id.id,
                                  'property_account_payable_id': account_pay_id.id})
            request.session['reg_and_enrol'] = 'yes'
            request.session['reg_and_enrol_email'] = post.get('inputEmail') if post.get('inputEmail') else ''
            request.session['do_invoice'] = 'yes' if post.get('do_invoice') == 'Yes' else 'no'
            return request.redirect('/payment')
        return request.render('cfo_snr_jnr.enrolment_process_registration_and_enroll', {'page_name': 'registration'})
