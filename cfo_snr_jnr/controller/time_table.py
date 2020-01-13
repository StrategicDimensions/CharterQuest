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
from odoo import http
from odoo.http import request



class TimeTable(http.Controller):

    @http.route(['/time_table',], type='http', auth="public", website=True,csrf=False)
    def time_table_view(self, **post):
        timetable_ids=[]
        level_select = post.get('level_select') if post.get('level_select') else ','.join(
            [str(i.id) for i in request.env['event.qual'].sudo().search([])])
        option_select = post.get('option_select') if post.get('option_select') else ','.join(
            [str(i.id) for i in request.env['cfo.course.option'].sudo().search([])])
        semester_select = post.get('semester_select') if post.get('semester_select') else ','.join(
            [str(i.id) for i in request.env['cfo.semester.information'].sudo().search([])])
        time_table_ids = request.env['cfo.time.table'].sudo().search([])
        time_table_ids = time_table_ids.filtered(
            lambda l: l.qualification_id.id in [int(i) for i in level_select.split(',')])
        time_table_ids = time_table_ids.filtered(
            lambda l: l.course_option_id.id in [int(i) for i in option_select.split(',')])
        time_table_ids = time_table_ids.filtered(
            lambda l: l.semester_id.id in [int(i) for i in semester_select.split(',')])
        time_table_ids=time_table_ids.sorted(key= lambda l: l.semester_id.sequence)
        course_code = post.get('course_code_select') if post.get('course_code_select') else ','.join(
            [str(i.id) for i in request.env['cfo.course.code'].sudo().search([])])
        campus_select = post.get('campus_select') if post.get('campus_select') else ','.join(
            [str(i.id) for i in request.env['res.partner'].sudo().search([('is_campus', '=', True)])])
        for data in time_table_ids:
            for line in data.time_table_line_ids:
                if line.course_code_id.id in [int(id) for id in course_code.split(',')]:
                    if data not in timetable_ids:
                        timetable_ids.append(data)

        return request.render("cfo_snr_jnr.time_table_template", {
            'time_table': time_table_ids, 'course_code_select': course_code,
            'campus_select': post.get('campus_select') if post.get('campus_select') else '',
            'option_select': post.get('option_select') if post.get('option_select') else '',
            'semester_select': post.get('semester_select') if post.get('semester_select') else '',
            'ids': str(time_table_ids.ids).strip('[]'),'is_visible':True if post.get('course_code_select') else False,
            'company':request.env['res.company'].sudo().search([('partner_id.name','=','The CharterQuest Institute')])
        })

    @http.route(['/time_table_snippet'], type='json', auth="public", website=True, csrf=False)
    def time_table_snippet_view(self, **post):
        list1 = [i.id for i in request.env['event.qual'].sudo().search([])]
        list2 = [i.id for i in request.env['cfo.course.option'].sudo().search([])]
        list3 = [i.id for i in request.env['cfo.semester.information'].sudo().search([])]
        list4 = [i.id for i in request.env['cfo.course.code'].sudo().search([])]
        list5 = [i.id for i in request.env['res.partner'].sudo().search([('is_campus', '=', True)])]
        timetable_ids=[]
        event_id=request.env['event.type'].browse(int(post.get('id')))
        level_select = post.get('level_select') if post.get('level_select') else list1
        option_select = post.get('option_select') if post.get('option_select') else list2
        semester_select = post.get('semester_select') if post.get('semester_select') else list3
        time_table_ids = request.env['cfo.time.table'].sudo().search([])
        time_table_ids = time_table_ids.filtered(
            lambda l: l.event_id.id in event_id.ids)
        time_table_ids = time_table_ids.filtered(
            lambda l: l.qualification_id.id in [int(i) for i in level_select])
        time_table_ids = time_table_ids.filtered(
            lambda l: l.course_option_id.id in [int(i) for i in option_select])
        time_table_ids = time_table_ids.filtered(
            lambda l: l.semester_id.id in [int(i) for i in semester_select])
        time_table_ids = time_table_ids.sorted(key=lambda l: l.semester_id.sequence)
        course_code = [int(i) for i in post.get('course_code_select')] if post.get('course_code_select') else list4
        course_code_select = str(course_code).strip('[]')
        campus_select = [int(id) for id in post.get('campus_select')] if post.get('campus_select') else list5
        for data in time_table_ids:
            for line in data.time_table_line_ids:
                if line.course_code_id.id in course_code and line.course_code_id.campus_id.id in campus_select:
                    if data not in timetable_ids:
                        timetable_ids.append(data)
        datas={
            'course_code_select': course_code,
            'course_code':course_code_select,
            'time_table':timetable_ids,
            'campus_select': campus_select,
            'option_select': post.get('option_select[]') if post.get('option_select[]') else '',
            'semester_select': post.get('semester_select[]') if post.get('semester_select[]') else '',
            'ids': str(time_table_ids.ids).strip('[]'), 'is_visible': True,
            'company': request.env['res.company'].sudo().search(
                [('partner_id.name', '=', 'The CharterQuest Institute')])
        }
        html = request.env['ir.ui.view'].render_template(
            'cfo_snr_jnr.timetable_snippet_template',
            values=datas,
        )
        return html



    @http.route(['/<string:lecturer_name>/<int:lecturer_id>'], type='http', auth="public", website=True)
    def view_lecturer_detail(self, lecturer_id, **post):
        if lecturer_id:
            lecturer_id = request.env['res.partner'].sudo().browse([lecturer_id])
            return request.render("cfo_snr_jnr.view_lecturer_details", {'lecturer': lecturer_id})

    @http.route('/time_table/report/print', methods=['POST', 'GET'], csrf=False, type='http', auth="public", website=True)
    def print_id(self, **kw):
        time_table_ids = [int(i) for i in kw['id'].split(",")]
        course_code = [int(i) for i in kw['code'].split(",")]
        timetable_ids=request.env['cfo.time.table'].sudo().search([('id','in',time_table_ids)])
        timetable_ids = timetable_ids.sorted(key=lambda l: l.semester_id.sequence)
        timetable_ids_list=[]
        for data in timetable_ids:
            for line in data.time_table_line_ids:
                if line.course_code_id.id in course_code:
                    if data not in timetable_ids_list:
                        timetable_ids_list.append(data)
        id=request.env['res.company'].sudo().search([('partner_id.name','=','The CharterQuest Institute')])
        datas={'course_code':course_code,'session_text':id.session_text}
        if timetable_ids and course_code:
            report_id = request.env.ref('cfo_snr_jnr.report_time_table')
            pdf = report_id.sudo().render_qweb_pdf(timetable_ids_list, data=datas)[0]
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf)),
                ('Content-Disposition', 'attachment;filename=Class TimeTable.pdf;'),
                ('target', '_blank'),
            ]
            return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/get_timetable_data'], type='json', auth="public", methods=['POST', 'GET'], website=True, csrf=False)
    def get_timetable_data(self, **kw):
        subject = []
        study_option = []
        if kw.get('qua_ids') and kw.get('campus_ids') and kw.get('semester_ids') and kw.get('option_ids'):

            res = request.env['cfo.time.table'].sudo().search([('qualification_id', 'in', [int(id) for id in kw.get('qua_ids')]),
                                                            ('semester_id', 'in', [int(id) for id in kw.get('semester_ids')]),('course_option_id','in',[int(id) for id in kw.get('option_ids')])])
            sub_list=[]
            for record in res:
                for line in record.time_table_line_ids:
                    if line.course_code_id.campus_id.id in [int(id) for id in kw.get('campus_ids')]:
                        if line.course_code_id.id not in sub_list:
                            subject.append({'id': line.course_code_id.id, 'name': line.course_code_id.name})
                            sub_list.append(line.course_code_id.id)
        else:
            subject = request.env['cfo.course.code'].sudo().search_read([], ['id', 'name'])


        return {
            'subject':subject,
            'study_option':study_option
        }

    @http.route(['/set_color'], type='json', auth="public", website=True)
    def set_color(self, **kw):
        res = request.env['cfo.time.table.weeks'].sudo().browse(kw.get('data_id'))
        res.write({'color': kw.get('hex_val')})

    @http.route(['/get_campus'], type='json', auth="public", website=True)
    def get_campus(self, **kw):
        data=[]
        if kw.get('id'):
            for id in request.env['event.type'].sudo().browse(int(kw.get('id'))).campus_ids:
                data.append({'id':id.id,'name':id.name})
            return {'campus': data}
        else:
            browse_ids = request.env['res.partner'].sudo().search_read([('is_campus', '=', True)], ['id', 'name'])
            return {'campus': browse_ids}
