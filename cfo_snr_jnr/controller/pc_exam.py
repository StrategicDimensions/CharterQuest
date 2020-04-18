import hashlib
import time
# import date_converter
from urllib.parse import urljoin
import logging
import werkzeug
from dateutil.relativedelta import relativedelta
from odoo.http import request
from datetime import date, datetime, timedelta
import json, base64
from odoo import http, SUPERUSER_ID, _
from odoo.addons.payment_payu_com.controllers.main import PayuController
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)




class PCExambooking(http.Controller):

    # select_exam_list = []
    @http.route(['/registerPB','/reschedulePB/<uuid>'], type='http', auth="public", methods=['POST', 'GET'], website=True,
                csrf=False)
    def pc_exam_form_render(self,uuid=False, **post):
        sale_order_id = False
        event_id = False
        reschedule_time=0.0
        campus_ids_lst = []
        campus_lst = []
        reschedule_campus_ids_lst = []
        reschedule_campus_lst = []
        print("\n\n\n\n\n============uuid============", uuid)
        event_ids = request.env['event.event'].sudo().search([])
        campus_ids = request.env['res.partner'].sudo().search([('is_campus','=', True)])

        for campus in campus_ids:
            for exam_campus in event_ids:
                if campus in exam_campus.address_ids:
                    if exam_campus.pc_exam == True:
                        campus_ids_lst.append(campus.id)

        for campus_exam in campus_ids_lst:
            if campus_exam not in campus_lst:
                campus_lst.append(campus_exam)

        print("\n\n\n\n=====campus lst====",campus_lst)
        if uuid:
            uuid_lst = uuid.split('&')
            print("\n\n\n\n\n\n=====uuid_lst=====",uuid_lst)
            sale_order_id = request.env['sale.order'].sudo().search([('debit_link','=',uuid_lst[0])])
            event_id = request.env['event.event'].sudo().search([('id','=',uuid_lst[1])])
            print("\n\n\n\n\n==========event_id line=========", event_id)
            event_reschedule_ids = request.env['event.event'].sudo().search([('name','=',event_id.name),('type_pc_exam','=',event_id.type_pc_exam.name),('subject','=',event_id.subject.name),('qualification','=',event_id.qualification.name)])
        if sale_order_id and event_id:

            today = datetime.now()
            print("\n\n\n\n\n====today date===",today)
            # for order_line in sale_order_id.order_line:
            #     if order_line.event_id.date_begin:
            event_date=datetime.strptime(event_id.date_begin, '%Y-%m-%d %H:%M:%S')
            print("\n\n\n\n\n====event_date date===",event_date)
            time_diff = event_date - today
            reschedule_time = time_diff.total_seconds()
            # if reschedule_time < 0:
            #     reschedule_time= - reschedule_time
            print("\n\n\n\n====time_diff==",reschedule_time)
            if event_reschedule_ids:
                for campus in campus_ids:
                    for exam_campus in event_reschedule_ids:
                        if campus in exam_campus.address_ids:
                            if exam_campus.pc_exam == True:
                                reschedule_campus_ids_lst.append(campus.id)

                for campus_exam in reschedule_campus_ids_lst:
                    if campus_exam not in reschedule_campus_lst:
                        reschedule_campus_lst.append(campus_exam)

        if reschedule_time < 172800 and reschedule_time != 0.0:
            return request.render('cfo_snr_jnr.exam_reschedule_fail')

        else:
            return request.render('cfo_snr_jnr.pc_exam_process_form', {'page_name': 'campus',
                                                                       'uuid': uuid,
                                                                       'sale_order_id': sale_order_id.id if sale_order_id else False,
                                                                       'campus_ids_lst':campus_lst if campus_lst else False,
                                                                       'event_id':event_id.id if event_id else False,
                                                                       'reschedule_campus_lst':reschedule_campus_lst if reschedule_campus_lst else False
                                                                       })

    @http.route(['/reg'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def pc_exam_type_reg(self, **post):
        examtype_ids = []
        exam_type_ids = []
        print('\n\n\n\n\n=======post======',post,type((post.get('Select Campus'))))

        event_ids = request.env['event.event'].sudo().search([])
        print("\n\n\n\n========event_id====",event_ids)
        for event in event_ids:
            if int(post.get('Select Campus')) in event.address_ids.ids:
                if event.type_pc_exam:
                    examtype_ids.append(event.type_pc_exam)
        print("\n\n\n\n==exam_type======",examtype_ids)
        for exam_type in examtype_ids:
            if exam_type.id not in exam_type_ids:
                exam_type_ids.append(exam_type.id)
        print("\n\n\n\n==exam_type_ids======", exam_type_ids)
        value={}
        value['sale_order_id'] = int(post.get('sale_order_id')) if post.get('sale_order_id') else False
        value['event_id'] = int(post.get('event_id')) if post.get('event_id') else False
        value['uuid'] = post.get('uuid')
        value['campus'] = int(post.get('Select Campus'))
        value['page_name'] = post.get("page_name")
        value['exam_type_ids'] = exam_type_ids
        return request.render('cfo_snr_jnr.pc_exam_type_process_form', value)

    @http.route(['/pcexamsearch'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def pc_exam_search_reg(self, **post):
        print("\n\n\n\n\n\===========exam post======",post)
        examlevel_ids = []
        exam_level_ids = []
        examsubject_ids = []
        exam_subject_ids = []
        exam_type_id = request.env['pc.exam.type'].sudo().browse(int(post.get('Select Exam Type')))
        event_ids = request.env['event.event'].sudo().search([])
        print("\n\n\n\n========event_id====", event_ids)
        for event in event_ids:
            if int(post.get('campus')) in event.address_ids.ids and exam_type_id.name == event.type_pc_exam.name:
                if event.qualification:
                    examlevel_ids.append(event.qualification)
                    # if event.subject:
                    #     examsubject_ids.append((event.subject))
        for exam_level in examlevel_ids:
            if exam_level.id not in exam_level_ids:
                exam_level_ids.append(exam_level.id)
        print("\n\n\n\n==exam_level_ids======", exam_level_ids)
        # for exam_subject in examsubject_ids:
        #     if exam_subject.id not in exam_subject_ids:
        #         exam_subject_ids.append(exam_subject.id)
        # print("\n\n\n\n==exam_subject_ids======", exam_subject_ids)
        value={}

        value['campus'] = int(post.get('campus'))
        value['sale_order_id'] = int(post.get('sale_order_id')) if post.get('sale_order_id') else False
        value['event_id'] = int(post.get('event_id')) if post.get('event_id') else False
        value['page_name'] = post.get("page_name")
        value['select_exam_type'] = post.get('Select Exam Type')
        value['exam_level_ids'] = exam_level_ids
        # value['exam_subject_ids'] = exam_subject_ids
        print("\n\n\n\n\n=====value dict====",value)
        return request.render('cfo_snr_jnr.pc_exam_search_process_form', value)

    @http.route('/pc_exam_search', type='json', auth='public', website=True)
    def pc_exam_search_data(self, **post):
        exam_list=[]

        print("\n\n\n\n\n\===========exam data post======", post)
        exam_date = post.get('date')
        # str_exam_date = date_converter.date_to_datetime(exam_date)
        last_date = str(exam_date) + ' 23:59:59'
        str_exam_date = datetime.strptime(exam_date, '%m/%d/%Y')
        end_exam_date = datetime.strptime(last_date, '%m/%d/%Y %H:%M:%S')

        str_exam_date = str_exam_date.strftime("%m/%d/%Y %H:%M:%S")
        end_exam_date = end_exam_date.strftime("%m/%d/%Y %H:%M:%S")
        print("\n\n\n\n==========str_exam_date========",str_exam_date,type(str_exam_date))
        exam_ids = request.env['event.event'].sudo().search([('type_pc_exam.id','=',post.get('exam_type')),('date_begin','>=',str_exam_date),('date_end','<=',end_exam_date),('subject','=',(post.get('subject'))),('qualification.id','=',int(post.get("level"))),('address_ids','in',int(post.get('campus')))])
        print("\n\n\n==========exam_id====",exam_ids)

        if exam_ids:
            for exam in exam_ids:
                if exam.seats_available > 0 or exam.seat_availability == 'unlimited':
                    exam_dict = {}
                    print("\n\n\n\n=====time=====",datetime.strptime(exam.date_begin,'%Y-%m-%d %H:%M:%S').time())
                    print("\n\n\n\n=====time end=====", datetime.strptime(exam.date_end, '%Y-%m-%d %H:%M:%S').time())
                    exam_dict['subject_name']=exam.name
                    exam_dict['start_time']=exam.date_begin
                    exam_dict['end_time']=exam.date_end
                    exam_dict['price']= 0.0 if post.get('sale_order_id') else exam.price
                    exam_dict['seats_available']=exam.seats_available
                    exam_dict['exam_id']=exam.id
                    exam_list.append(exam_dict)
                    # print("\n\n\n\n===========list========",exam_list)
            return exam_list

    @http.route('/pc_exam_subject_search', type='json', auth='public', website=True)
    def pc_exam_subject_search(self, **post):
        exam_subject_list = []
        subject_list = []
        exam_date_lst = []

        print("\n\n\n\n\n\===========exam pc_exam_subject_search post======", post)
        exam_type_id = request.env['pc.exam.type'].sudo().browse(int(post.get('exam_type')))

        today_datetime = datetime.now() + timedelta(7)
        tody_date_format = today_datetime.strftime('X%d-X%m-%Y').replace('X0', 'X').replace('X', '')
        if post.get('level'):
            exam_level_id = request.env['event.qual'].sudo().browse(int(post.get('level')))
            event_ids = request.env['event.event'].sudo().search([])

            for event in event_ids:
                if int(post.get('campus')) in event.address_ids.ids and exam_type_id.name == event.type_pc_exam.name and exam_level_id.name == event.qualification.name:
                    if event.subject:
                        exam_subject_list.append(event.subject)
                    exam_date = event.date_end.split(" ")
                    print("\n\n\n\n\n===========exam_date types===", exam_date,exam_date[0])
                    datetimeobject = datetime.strptime(exam_date[0], '%Y-%m-%d')
                    newformat = datetimeobject.strftime('X%d-X%m-%Y').replace('X0', 'X').replace('X', '')
                    print("\n\n\n\n\n===========dates types===", type(tody_date_format), type(newformat),newformat)

                    date1 = datetime.strptime(tody_date_format, "%d-%m-%Y")
                    date2 = datetime.strptime(newformat, "%d-%m-%Y")
                    if date1 <= date2:
                        exam_date_lst.append(newformat)
            print("\n\n\n\n\n===========exam_subject_list========",exam_subject_list)
            for subject in exam_subject_list:
                if subject.name not in subject_list:
                    subject_list.append(subject.name)

            print("\n\n\n\n\n===========exam_subject_list=====subject_list===", subject_list)
            print("\n\n\n\n\n===========exam_date_lst=====exam_date_lst===", exam_date_lst)

            return {'subjects':subject_list,'dates':exam_date_lst}
    # @http.route('/set_available_seats', type='json', auth='public', website=True)
    # def set_available_seats(self, select_exam_list=select_exam_list, **post):
    #
    #     print("\n\n\n\n===========post========",post,select_exam_list)
    #     if post.get('type') == 'Select':
    #         if int(post.get('select_exam_id')) not in select_exam_list:
    #             select_exam_list.append(int(post.get('select_exam_id')))
    #         # event_id = request.env['event.event'].sudo().browse([int(post.get('select_exam_id'))])
    #         # if event_id:
    #         #     available_seats = event_id.seats_available - 1
    #         #     event_id.write({
    #         #                     'seats_available':available_seats,
    #         #                     })
    #         print("\n\n\n=====select_list====",select_exam_list)
    #     if post.get('type') == 'Remove':
    #         if int(post.get('remove_exam_id')) in select_exam_list:
    #             select_exam_list.remove(int(post.get('remove_exam_id')))
    #         # event_id = request.env['event.event'].sudo().browse([int(post.get('remove_exam_id'))])
    #         # if event_id:
    #         #     available_seats = event_id.seats_available + 1
    #         #     event_id.write({
    #         #                     'seats_available':available_seats,
    #         #                     })
    #         print("\n\n\n=====select_list====", select_exam_list)
    #     return select_exam_list

    @http.route('/pc_exam_date_search', type='json', auth='public', website=True)
    def pc_exam_date_search_data(self, **post):
        exam_date_list = []

        print("\n\n\n\n\n\===========exam data post======", post)
        if not post.get('sale_order'):
            exam_ids = request.env['event.event'].sudo().search(
                [('type_pc_exam.id', '=', post.get('exam_type')), ('subject', '=', (post.get('subject'))),
                 ('qualification.id', '=', int(post.get("level"))), ('address_ids', 'in', int(post.get('campus')))])
        if post.get('sale_order') and post.get('event_id'):
            event_id = request.env['event.event'].sudo().browse(int(post.get('event_id')))
            exam_ids = request.env['event.event'].sudo().search([('name','=',event_id.name),('type_pc_exam.id', '=', post.get('exam_type')),('address_ids', 'in', int(post.get('campus'))),('subject','=',post.get('subject')),('qualification.id', '=', int(post.get("level")))])

        print("\n\n\n==========exam_id====", exam_ids)
        today_datetime = datetime.now() + timedelta(7)
        tody_date_format = today_datetime.strftime('X%d-X%m-%Y').replace('X0','X').replace('X','')

        print("\n\n\n\n\n\n===========today date======",tody_date_format)
        if exam_ids:
            for exam in exam_ids:
                if exam.seats_available > 0:
                    exam_date = exam.date_end\
                        .split(" ")
                    datetimeobject = datetime.strptime(exam_date[0], '%Y-%m-%d')
                    newformat = datetimeobject.strftime('X%d-X%m-%Y').replace('X0','X').replace('X','')

                    date1 = datetime.strptime(tody_date_format, "%d-%m-%Y")
                    date2 = datetime.strptime(newformat, "%d-%m-%Y")
                    if date1 <= date2:
                        exam_date_list.append(newformat)
            print("\n\n\n\n===========list========",exam_date_list)
            return exam_date_list

    @http.route('/check_voucher', type='json', auth='public', website=True)
    def check_voucher(self, **post):
        voucher_price = 0.0
        print("\n\n\n\n\n===========post voucher=======",post)
        event_id = request.env['event.event'].sudo().browse([int(post.get('event_id'))])
        print("\n\n\n\n\n===========event_id voucher=======", event_id,event_id.qualification.name)
        voucher_num = post.get('voucher_value')

        voucher_id = request.env['pcexams.voucher'].sudo().search([('voucher_no','=',voucher_num)])
        print("\n\n\n\n\n===========voucher_id voucher=======", voucher_id,voucher_id.qualification_id.name)

        if voucher_id and event_id.qualification.name == voucher_id.qualification_id.name and voucher_id.status == 'Issued':
            voucher_price = voucher_id.voucher_value
            voucher_id.write({'status':'Redeemed'})
            return {'voucher_price':voucher_price,
                    'voucher_id':voucher_id.id}
        elif voucher_id and event_id.qualification.name == voucher_id.qualification_id.name and voucher_id.status != 'Issued':
            return {'error': 'status',
                    'status':voucher_id.status}
        elif voucher_id and event_id.qualification.name != voucher_id.qualification_id.name and voucher_id.status == 'Issued':
            return {'error': 'qualification'}
        elif not voucher_id:
            return {'error': 'error'}

    @http.route(['/examsearch'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def exam_search_reg(self, **post):
        exam_list = []
        level_lst=[]
        subject_lst=[]
        date_lst = []
        price = 0.0
        value={}
        print("\n\n\n\n\n\===========exam search post======", post,type(post.get('event[]')))
        exam_select_list = post.get('event[]').split(',')

        for i in range(0 , len(exam_select_list)):
            event_id = request.env['event.event'].sudo().browse([int(exam_select_list[i])])
            if event_id:
                level_lst.append(event_id.qualification.id)
                subject_lst.append(event_id.subject.id)
                price = price + event_id.price
                date = event_id.date_end.split(" ")
                date_lst.append(date[0])
                # available_seats = event_id.seats_available - 1
                # event_id.write({
                #     'seats_available': available_seats,
                # })
                exam_list.append(int(exam_select_list[i]))
        print("\n\n\n\n\=========exam list=======",exam_list)
        print("\n\n\n\n\=========level_lst list=======", level_lst)
        print("\n\n\n\n\=========subject_lst list=======", subject_lst)
        value['event_ids']=exam_list
        value['page_name']=post.get('page_name')
        value['select_pc_exam_level']=post.get('select_pc_exam_level') if post.get('select_pc_exam_level') else level_lst
        value['select_pc_exam_subject']=post.get('select_pc_exam_subject') if post.get('select_pc_exam_subject') else subject_lst
        value['inputDate']=post.get('inputDate') if post.get('inputDate') else date_lst
        value['campus']=post.get('campus')
        value['select_exam_type']=post.get('select_exam_type')
        value['total_price']= post.get('total_price') if post.get('total_price') else price

        return request.render('cfo_snr_jnr.exam_process_form', value)

    @http.route(['/pricing'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def pricing(self, **post):
        event_id_list=[]
        print("\n\n\n\n\n\===========exam price post======", post)
        res_id = post.get('event[]').strip('][').split(', ')
        for i in res_id:
            event_id_list.append(int(i))
        print("\n\n\nn\===res====",event_id_list)
        value={}
        value['exam_id_list']=event_id_list
        value['page_name'] = post.get('page_name')
        value['total_price']=post.get('total_price')
        value['campus']=post.get('campus')
        return request.render('cfo_snr_jnr.exam_pricing_form', value)

    @http.route(['/exam_registration'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def registration(self, **post):
        event_id_list = []
        voucher_lst=[]
        print("\n\n\n\n\n\===========exam registration post======", post)
        res_id = post.get('exam_id_list').strip('][').split(', ')
        for i in res_id:
            event_id_list.append(int(i))
        if post.get('voucher_id'):
            voucher_list = post.get('voucher_id').split(',')
            for voucher in voucher_list:
                voucher_lst.append(int(voucher))
        return request.render('cfo_snr_jnr.exam_registration_form', {'page_name': post.get('page_name'),
                                                                     'event_id_list':event_id_list,
                                                                     'voucher_list':voucher_lst,
                                                                     'total_price':post.get('price_total'),
                                                                     'campus':post.get('campus'),
                                                                     'pay_via_credit_card':post.get('button_credit') if post.get('button_credit') else '',
                                                                     'pay_via_eft':post.get('button_eft') if post.get('button_eft') else '',
                                                                     'confirm_booking':post.get('button_confirm') if post.get('button_confirm') else ''})

    @http.route(['/registerexam'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def registerexam(self, **post):
        order_line = []
        online_registration=[]

        print("\n\n\n\n\n\===========exam post registerexam======", post)
        if post.get('uuid'):
            print("\n\n\n\n\n\====registerexam=======exam post======", post)
        sale_order_id = False
        warehouse_id = False
        sale_order_dict = {}
        attachment_list=[]
        voucher_lst = []

        # print("\n\n\n\n===========event =========ids=======", event_select_list)
        campus_id = request.env['res.partner'].sudo().search([('id', '=', int(post.get('campus')))])
        print("\n\n\n\n===========event =========campus_id=======", campus_id)
        warehouse_id = request.env['stock.warehouse'].sudo().search([('name', '=', campus_id.name)])
        print("\n\n\n\n===========event =========warehouse_id=======", warehouse_id)
        if post.get('sale_order_id'):

            exam_list=[]
            sale_order_id = request.env['sale.order'].sudo().browse(int(post.get('sale_order_id')))
            # sale_order_id.order_line.unlink()
            exam_select = post.get('event[]').split(',')
            for i in range(0, len(exam_select)):
                event_id = request.env['event.event'].sudo().browse([int(exam_select[i])])
                if event_id:
                    exam_list.append(int(exam_select[i]))
            product_id = request.env['product.product'].sudo().search([('name', '=', 'PC Exams')])
            for event in exam_list:
                event_reschedule_id = request.env['event.event'].sudo().browse(int(event))
                for order_line in sale_order_id.order_line:
                    if int(post.get('event_id')) == order_line.event_id.id:
                        sale_order_id.write({'order_line':[(1,order_line.id,{'product_id': product_id.id,
                                                                                      'event_id': event_reschedule_id.id if event_reschedule_id else '',
                                                                                      'event_type_id': event_reschedule_id.event_type_id.id if event_reschedule_id else '',
                                                                                      # 'event_ticket_id': event_ticket.id if event_ticket.event_id else '',
                                                                                      'name': event_reschedule_id.name,
                                                                                      'product_uom_qty': 1.0,
                                                                                      'product_uom': 1.0,
                                                                                      'price_unit': event_reschedule_id.price,
                                                                                      'discount': 0})]})
                        available_seats = event_reschedule_id.seats_available - 1
                        event_reschedule_id.write({
                            'seats_available': available_seats,
                        })

                # sale_order_dict['prof_body'] = event_record_id.event_type_id.id if event_record_id.event_type_id else event_record_id.type_pc_exam.type_event_id.id
                # sale_order_dict['semester_id'] = event_record_id.semester_id.id
                # sale_order_dict['pc_exam_type'] = event_record_id.type_pc_exam.id

            # sale_order_id.write({'campus':campus_id.id if campus_id else ''})
            # sale_order_id.write(sale_order_dict)
            print("\n\n\n\n\n================post event_id====",post.get('event_id'),sale_order_id)
            return request.render('cfo_snr_jnr.exam_registration', {'page_name': post.get('page_name'),
                                                                    'total_price': 0.0,
                                                                    'campus': campus_id.name,
                                                                    'event_ids':exam_select,
                                                                    'pc_exam_type': sale_order_id.pc_exam_type.name,
                                                                    'exam_type':'PC Exams',
                                                                    'event_reschedule_id': post.get('event_id') if post.get('event_id') else False,
                                                                    'saleorder_id': sale_order_id.id,
                                                                 })
        if post and not post.get('sale_order_id'):
            event_select_list = post.get('event_id_list').strip('][').split(', ')
            account_rec_id = False
            account_pay_id = False
            name = False
            res_partner_obj = request.env['res.partner'].sudo()
            sale_obj = request.env['sale.order'].sudo()
            invoice_obj = request.env['account.invoice'].sudo()
            invoice_line = []
            if post.get('FirstName'):
                name = post.get('FirstName')
            else:
                name += ''
            if post.get('LastName'):
                name += ' ' + post.get('LastName')
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
            partner_id = request.env['res.partner'].sudo().search([('email', '=', post.get('Email'))], limit=1,
                                                                  order="id desc")
            product_id = request.env['product.product'].sudo().search([('name','=','PC Exams')])
            product_voucher_id = request.env['product.product'].sudo().search([('name', '=', 'PC Exam Voucher')])

            if post.get('voucher_list'):
                voucher_list = post.get('voucher_list').strip('][').split(', ')

                for voucher in voucher_list:
                    voucher_lst.append(voucher)
                    voucher_id = request.env['pcexams.voucher'].sudo().browse(int(voucher))
                    order_line.append([0, 0, {'product_id': product_voucher_id.id,
                                              # 'event_id': event_id.id if event_id else '',
                                              # 'event_type_id': event_id.event_type_id.id if event_id else '',
                                              # 'event_ticket_id': event_ticket.id if event_ticket.event_id else '',
                                              'name': 'PC Exam Voucher'+'('+voucher_id.voucher_no+')',
                                              'product_uom_qty': 1.0,
                                              'product_uom': 1.0,
                                              'price_unit': -voucher_id.voucher_value,
                                              'discount': 0
                                             }])

            for event in event_select_list:
                print("\n\n\n\n===========event =========ids=-----++======", event)
                event_id = request.env['event.event'].sudo().browse(int(event))
                order_line.append([0, 0, {'product_id': product_id.id,
                                          'event_id': event_id.id if event_id else '',
                                          'event_type_id': event_id.event_type_id.id if event_id else '',
                                          # 'event_ticket_id': event_ticket.id if event_ticket.event_id else '',
                                          'name': event_id.name,
                                          'product_uom_qty': 1.0,
                                          'product_uom': 1.0,
                                          'price_unit': event_id.price,
                                          'discount': 0
                                          }])
                available_seats = event_id.seats_available - 1
                event_id.write({
                    'seats_available': available_seats,
                })
                print("\n\n\n\n=====order line=====",order_line)
                # sale_order_dict['Validity_date'] = event_id.date_end
                sale_order_dict['prof_body'] = event_id.event_type_id.id if event_id.event_type_id else event_id.type_pc_exam.type_event_id.id
                sale_order_dict['semester_id'] = event_id.semester_id.id
                # sale_order_dict['date_order'] = event_id.date_begin
                sale_order_dict['pc_exam_type']=event_id.type_pc_exam.id

                print("\n\n\n\n\=================dict=============",sale_order_dict)
            if not partner_id:
                partner_id = res_partner_obj.sudo().create({'name': name,
                                                     'student_company': post.get('Company') if post.get(
                                                         'Company') else '',
                                                     'email': post.get('Email') if post.get('Email') else '',
                                                     'vat_no_comp': post.get('Vatno') if post.get(
                                                         'Vatno') else '',
                                                     'title': post.get('inputTitle') if post.get('inputTitle') else '',
                                                     'idpassport': post.get('ID_PassportNo.') if post.get(
                                                         'ID_PassportNo.') else '',
                                                     'cq_password': post.get('inputexamPassword') if post.get(
                                                         'inputexamPassword') else '',
                                                     'mobile': post.get('ContactNumber') if post.get(
                                                         'ContactNumber') else '',
                                                     'street': post.get('Street') if post.get(
                                                         'Street') else '',
                                                     'street2': post.get('Street2') if post.get(
                                                         'Street2') else '',
                                                     'city': post.get('City') if post.get('City') else '',
                                                     'country_id': int(post.get('exam_country_id')) if post.get(
                                                         'exam_country_id') else '',
                                                     'state_id': int(post.get('inputexamState')) if post.get(
                                                         'inputexamState') else '',
                                                     'zip': post.get('inputexamZip') if post.get(
                                                         'inputexamZip') else '',
                                                     'dob': post.get('DOB') if post.get('DOB') else '',
                                                     'prof_password': post.get('inputexampassword') if post.get(
                                                         'inputexampassword') else '',
                                                     'prof_body_id': post.get('inputexamId') if post.get(
                                                         'inputexamId') else '',
                                                     'examwritten':post.get('inputbeforepcexam'),
                                                     'property_account_receivable_id': account_rec_id.id,
                                                     'property_account_payable_id': account_pay_id.id})
            else:
                partner_id.sudo().write({'name': name,
                                                     'student_company': post.get('Company') if post.get(
                                                         'Company') else '',
                                                     'email': post.get('Email') if post.get('Email') else '',
                                                     'vat_no_comp': post.get('Vatno') if post.get(
                                                         'Vatno') else '',
                                                     'title': post.get('inputTitle') if post.get('inputTitle') else '',
                                                     'idpassport': post.get('ID_PassportNo.') if post.get(
                                                         'ID_PassportNo.') else '',
                                                     'cq_password': post.get('inputexamPassword') if post.get(
                                                         'inputexamPassword') else '',
                                                     'mobile': post.get('ContactNumber') if post.get(
                                                         'ContactNumber') else '',
                                                     'street': post.get('Street') if post.get(
                                                         'Street') else '',
                                                     'street2': post.get('Street2') if post.get(
                                                         'Street2') else '',
                                                     'city': post.get('City') if post.get('City') else '',
                                                     'country_id': int(post.get('exam_country_id')) if post.get(
                                                         'exam_country_id') else '',
                                                     'state_id': int(post.get('inputexamState')) if post.get(
                                                         'inputexamState') else '',
                                                     'zip': post.get('inputexamZip') if post.get(
                                                         'inputexamZip') else '',
                                                     'dob': post.get('DOB') if post.get('DOB') else '',
                                                     'prof_password': post.get('inputexampassword') if post.get(
                                                         'inputexampassword') else '',
                                                     'prof_body_id': post.get('inputexamId') if post.get(
                                                         'inputexamId') else '',
                                                     'examwritten':post.get('inputbeforepcexam'),
                                                     'property_account_receivable_id': account_rec_id.id,
                                                     'property_account_payable_id': account_pay_id.id})


            if partner_id:
                sale_order_id=sale_obj.sudo().create({'partner_id': partner_id.id,
                                     'campus': campus_id.id if campus_id else '',
                                     'student_number': partner_id.student_number,
                                     'warehouse_id': warehouse_id.id,
                                     'amount_untaxed': post.get('total_price'),
                                     'pc_exam':True,
                                     'date_order':datetime.now(),
                                     'quote_type': 'PC Exam',
                                     # 'discount_type_ids': [(6, 0, [each for each in discount_id])],
                                     'order_line': order_line})
                sale_order_id.sudo().write(sale_order_dict)
                sale_order_id.sudo().write({'name': sale_order_id.name + 'PC'})
                partner_id.sudo().write({'event_type_id':sale_order_id.prof_body.id})
                request.session['event_ids']=event_select_list
                # for event in event_select_list:
                #     event_id = request.env['event.event'].sudo().browse(int(event))
                #     online_registration.append([0, 0, {'event_id': event_id.name,
                #                                        'partner_id':partner_id.id,
                #                                        'email':partner_id.email
                #                                        }])
                #     event_id.write({'online_registration_ids':online_registration})
        if post.get('confirm_booking'):
            request.session['voucher_id']=voucher_lst
            request.session['sale_order'] = sale_order_id.id if sale_order_id else ''
            return request.redirect('/confirm/thankyou')

        if post.get('pay_via_credit_card'):
            return request.render('cfo_snr_jnr.exam_registration', {'page_name': post.get('page_name'),
                                                                    'total_price': sale_order_id.amount_untaxed,
                                                                    'campus': campus_id.name,
                                                                    'pc_exam_type':sale_order_id.pc_exam_type.name,
                                                                    'exam_type':product_id.name,
                                                                    'event_ids':event_select_list,
                                                                    'sale_order': sale_order_id.id,
                                                                    'sale_order_id': sale_order_id if sale_order_id else False,
                                                                    'pay_via_credit_card': post.get('pay_via_credit_card'),
                                                                    'pay_via_eft':post.get('pay_via_eft'),
                                                                    'do_invoice':'yes' if post.get('do_invoice') == 'Yes' else 'no',})
        if post.get('pay_via_eft'):
            if post.get('do_invoice') == 'No':
                sale_order_id.sudo().write({'state': 'draft'})

                # for event in event_select_list:
                #     event_id = request.env['event.event'].sudo().browse(int(event))
                #     online_registration.append([0, 0, {'event_id': event_id.name,
                #                                        'partner_id':partner_id.id,
                #                                        'email':partner_id.email
                #                                        }])
                #     event_id.write({'online_registration_ids':online_registration})

                mail_obj = request.env['mail.mail'].sudo()
                template_invoice_id = request.env.ref('cfo_snr_jnr.email_template_pcexam_payvia_eft_no_invoice',
                                                      raise_if_not_found=False)
                if template_invoice_id:
                    sale_order_id = sale_order_id.sudo()
                    pdf_data_enroll = request.env.ref('event_price_kt.report_pc_exam').sudo().render_qweb_pdf(
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
                        attachment_list.append(pdf_create)

                    agreement_id = request.env.ref('cfo_snr_jnr.pc_exam_data_pdf')
                    if agreement_id:
                        attachment_list.append(agreement_id)

                    agreement_id = request.env.ref('cfo_snr_jnr.pc_exam_data_pdf')
                    if agreement_id:
                        attachment_list.append(agreement_id)
                    template_invoice_id.sudo().write(
                        {'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])]})
                    template_invoice_id.sudo().with_context(
                        # email_to=each_request.get('email'),
                        # event_list=event_list,
                        email_cc='thecfo@charterquest.co.za',
                        # prof_body=invoice_id.prof_body.name,
                    ).sudo().send_mail(sale_order_id.id, force_send=True)
                    # body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
                    # body_html += "<br>"
                    # body_html += "Dear " + sale_order_id.partner_id.name + ","
                    # body_html += "<br><br>"
                    # body_html += "Thank you for provisionally booking your exam with CharterQuest."
                    # body_html += "<br><br>"
                    # body_html += "Payment must be submitted today to ensure your exam is fully booked 7 days in advance. Please note that space is limited so it is advisable to make payment as soon as possible."
                    # body_html += "<br><br>"
                    # body_html += "If you have paid your exams with your enrolment kindly forward your booking to accounts@charterquest.co.za to receive a confirmation of booking."
                    # body_html += "<br><br>"
                    # body_html += "Please see attached Terms and Condition for the pc exams."
                    # body_html += "<br><br>"
                    # body_html += "Email enquiries@charterquest.co.za for more information."
                    # body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Professional Education Institute<br>"
                    # body_html += "CENTRAL CONTACT INFORMATION:<br> Tel: +27 (0)11 234 9223 [SA & Intl]<br> Cell: +27 (0)73 174 5454 [SA & Intl]<br> <br/><div>"
                    #
                    # mail_values = {
                    #     'email_from': template_invoice_id.email_from,
                    #     'reply_to': template_invoice_id.reply_to,
                    #     'email_to': sale_order_id.partner_id.email if sale_order_id.partner_id.email else '',
                    #     'subject': "Charterquest PC Exam Booking " + sale_order_id.name + "PC",
                    #     'body_html': body_html,
                    #     'notification': True,
                    #     'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])],
                    #     'auto_delete': False,
                    # }
                    # msg_id = mail_obj.sudo().create(mail_values)
                    # msg_id.sudo().send()
                return request.render('cfo_snr_jnr.exam_page_eft_thankyou', {'page_name': post.get('page_name')})


            if post.get('do_invoice') == 'Yes':
                # for each_order_line in sale_order_id.order_line:
                #     print("\n\n\n\n\n\n\n==========each_order_line.name,==========",each_order_line.name)
                #     invoice_line.append([0, 0, {'product_id': each_order_line.product_id.id,
                #                                 'name': each_order_line.name,
                #                                 'quantity': 1.0,
                #                                 'account_id': each_order_line.product_id.categ_id.property_account_income_categ_id.id,
                #                                 'invoice_line_tax_ids': [
                #                                     (6, 0, [each_tax.id for each_tax in each_order_line.tax_id])],
                #                                 'price_unit': each_order_line.price_unit,
                #                                 'discount': each_order_line.discount}])
                # print("\n\n\n\n\n\n\n===============invoice line===========",invoice_line)
                # invoice_id = invoice_obj.sudo().create({'partner_id': sale_order_id.partner_id.id,
                #                                         'campus': sale_order_id.campus.id,
                #                                         'prof_body': sale_order_id.prof_body.id,
                #                                         'sale_order_id': sale_order_id.id,
                #                                         'semester_id': sale_order_id.semester_id.id,
                #                                         'invoice_line_ids': invoice_line,
                #                                         'residual': sale_order_id.out_standing_balance_incl_vat,
                #                                         })

                sale_order_id._action_confirm()
                # sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
                ctx = {'default_type': 'out_invoice', 'type': 'out_invoice', 'journal_type': 'sale',
                       'company_id': sale_order_id.company_id.id}
                inv_default_vals = request.env['account.invoice'].with_context(ctx).sudo().default_get(['journal_id'])
                ctx.update({'journal_id': inv_default_vals.get('journal_id')})
                print("\n\n\n\n\n============ctx================",sale_order_id.with_context(ctx))
                invoice_id = sale_order_id.with_context(ctx).sudo().action_invoice_create()
                invoice_id = request.env['account.invoice'].sudo().browse(invoice_id[0])
                # journal_id = request.env['account.journal'].sudo().browse(inv_default_vals.get('journal_id'))
                # payment_methods = journal_id.inbound_payment_method_ids or journal_id.outbound_payment_method_ids
                # payment_id = request.env['account.payment'].sudo().create({
                #     'partner_id': sale_order_id.partner_id.id,
                #     'amount': sale_order_id.due_amount if sale_order_id.due_amount else sale_order_id.amount_total,
                #     'payment_type': 'inbound',
                #     'partner_type': 'customer',
                #     'invoice_ids': [(6, 0, invoice_id.ids)],
                #     'payment_date': datetime.today(),
                #     'journal_id': journal_id.id,
                #     'payment_method_id': payment_methods[0].id
                # })
                invoice_id.action_invoice_open()

                # for event in event_select_list:
                #     event_id = request.env['event.event'].sudo().browse(int(event))
                #     online_registration.append([0, 0, {'event_id': event_id.name,
                #                                        'partner_id':partner_id.id,
                #                                        'email':partner_id.email
                #                                        }])
                #     event_id.write({'online_registration_ids':online_registration})



                mail_obj = request.env['mail.mail'].sudo()
                template_invoice_id = request.env.ref('cfo_snr_jnr.email_template_pcexam_payvia_eft',
                                                   raise_if_not_found=False)
                if template_invoice_id:
                    sale_order_id = sale_order_id.sudo()
                    pdf_data_order = request.env.ref(
                        'event_price_kt.report_invoice_pcexam').sudo().render_qweb_pdf(invoice_id.id)
                    if pdf_data_order:
                        pdfvals = {'name': 'Invoice Report',
                                   'db_datas': base64.b64encode(pdf_data_order[0]),
                                   'datas': base64.b64encode(pdf_data_order[0]),
                                   'datas_fname': 'Invoice Report.pdf',
                                   'res_model': 'account.invoice',
                                   'type': 'binary'}
                        pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                        attachment_list.append(pdf_create)

                    agreement_id = request.env.ref('cfo_snr_jnr.pc_exam_data_pdf')
                    if agreement_id:
                        attachment_list.append(agreement_id)
                    template_invoice_id.sudo().write(
                        {'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])]})
                    template_invoice_id.sudo().with_context(
                        # email_to=each_request.get('email'),
                        # event_list=event_list,
                        email_cc='thecfo@charterquest.co.za',
                        # prof_body=invoice_id.prof_body.name,
                    ).sudo().send_mail(invoice_id.id, force_send=True)
                return request.render('cfo_snr_jnr.exam_page_eft_thankyou', {'page_name': post.get('page_name')})

    @http.route(['/exam/redirect_payu'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def exam_redirect(self, **post):
        print("\n\n\n\n\n==============credit card post======",post)
        _logger.info("===================credit card post-------------------- <%s>", post)
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return_url = urljoin(base_url, '/exam/payment/payu_com/dpn/')
        cancel_url = urljoin(base_url, '/exam/payment/payu_com/cancel/')
        currency = request.env.ref('base.main_company').currency_id
        invoice_obj = request.env['account.invoice'].sudo()
        invoice_line = []

        if post.get('sale_order'):
            sale_order_id = request.env['sale.order'].sudo().browse(int(post.get('sale_order')))
        payment_acquire = request.env['payment.acquirer'].sudo().search([('provider', '=', 'payu')])
        amount =post.get('total_price') if post.get('total_price') else 0
        payu_tx_values = dict(post)

        account_id = request.env['account.account'].sudo().search([('code', '=', '200000')], limit=1)
        product_id = request.env['product.product'].sudo().search([('name', '=', 'Interest Amount')], limit=1)

        if amount:
            if len(amount.split('.')[1]) == 1:
                amount = amount + '0'
                amount = amount.replace('.', '')
            elif len(amount.split('.')[1]) == 2:
                amount = amount.replace('.', '')
        elif sale_order_id:
            amount = str(sale_order_id.amount_total) + '0'
            amount = amount.replace('.', '')

        # if post.get('do_invoice') == 'yes':

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
            first_name = ''
            last_name = ''
            if ' ' in sale_order_id.partner_id.name:
                first_name, last_name = sale_order_id.partner_id.name.split(' ', 1)
            else:
                first_name = sale_order_id.partner_id.name

            request.session['sale_order']=sale_order_id.id
            request.session['do_invoice']=post.get('do_invoice')

            transactionDetails = {}
            transactionDetails['store'] = {}
            transactionDetails['store']['soapUsername'] = payment_acquire.payu_api_username
            transactionDetails['store']['soapPassword'] = payment_acquire.payu_api_password
            transactionDetails['store']['safekey'] = payment_acquire.payu_seller_account
            transactionDetails['store']['environment'] = payment_acquire.environment
            transactionDetails['store']['TransactionType'] = 'PAYMENT'
            transactionDetails['basket'] = {}
            transactionDetails['basket']['description'] = 'PC Exam Booking'
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

            print("\n\n\n\nn\==============transactiondetails========",transactionDetails)
            request.session['sale_order_id'] = sale_order_id.id
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
            'amount': "{0:.2f}".format(sale_order_id.amount_total or 0),
            # 'amount':round(sale_order_id.amount_total) or 0,
            'currency_id': sale_order_id.pricelist_id.currency_id.id,
            'partner_id': sale_order_id.partner_id.id,
            'partner_country_id': sale_order_id.partner_id.country_id.id if sale_order_id.partner_id.country_id else 1,
            'reference': request.env['payment.transaction'].get_next_reference(sale_order_id.name),
            'sale_order_id': sale_order_id.id,
        }
        tx = request.env['payment.transaction'].sudo().create(tx_values)
        print("\n\n\n\nn\==================url  transactiondetails========", transactionDetails)
        url = PayuController.payuMeaSetTransactionApiCall('', transactionDetails)
        print("\n\n\n\n\n\n============url==========", url)
        _logger.info("===================payu url-------------------- <%s>",url)
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
            print("\n\n\n\n\n\n=======result====",result)
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
            print("\n\n\n\n=========response_state=====",response_state)
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
                print("\n\n\n\n==============status============",response_state)
                sale_order_data.message_post(subject="T&C's Privacy Policy",
                                             body="%s accepted T&C's and Privacy Policy." % sale_order_data.partner_id.name)
                return werkzeug.utils.redirect('/exam/pay/thank_you')
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
        attchment_list = []
        mail_obj = request.env['mail.mail'].sudo()
        sale_order_id = request.session.get('sale_order_id')
        print("\n\n\n\n=======sale_order_id=======", sale_order_id)
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            print("\n\n\n\n=======order=======",order)
        else:
            return request.redirect('/enrolment_book')

        template_id = request.env.ref('cfo_snr_jnr.unsuccessful_sponsored_regist_enrol_email_template',
                                      raise_if_not_found=False)
        if template_id:
            pdf_data_enroll = request.env.ref('event_price_kt.report_pc_exam').sudo().render_qweb_pdf(
                order.id)
            enroll_file_name = "Pro-Forma " + order.name
            if pdf_data_enroll:
                pdfvals = {'name': enroll_file_name,
                           'db_datas': base64.b64encode(pdf_data_enroll[0]),
                           'datas': base64.b64encode(pdf_data_enroll[0]),
                           'datas_fname': enroll_file_name + ".pdf",
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

            # mail_values = {
            #     'email_from': template_id.email_from,
            #     'reply_to': template_id.reply_to,
            #     'email_to': order.partner_id.email if order.partner_id.email else '',
            #     'email_cc': 'enquiries@charterquest.co.za,accounts@charterquest.co.za,cqops@charterquest.co.za',
            #     'subject': "PC Exams" + order.name,
            #     'notification': True,
            #     'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])],
            #     'auto_delete': False,
            # }
            # msg_id = mail_obj.create(mail_values)
            # msg_id.send()

            template_id.sudo().write(
                    {'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attchment_list])]})
            template_id.sudo().with_context(
                # email_to=each_request.get('email'),
                # event_list=event_list,
                email_cc='thecfo@charterquest.co.za',
                # prof_body=invoice_id.prof_body.name,
            ).send_mail(order.id, force_send=True)

        request.website.sale_reset()
        return request.render("cfo_snr_jnr.exam_unsuccessful")

    @http.route('/exam/payment/payu_com/cancel', type='http', auth="none", methods=['POST', 'GET'])
    def exam_payu_com_cancel(self, **post):
        """ When the user cancels its Payu payment: GET on this route """
        cr, uid, context = request.cr, SUPERUSER_ID, request.context
        return werkzeug.utils.redirect('/exam/unsuccessful')

    @http.route(['/exam/pay/thank_you'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def pay_thank_you(self, **post):
        print("\n\n\n\n\n==================exam thank you==============",post)
        _logger.info("===================exam thank you-------------------- <%s>", request.session.get('sale_order'))
        invoice_obj = request.env['account.invoice'].sudo()
        mail_obj = request.env['mail.mail'].sudo()
        attachment_list = []
        invoice_line = []
        online_registration = []

        if post.get('sale_order'):
            sale_order = post.get('sale_order')
        if request.session.get('sale_order'):
            sale_order = request.session['sale_order']
        if request.session.get('sale_last_order_id'):
            sale_order = request.session.get('sale_last_order_id')

        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))

        # sale_order_id.write({'state': 'sale'})
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

        # if request.session.get('do_invoice') == 'yes':
        sale_order_id._action_confirm()
        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
        ctx = {'default_type': 'out_invoice', 'type': 'out_invoice', 'journal_type': 'sale',
               'company_id': sale_order_id.company_id.id}
        inv_default_vals = request.env['account.invoice'].with_context(ctx).sudo().default_get(['journal_id'])
        ctx.update({'journal_id': inv_default_vals.get('journal_id')})
        _logger.info("invoice id============ <%s>", ctx)
        invoice_id = sale_order_id.with_context(ctx).sudo().action_invoice_create()
        _logger.info("invoice id============ <%s>", invoice_id)
        print("\n\n\n\n=========invoice line=========",invoice_id)
        invoice_id = request.env['account.invoice'].sudo().browse(invoice_id[0])
        journal_id = request.env['account.journal'].sudo().browse(inv_default_vals.get('journal_id'))
        payment_methods = journal_id.inbound_payment_method_ids or journal_id.outbound_payment_method_ids
        payment_id = request.env['account.payment'].sudo().create({
            'partner_id': sale_order_id.partner_id.id,
            'amount': sale_order_id.amount_total,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'invoice_ids': [(6, 0, invoice_id.ids)],
            'payment_date': datetime.today(),
            'journal_id': journal_id.id,
            'payment_method_id': payment_methods[0].id
        })

        invoice_id.action_invoice_open()
        print("\n\n\n\nn\====state=======",invoice_id.state)
        payment_id.action_validate_invoice_payment()
    # if request.session.get('do_invoice') == 'no':
    #     invoice_id.action_invoice_cancel()
    #     sale_order_id.write({'state': 'draft'})
    #
    # invoice_id.action_invoice_open()
    # payment_id.action_validate_invoice_payment()
    # template_id = request.env['mail.template'].sudo().search([('name', '=', "CharterQuest PC Exams Confirmation")])
    # quote_name = "SO{0}WEB".format(str(sale_order_id.id).zfill(3))
    # m = hashlib.md5(quote_name.encode())
    # decoded_quote_name = m.hexdigest()
    # config_para = request.env['ir.config_parameter'].sudo().search(
    #     [('key', 'ilike', 'web.base.url')])
    # if config_para:
    #     link = config_para.value + "/reschedulePB/" + decoded_quote_name
    #     sale_order_id.write({'debit_link': decoded_quote_name})
    #     print("\n\n\n\n=====link============",link)

    # template_id = request.env.ref('cfo_snr_jnr.email_template_payvia_credit_card',
    #                                   raise_if_not_found=False)
    # print("\n\n\n\n\n\n\==========event_ids==========",request.session.get('event_ids'))
    #
    # event_list=[]
    # # event_list = request.session.get('event_ids')
    # for event in request.session.get('event_ids'):
    #     exam_dict = {}
    #     event_id = request.env['event.event'].sudo().browse(int(event))
    #     online_registration.append([0, 0, {'event_id': event_id.name,
    #                                        'partner_id': invoice_id.partner_id.id,
    #                                        'email': invoice_id.partner_id.email
    #                                        }])
    #     event_id.write({'online_registration_ids': online_registration})
    #     exam = request.env['event.event'].sudo().browse(int(event))
    #     exam_dict['subject_name'] = exam.name
    #     exam_dict['start_time'] = exam.date_begin
    #     exam_dict['end_time'] = exam.date_end
    #     exam_dict['campus'] = sale_order_id.campus.name
    #     event_list.append(exam_dict)
    #
    # print("\n\n\n\n\n\n===================exam ============list======",event_list)
    #
    # if template_id:
    #     template_id.sudo().with_context(
    #         # email_to=each_request.get('email'),
    #         event_list=event_list,
    #         email_cc='thecfo@charterquest.co.za',
    #         reschedule_link = link,
    #         prof_body = invoice_id.prof_body.name,
    #     ).send_mail(sale_order_id.id,force_send=True)

        # if request.session.get('sale_order') and request.session.get('do_invoice') == 'yes':

    # template_invoice_id = request.env.ref('cfo_snr_jnr.email_template_pcexam_confirm',
    #                                           raise_if_not_found=False)
    # if template_invoice_id:
    #     if request.session.get('sale_order'):
    #         pdf_data_order = request.env.ref(
    #             'event_price_kt.report_invoice_pcexam').sudo().render_qweb_pdf(invoice_id.id)
    #         if pdf_data_order:
    #             pdfvals = {'name': 'Invoice Report',
    #                        'db_datas': base64.b64encode(pdf_data_order[0]),
    #                        'datas': base64.b64encode(pdf_data_order[0]),
    #                        'datas_fname': 'Invoice Report.pdf',
    #                        'res_model': 'account.invoice',
    #                        'type': 'binary'}
    #             pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
    #             attachment_list.append(pdf_create)

        # if request.session.get('sale_order') and request.session.get('do_invoice') == 'no':
        #     # com_spo_free_quote = request.env.ref('cfo_snr_jnr.company_sponsored_free_quote_email_template')
        #     pdf_data_enroll = request.env.ref(
        #         'event_price_kt.report_sale_enrollment').sudo().render_qweb_pdf(
        #         sale_order_id.id)
        #     enroll_file_name = "Pro-Forma " + sale_order_id.name
        #     if pdf_data_enroll:
        #         pdfvals = {'name': enroll_file_name,
        #                    'db_datas': base64.b64encode(pdf_data_enroll[0]),
        #                    'datas': base64.b64encode(pdf_data_enroll[0]),
        #                    'datas_fname': enroll_file_name + '.pdf',
        #                    'res_model': 'sale.order',
        #               invoice_id     'type': 'binary'}
        #         pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
        #         attachment_list.append(pdf_create)

        # agreement_id = request.env.ref('cfo_snr_jnr.pc_exam_data_pdf')
        # if agreement_id:
        #     attachment_list.append(agreement_id)
        # body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
        # body_html += "<br>"
        # body_html += "Dear " + sale_order_id.partner_id.name + ","
        # body_html += "<br><br>"
        # body_html += "Thank you for contacting CharterQuest and sending through your PC Exam Application."
        # body_html += "<br><br>"
        # body_html += "Please find attached your Tax invoice as well as the PC Exams Terms & Conditions."
        # body_html += "<br><br>"
        # body_html += "We look forward to seeing you on the day of your PC Exam. Please lookout for another email confirming your PC Exam Booking. CIMA Exams will be confirmed with PearsonVUE within 5-7 working days at most times sooner."
        # body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Professional Education Institute<br>"
        # body_html += "CENTRAL CONTACT INFORMATION:<br> Tel: +27 (0)11 234 9223 [SA & Intl]<br> Cell: +27 (0)73 174 5454 [SA & Intl]<br> Tel: 0861 131 137 [SA ONLY] <br> Fax: 086 218 8713 [SA ONLY] <br> Email:enquiries@charterquest.co.za <br/><div>"
        #
        # mail_values = {
        #     'email_from': template_id.email_from,
        #     'reply_to': template_id.reply_to,
        #     'email_to': sale_order_id.partner_id.email if sale_order_id.partner_id.email else '',
        #     'subject': "Charterquest PC Exam Booking " + sale_order_id.name + "PC",
        #     'body_html': body_html,
        #     'notification': True,
        #     'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])],
        #     'auto_delete': False,
        # }
        # msg_id = mail_obj.create(mail_values)
        # msg_id.send()
        # template_invoice_id.write(
        #     {'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])]})
        # template_invoice_id.sudo().with_context(
        #     # email_to=each_request.get('email'),
        #     # event_list=event_list,
        #     email_cc='thecfo@charterquest.co.za',
        #     # prof_body=invoice_id.prof_body.name,
        # ).send_mail(invoice_id.id, force_send=True)
        print("\n\n\n\n\n=======ca;lllllllllllll================")
        return request.render('cfo_snr_jnr.exam_process_page_thankyou', {'page_name': post.get('page_name')})

    @http.route(['/confirm/thankyou'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def confirm_thank_you(self, **post):
        invoice_obj = request.env['account.invoice'].sudo()
        mail_obj = request.env['mail.mail'].sudo()
        attachment_list = []
        invoice_line = []
        online_registration = []
        event_list = []
        if post.get('sale_order'):
            sale_order = post.get('sale_order')
        if request.session.get('sale_order'):
            sale_order = request.session['sale_order']
        print("\n\n\n\n\n\n===========voucher_ids_list====",request.session.get('voucher_id'))
        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))

        # sale_order_id.write({'amount_untaxed': 0.00})
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
        ctx = {'default_type': 'out_invoice', 'type': 'out_invoice', 'journal_type': 'sale',
               'company_id': sale_order_id.company_id.id}
        inv_default_vals = request.env['account.invoice'].with_context(ctx).sudo().default_get(['journal_id'])
        ctx.update({'journal_id': inv_default_vals.get('journal_id')})
        invoice_id = sale_order_id.with_context(ctx).sudo().action_invoice_create()
        invoice_id = request.env['account.invoice'].sudo().browse(invoice_id[0])
        journal_id = request.env['account.journal'].sudo().browse(inv_default_vals.get('journal_id'))
        payment_methods = journal_id.inbound_payment_method_ids or journal_id.outbound_payment_method_ids
        # payment_id = request.env['account.payment'].sudo().create({
        #     'partner_id': sale_order_id.partner_id.id,
        #     'amount': sale_order_id.amount_total,
        #     'payment_type': 'inbound',
        #     'partner_type': 'customer',
        #     'invoice_ids': [(6, 0, invoice_id.ids)],
        #     'payment_date': datetime.today(),
        #     'journal_id': journal_id.id,
        #     'payment_method_id': payment_methods[0].id
        # })

        invoice_id.action_invoice_open()
        print("\n\n\n\nn\====state=======", invoice_id.state)
        # payment_id.action_validate_invoice_payment()
        # payment_id.post()
        template_id = request.env.ref('cfo_snr_jnr.email_template_payvia_credit_card',
                                      raise_if_not_found=False)
        print("\n\n\n\n\n\n\==========event_ids==========", request.session.get('event_ids'))

        if sale_order_id:
            for exam in sale_order_id.order_line:
                exam_dict = {}
                event = request.env['event.event'].sudo().search([('id','=',exam.event_id.id),('name', '=', exam.event_id.name), ('type_pc_exam', '=', sale_order_id.pc_exam_type.id)])
                if event:
                    online_registration.append([0, 0, {'event_id': exam.event_id.name,
                                                       'partner_id': sale_order_id.partner_id.id,
                                                       'email': sale_order_id.partner_id.email
                                                       }])
                    quote_name = "SO{0}WEB".format(str(sale_order_id.id).zfill(3))

                    m = hashlib.md5(quote_name.encode())
                    decoded_quote_name = m.hexdigest()
                    config_para = request.env['ir.config_parameter'].sudo().search(
                        [('key', 'ilike', 'web.base.url')])
                    if config_para:
                        link = config_para.value + "/reschedulePB/" + decoded_quote_name
                        sale_order_id.write({'debit_link': decoded_quote_name})

                    exam.event_id.write({'online_registration_ids': online_registration})
                    exam_dict['subject_name'] = exam.event_id.name
                    exam_dict['start_time'] = exam.event_id.date_begin
                    exam_dict['end_time'] = exam.event_id.date_end
                    exam_dict['campus'] = sale_order_id.campus.name
                    link += '&%s' % (exam.event_id.id)
                    exam_dict['link'] = link
                    event_list.append(exam_dict)
                    print("\n\n\n\n\n\n========event_list======", event_list)

        if template_id:
            template_id.sudo().with_context(
                event_list=event_list,
                email_cc='thecfo@charterquest.co.za',
                prof_body=sale_order_id.prof_body.name,
            ).sudo().send_mail(sale_order_id.id, force_send=True)

        template_invoice_id = request.env.ref('cfo_snr_jnr.email_template_pcexam_confirm',
                                          raise_if_not_found=False)
        if template_invoice_id:
            # if request.session.get('sale_order'):
            pdf_data_order = request.env.ref(
                'event_price_kt.report_invoice_pcexam').sudo().render_qweb_pdf(invoice_id.id)
            if pdf_data_order:
                pdfvals = {'name': 'Invoice Report',
                           'db_datas': base64.b64encode(pdf_data_order[0]),
                           'datas': base64.b64encode(pdf_data_order[0]),
                           'datas_fname': 'Invoice Report.pdf',
                           'res_model': 'account.invoice',
                           'type': 'binary'}
                pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                attachment_list.append(pdf_create)

            agreement_id = request.env.ref('cfo_snr_jnr.pc_exam_data_pdf')
            if agreement_id:
                attachment_list.append(agreement_id)
            # body_html = "<div style='font-family: 'Lucica Grande', Ubuntu, Arial, Verdana, sans-serif; font-size: 12px; color: rgb(34, 34, 34); background-color: #FFF;'>"
            # body_html += "<br>"
            # body_html += "Dear " + sale_order_id.partner_id.name + ","
            # body_html += "<br><br>"
            # body_html += "Thank you for contacting CharterQuest and sending through your PC Exam Application."
            # body_html += "<br><br>"
            # body_html += "Please find attached your Tax invoice as well as the PC Exams Terms & Conditions."
            # body_html += "<br><br>"
            # body_html += "We look forward to seeing you on the day of your PC Exam. Please lookout for another email confirming your PC Exam Booking. CIMA Exams will be confirmed with PearsonVUE within 5-7 working days at most times sooner."
            # body_html += "<br><br><br> Thanking You <br><br> Patience Mukondwa<br> Head Of Operations<br> The CharterQuest Professional Education Institute<br>"
            # body_html += "CENTRAL CONTACT INFORMATION:<br> Tel: +27 (0)11 234 9223 [SA & Intl]<br> Cell: +27 (0)73 174 5454 [SA & Intl]<br> Tel: 0861 131 137 [SA ONLY] <br> Fax: 086 218 8713 [SA ONLY] <br> Email:enquiries@charterquest.co.za <br/><div>"

            # mail_values = {
            #     'email_from': template_id.email_from,
            #     'reply_to': template_id.reply_to,
            #     'email_to': sale_order_id.partner_id.email if sale_order_id.partner_id.email else '',
            #     'subject': "Charterquest PC Exam Booking " + sale_order_id.name + "PC",
            #     'body_html': body_html,
            #     'notification': True,
            #     'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])],
            #     'auto_delete': False,
            # }
            # msg_id = mail_obj.create(mail_values)
            # msg_id.send()
            template_invoice_id.sudo().write({'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])]})
            template_invoice_id.sudo().with_context(
                # email_to=each_request.get('email'),
                # event_list=event_list,
                email_cc='thecfo@charterquest.co.za',
                # prof_body=invoice_id.prof_body.name,
            ).sudo().send_mail(invoice_id.id, force_send=True)
        return request.render('cfo_snr_jnr.confirm_booking_thankyou', {'page_name': post.get('page_name')})

    @http.route(['/page/reschedule_thank_you'], type='http', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def reschedule_thank_you(self, **post):
        mail_obj = request.env['mail.mail'].sudo()
        attachment_list = []
        online_registration = []
        event_lst = []
        print("\n\n\n\n\n=========post reschedule====",post)
        if post.get('saleorder_id'):
            sale_order = post.get('saleorder_id')
        if post.get('event_reschedule_id'):
            event_id = request.env['event.event'].sudo().browse(int(post.get('event_reschedule_id')))
            print("\n\n\n\n\n=========post event_id====", event_id)
        sale_order_id = request.env['sale.order'].sudo().browse(int(sale_order))
        print("\n\n\n\n\n\n==============sale order name=====",sale_order_id.name)
        invoice_id = request.env['account.invoice'].sudo().search([('sale_order_id','=',sale_order_id.name),'|', ('state','=','paid'), ('state', '=', 'open')])
        template_id = request.env.ref('cfo_snr_jnr.email_template_reschedule_exam',raise_if_not_found=False)
        print("\n\n\n\n\n\n==============invoice id==========",invoice_id)
        event_list = []
        # event_list = request.session.get('event_ids')
        campus_name =''
        for order_line in sale_order_id.order_line:
            exam_dict = {}
            event_id = request.env['event.event'].sudo().search(
                [('id','=',order_line.event_id.id),('name', '=', order_line.event_id.name), ('type_pc_exam', '=', sale_order_id.pc_exam_type.id)])

            if event_id:
                campus_name = sale_order_id.campus.name
                if event_id.id == int(post.get('event_reschedule_id')):
                    campus_id = request.env['res.partner'].sudo().search([('name', '=', post.get('campus'))])
                    campus_name = campus_id.name
                online_registration.append([0, 0, {'event_id': event_id.name,
                                                   'partner_id': sale_order_id.partner_id.id,
                                                   'email': sale_order_id.partner_id.email
                                                   }])
                quote_name = "SO{0}WEB".format(str(sale_order_id.id).zfill(3))

                m = hashlib.md5(quote_name.encode())
                decoded_quote_name = m.hexdigest()
                config_para = request.env['ir.config_parameter'].sudo().search(
                    [('key', 'ilike', 'web.base.url')])
                if config_para:
                    link = config_para.value + "/reschedulePB/" + decoded_quote_name
                    sale_order_id.write({'debit_link': decoded_quote_name})

                exam_dict['subject_name'] = order_line.event_id.name
                exam_dict['start_time'] = order_line.event_id.date_begin
                exam_dict['end_time'] = order_line.event_id.date_end
                exam_dict['campus'] = campus_name
                link += '&%s' % (order_line.event_id.id)
                exam_dict['link'] = link
                event_list.append(exam_dict)

            print("\n\n\n\n\n=======event_list=====", event_list)

        agreement_id = request.env.ref('cfo_snr_jnr.pc_exam_data_pdf')
        if agreement_id:
            attachment_list.append(agreement_id)
        template_id.sudo().write(
            {'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])]})
        if template_id:
            template_id.sudo().with_context(
                event_list=event_list,
                email_cc='thecfo@charterquest.co.za',
                prof_body=sale_order_id.prof_body.name,
            ).sudo().send_mail(sale_order_id.id, force_send=True)

        template_invoice_id = request.env.ref('cfo_snr_jnr.email_template_pcexam_confirm',
                                                  raise_if_not_found=False)
        if template_invoice_id:
            pdf_data_order = request.env.ref('event_price_kt.report_invoice_pcexam').sudo().render_qweb_pdf(invoice_id.id)
            if pdf_data_order:
                pdfvals = {'name': 'Invoice Report',
                           'db_datas': base64.b64encode(pdf_data_order[0]),
                           'datas': base64.b64encode(pdf_data_order[0]),
                           'datas_fname': 'Invoice Report.pdf',
                           'res_model': 'account.invoice',
                           'type': 'binary'}
                pdf_create = request.env['ir.attachment'].sudo().create(pdfvals)
                attachment_list.append(pdf_create)
        template_invoice_id.sudo().write(
            {'attachment_ids': [(6, 0, [each_attachment.id for each_attachment in attachment_list])]})
        if template_invoice_id:
            template_invoice_id.sudo().with_context(
                # event_list=event_list,
                email_cc='thecfo@charterquest.co.za',
                # prof_body=invoice_id.prof_body.name,
            ).sudo().send_mail(invoice_id.id, force_send=True)

        return request.render('cfo_snr_jnr.reschedule_booking_thankyou', {'page_name': post.get('page_name')})