# -*- coding: utf-8 -*-
import odoo
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import werkzeug.urls
from werkzeug.exceptions import NotFound

from odoo.addons.http_routing.models.ir_http import slug
from odoo import tools
from odoo.http import request, _logger
from odoo.tools.translate import _
from odoo import SUPERUSER_ID
import re
import json
import hashlib
# import pyDes
import urllib3
import base64
import simplejson
import requests
from odoo import http
from odoo.http import request


class website_event(http.Controller):

    @http.route(['/customer_unsubscribe', ], type='http', auth="public", website=True)
    def customer_unsubscribe(self, **post):
        return request.website.render('kt_website_event.UnsubscribePage')

    ## Magazine Unsubscribe
    @http.route(['/magazine/unsubscribe/<rec>', ], type='http', auth="public", website=True)
    def magazine_unsubscribe(self, **post):
        if post:
            partner_id = request.env['res.partner'].sudo().browse(int(post.get('rec')))

            if partner_id:
                partner_id.write({'magazine_opt_out': True})
            # return request.redirect("/magazine/unsubscribe")
        return request.website.render('kt_website_event.unsubscribePagemagazine')

    @http.route(['/magazine/signin', ], type='http', auth="public", website=True)
    def magazine_signin(self, **post):
        session = request.session
        if post:
            ids = request.env['res.partner'].search(['|', ('email', '=ilike', post.get('email2')),
                                                     ('email_1', '=ilike', post.get('email2'))])
            if ids:
                is_subscriber = request.env['res.partner'].browse(ids[0]).is_subscriber
                if not is_subscriber:
                    return request.website.render('kt_website_event.magazine_signin',
                                                  {'message': 'Please activate your account to continue.'})
                else:
                    session['is_signed'] = True
                    ## Raaj commented and added
                    return request.redirect('/magazine/october_16')
                    # return request.redirect(session['re_url'])
            else:
                return request.website.render('kt_website_event.magazine_signin',
                                              {'message': 'Please Subscribe to continue.'})

        return request.render("kt_website_event.magazine_signin")

    @http.route(['/magazine/signout', ], type='http', auth="public", website=True)
    def magazine_signout(self, **post):
        session = request.session
        session['is_signed'] = False
        return request.render("kt_website_event.magazine_signout")

    # @http.route(['/magazine/reset-password'], type='http', auth='public', website=True)
    # def reset_password_magazine(self, **post):
    #     ids = []
    #     if post:
    #         # for obj in map_magazine_types.keys():
    #         obj = 'res.partner'
    #         ids = request.env[obj].search([('email', '=ilike', post.get('email'))])
    #         if ids:
    #             record = request.env[obj].browse(ids[0])
    #             data = 'res.partner'
    #             k = pyDes.triple_des("fFf48IOJ6gGaqXKg", pyDes.CBC, False, pad=None, padmode=pyDes.PAD_PKCS5)
    #             d = k.encrypt(str(data))
    #             enc = d.encode('base64')
    #             enc = urllib3.quote(enc)
    #             mail_vals = {
    #                 'email_from': 'futurecfomagazine@charterquest.co.za',
    #                 'email_to': post.get('email'),
    #                 'email_cc': 'futurecfomagazine@charterquest.co.za',
    #                 'subject': 'The Magazine Subscriber Password Reset',
    #                 # 'body_html': reset_template_1 + reset_template_2.format(record.name, record.surname, enc,
    #                 #                                                         str(record.cfo_encoded_link), enc,
    #                 #                                                         str(record.cfo_encoded_link), enc,
    #                 #                                                         str(record.cfo_encoded_link)),
    #             }
    #             res = request.env['mail.mail'].create(mail_vals)
    #             return request.redirect('/magazine/reset-password-status?status=mail_sent')
    #         #                   return request.website.render('kt_website_event.reset_password',{'success':'An email has been sent with credentials to reset your password'})
    #         else:
    #             return request.website.render('kt_website_event.reset_password',
    #                                           {'error': 'Reset Password: Invalid Email'})
    #     return request.website.render('kt_website_event.reset_password')

    @http.route(['/magazine/reset-password-status'], type='http', auth='public', website=True)
    def reset_password_status(self, **post):
        if post.get('status') == 'mail_sent':
            return request.website.render('kt_website_event.reset_password_status',
                                          {'message': 'An email has been sent with credentials to reset your password'})
        if post.get('status') == 'reset_success':
            return request.website.render('kt_website_event.reset_password_status',
                                          {'message': 'Your password has been successfully updated.'})

    @http.route(['/magazine/reset-magazine-password/<link>'], type='http', auth='public', website=True)
    def reset_magazine_password(self, **post):
        if post:
            cfo_encoded_link = post.get('link')
            obj = "res.partner"
            try:
                if obj:
                    ids = request.env[obj].search([('cfo_encoded_link', '=', post.get('link'))])
                    if ids:
                        record = request.env[obj].browse(ids[0])
                        return request.website.render('kt_website_event.reset_magazine_password',
                                                      {'obj': obj, 'link': post.get('link'), 'record': record})
                    else:
                        return request.website.render('website_sale.404')
            except Exception as e:
                _logger.error('%s' % e)
                return request.website.render('website_sale.404')

    @http.route(['/magazine/reset_magazine_account/'], type='http', auth='public', website=True)
    def reset_magazine_account(self, **post):
        if post:
            ids = request.env[post.get('obj')].search([('cfo_encoded_link', '=', post.get('link'))])
            if ids:
                ids.write({'password': post.get('password')})
                return request.redirect('/magazine/reset-password-status?status=reset_success')

    @http.route(['/magazine/subscription'], type='http', auth="public", website=True)
    def magazine_subscription(self, **post):
        session = request.session
        country_ids = request.env['res.country'].search([])
        country_list = request.env['res.country'].read(country_ids, ['name'])

        ip = request.httprequest.environ['HTTP_X_FORWARDED_FOR']
        url = 'http://freegeoip.net/json/' + ip
        r = requests.get(url)
        js = r.json()

        country_id = request.env['res.country'].search([('name', '=', js['country_name'])])[0] or False
        state_id = request.env['res.country.state'].search([('name', '=', js['region_name'])])
        if state_id:
            state_id = state_id[0]
        if not state_id:
            request.env['res.country.state'].create({'name': js['region_name'], 'code': js['region_code'],
                                                     'country_id': country_id})

        # post.update({'is_subscriber' : False})
        request.context.update({'is_subscriber': False})
        if post and not request.context['is_subscriber']:
            post.update({'city': js['city'], 'state_id': state_id, 'country_id': country_id, 'zip': js['zip_code'],
                         'subscriber_state_id': state_id, 'subscriber_country_id': country_id})
            partner = request.env['res.partner']
            res_id = partner.search(['|', ('email', '=ilike', post.get('email')),
                                     ('email_1', '=ilike', post.get('email'))])
            if res_id:
                # partner.write(cr, SUPERUSER_ID, res_id, post)
                res_id = res_id[0]
                res_id.write(post)
            else:
                res_id = partner.create(post)

            blog = request.env['blog.blog']
            blog_id = blog.search([('name', '=', "The Future CFO Magazine")])
            res = blog_id.write({'message_follower_ids': (4, res_id)})
            record = partner.browse(res_id)
            mail_vals = {
                'email_from': 'futurecfomagazine@charterquest.co.za',
                'email_to': record.email or record.email_1,
                'email_cc': 'futurecfomagazine@charterquest.co.za',
                'subject': 'Subscription Confirmation Email',
                # 'body_html': email_template_1 + email_template_for_activate.format(record.name, record.email,
                #                                                                    record.email, record.email, res_id),
            }

            res = request.env['mail.mail'].create(mail_vals)

            return request.redirect("/magazine/subscription_success")
        return request.render("kt_website_event.magazine_subscription_page")

    ## Raaj Added for Activation  <!-- Deploy to live -->
    @http.route(['/magazine/account_activate/<email>'], type='http', auth='public', website=True)
    def account_activate_magazine(self, **post):
        obj = "res.partner"
        if post:
            partner_id = request.env[obj].search(['|', ('email', 'ilike', post.get('email')),
                                                  ('email_1', 'ilike', post.get('email'))])
            if partner_id:
                is_subscriber = partner_id.is_subscriber
                if not is_subscriber:
                    partner_id.write({'is_subscriber': True})
                    data = partner_id
                    mail_vals = {
                        'email_from': 'futurecfomagazine@charterquest.co.za',
                        'email_to': data.email,
                        'email_cc': 'futurecfomagazine@charterquest.co.za',
                        'subject': 'The Magazine Account Activation Confirmation',
                        # 'body_html': email_template_1 + email_template_activate_success.format(
                        #     data.name) + email_template_3,
                    }
                    res = request.env['mail.mail'].create(mail_vals)
                    return request.website.render('kt_website_event.activationsuccessPagemagazine')
                elif is_subscriber:
                    return request.website.render('kt_website_event.magazine-activation-already-activated')
                else:
                    return request.website.render('kt_website_event.magazine-activation-failed')

    @http.route(['/magazine/subscription_success'], type='http', auth="public", website=True)
    def magazine_subscription_success(self, **post):
        return request.render("kt_website_event.magazine_subscription_success_page")

    @http.route(['/subscriber/email_validation'], type='http', auth='public', website=True)
    def subscriber_email_validation(self, **post):
        if post:
            email = post.get('email')
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return json.dumps({'error': 'Entered email is not valid, Please enter in the form xxxxxx@domain.com '})
                return json.dumps({'valid': 'Email is valid'})
            partner = request.env['res.partner']
            subscriber = partner.search([('email', '=', email), ('is_subscriber', '=', True)])
            if subscriber:
                return json.dumps({'error': 'Email already exists'})

    ## <!-- Deploy to live -->
    @http.route(['/subscriber/email_validation2'], type='http', auth='public', website=True)
    def subscriber_email_validation2(self, **post):
        if post:
            email2 = post.get('email2')
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email2):
                return json.dumps({'error': 'Entered email is not valid, Please enter in the form xxxxxx@domain.com '})

    @http.route(['/magazine_preview', ], type='http', auth="public", website=True)
    def magazine_preview(self):
        return request.render("kt_website_event.magazine_preview")

    @http.route(['/magazines', ], type='http', auth="public", website=True)
    def magazines(self, **post):
        return request.render("kt_website_event.magazine_page")

    @http.route(['/magazine/october_16'], type='http', auth="public", website=True)
    def magazine_october_16(self, **post):
        session = request.session
        if session.get('is_signed'):
            return request.render("kt_website_event.magazine_october_16")
        else:
            session['re_url'] = "/magazine/october_16"
            return request.render("kt_website_event.magazine_signin")

    @http.route(['/magazine/january_17'], type='http', auth="public", website=True)
    def magazine_january_16(self, **post):
        session = request.session
        if session.get('is_signed'):
            return request.render("kt_website_event.magazine_january_17")
        else:
            session['re_url'] = "/magazine/january_17"
            return request.render("kt_website_event.magazine_signin")

    @http.route(['/magazine/april_17'], type='http', auth="public", website=True)
    def magazine_april_16(self, **post):
        session = request.session
        if session.get('is_signed'):
            return request.render("kt_website_event.magazine_april_17")
        else:
            session['re_url'] = "/magazine/april_17"
            return request.render("kt_website_event.magazine_signin")

    @http.route(['/magazine/july_17'], type='http', auth="public", website=True)
    def magazine_january_16(self, **post):
        session = request.session
        if session.get('is_signed'):
            return request.render("kt_website_event.magazine_july_17")
        else:
            session['re_url'] = "/magazine/july_17"
            return request.render("kt_website_event.magazine_signin")

    @http.route(['/magazine/october_17'], type='http', auth="public", website=True)
    def magazine_january_16(self, **post):
        session = request.session
        if session.get('is_signed'):
            return request.render("kt_website_event.magazine_october_17")
        else:
            session['re_url'] = "/magazine/october_17"
            return request.render("kt_website_event.magazine_signin")

    @http.route(['/magazine/previous_issues'], type='http', auth="public", website=True)
    def magazine_previous_issues(self, **post):
        session = request.session
        if session.get('is_signed'):
            return request.render("kt_website_event.magazine_previous_issues")
        else:
            return request.render("kt_website_event.magazine_signin")

    ##ENd

    @http.route(['/event/<model("event.event"):event>/register'], type='http', auth="public", website=True)
    def event_register(self, event, **post):
        # if not request.context.get('tz', False):
        #     request.context.update({'tz': 'Africa/Johannesburg'})
        values = {
            'event': event,
            'main_object': event,
            'range': range,
        }
        return request.render("website_event.event_description_full", values)

    # overrided method to show only fixed number of events
    @http.route(['/event', '/event/page/<int:page>'], type='http', auth="public", website=True)
    def events(self, page=1, **searches):
        event_obj = request.env['event.event']
        type_obj = request.env['event.type']
        country_obj = request.env['res.country']

        searches.setdefault('date', 'all')
        searches.setdefault('type', 'all')
        searches.setdefault('country', 'all')

        domain_search = {}

        def sdn(date):
            return date.strftime('%Y-%m-%d 23:59:59')

        def sd(date):
            return date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        today = datetime.today()
        dates = [
            ['all', _('Next Events'), [("date_end", ">", sd(today))], 0],
            ['today', _('Today'), [
                ("date_end", ">", sd(today)),
                ("date_begin", "<", sdn(today))],
             0],
            ['week', _('This Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=6 - today.weekday())))],
             0],
            ['nextweek', _('Next Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=7 - today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=13 - today.weekday())))],
             0],
            ['month', _('This month'), [
                ("date_end", ">=", sd(today.replace(day=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))],
             0],
            ['nextmonth', _('Next month'), [
                ("date_end", ">=", sd(today.replace(day=1) + relativedelta(months=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=2)).strftime('%Y-%m-%d 00:00:00'))],
             0],
            ['old', _('Old Events'), [
                ("date_end", "<", today.strftime('%Y-%m-%d 00:00:00'))],
             0],
        ]
        # search domains
        current_date = None
        current_type = None
        current_country = None
        for date in dates:
            if searches["date"] == date[0]:
                domain_search["date"] = date[2]
                if date[0] != 'all':
                    current_date = date[1]
        if searches["type"] != 'all':
            current_type = type_obj.browse(int(searches['type']))
            domain_search["type"] = [("type", "=", int(searches["type"]))]

        if searches["country"] != 'all' and searches["country"] != 'online':
            current_country = country_obj.browse(int(searches['country']))
            domain_search["country"] = ['|', ("country_id", "=", int(searches["country"])), ("country_id", "=", False)]
        elif searches["country"] == 'online':
            domain_search["country"] = [("country_id", "=", False)]

        # @change made here to display only the event_type records whose publish_on_website [on event_type master] boolean field is True.
        type_ids = type_obj.search([('publish_on_website', '=', True)])

        def dom_without(without):
            domain = [('state', "in", ['draft', 'confirm', 'done']), ('type', 'in', type_ids)]
            for key, search in domain_search.items():
                if key != without:
                    domain += search
            return domain

        # count by domains without self search
        for date in dates:
            if date[0] != 'old':
                date[3] = event_obj.search(dom_without('date') + date[2], count=True)
        domain = dom_without('type')
        types = event_obj.read_group(domain, ["id", "type"], groupby="type", orderby="type")
        type_count = event_obj.search(domain, count=True)
        types.insert(0, {
            'type_count': type_count,
            'type': ("all", _("All Categories"))
        })

        domain = dom_without('country')
        countries = event_obj.read_group(domain, ["id", "country_id"], groupby="country_id", orderby="country_id")
        country_id_count = event_obj.search(domain, count=True)
        countries.insert(0, {
            'country_id_count': country_id_count,
            'country_id': ("all", _("All Countries"))
        })
        step = 10  # Number of events per page
        event_count = event_obj.search(dom_without("none"), count=True)
        pager = request.website.pager(
            url="/event",
            url_args={'date': searches.get('date'), 'type': searches.get('type'), 'country': searches.get('country')},
            total=event_count,
            page=page,
            step=step,
            scope=5)

        order = 'website_published desc, date_begin'
        if searches.get('date', 'all') == 'old':
            order = 'website_published desc, date_begin desc'
        if not request.context.get('tz', False):
            request.context.update({'tz': 'Africa/Johannesburg'})
        obj_ids = event_obj.search(dom_without("none"), limit=step, offset=pager['offset'], order=order)

        events_ids = event_obj.browse(obj_ids)

        values = {
            'current_date': current_date,
            'current_country': current_country,
            'current_type': current_type,
            'event_ids': events_ids,
            'dates': dates,
            'types': types,
            'countries': countries,
            'pager': pager,
            'searches': searches,
            'search_path': "?%s" % werkzeug.url_encode(searches),
        }
        return request.website.render("website_event.index", values)

    # overrided to redirect form in case of free event tickets
    @http.route(['/event/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, event_id, **post):
        cr, uid, context = request.cr, request.uid, request.context
        ticket_obj = request.env['event.event.ticket']

        sale = False
        for key, value in post.items():
            quantity = int(value or "0")
            if not quantity:
                continue
            sale = True
            ticket_id = key.split("-")[0] == 'ticket' and int(key.split("-")[1]) or None
            ticket = ticket_obj.browse(ticket_id)
            if ticket.is_free:
                event = request.env['event.event'].browse(cr, uid, int(event_id))
                return request.redirect("/open_day_register/%s/%s/%s" % (slug(event), slug(ticket), quantity))
            order = request.website.sale_get_order(force_create=1)
            order.with_context(event_ticket_id=ticket.id)._cart_update(product_id=ticket.product_id.id,
                                                                       add_qty=quantity)

        if not sale:
            return request.redirect("/event/%s" % event_id)
        return request.redirect("/shop/checkout")

    # registration form for free event tickets - new method
    @http.route(
        ['/open_day_register/<model("event.event"):event>/<model("event.event.ticket"):event_ticket>/<quantity>'],
        type='http', auth="public", website=True)
    def open_day_register(self, event, event_ticket, quantity, **post):
        values = {'event': event, 'ticket': event_ticket, 'quantity': quantity}
        error_flag = False
        if post == None: post = {}
        if post:
            if not post.get('name'):
                values.update({'error_name': '* Required'})
                error_flag = True
            if not post.get('email'):
                error_flag = True
                values.update({'error_email': '* Required'})
            if not post.get('mobile'):
                error_flag = True
                values.update({'error_mobile': '* Required'})
            if error_flag:
                values.update({'post': post})
                return request.website.render("kt_website_event.open_day_register", values)
            vals = {
                'name': post.get('name'),
                'email': post.get('email'),
                'phone': post.get('mobile'),
                'event_id': event.id,
                'event_ticket_id': event_ticket.id,
                'nb_register': int(quantity),
                'state': 'open',
            }

            reg_id = request.env['event.registration'].create(vals)
            template_id = request.env['event.registration'].browse(reg_id).event_id.email_registration_id.id
            if template_id:
                request.env['email.template'].send_mail(template_id, reg_id)
            return request.redirect("/open_day_register/confirm")
        return request.website.render("kt_website_event.open_day_register",
                                      {'event': event, 'ticket': event_ticket, 'quantity': quantity})

    # confirmation form - new method
    @http.route(['/open_day_register/confirm'], type='http', auth="public", website=True)
    def open_day_register_confirm(self, **post):
        return request.website.render("kt_website_event.open_day_register_confirm")
