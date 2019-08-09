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

    @http.route(['/time_table'], type='http', auth="public", website=True)
    def time_table_view(self, **post):
        print("\n\n\n\n\n post",post)
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
        course_code = post.get('course_code_select') if post.get('course_code_select') else ','.join(
            [str(i.id) for i in request.env['cfo.course.code'].sudo().search([])])
        campus_select = post.get('campus_select') if post.get('campus_select') else ','.join(
            [str(i.id) for i in request.env['res.partner'].sudo().search([('is_campus', '=', True)])])

        print("\n\n\n called")
        print("\n\n\n time_table_ids",time_table_ids)
        print("\n\n\n campus_select",campus_select)
        print("\n\n\n level_select",level_select)
        print("\n\n\n option_select",option_select)
        print("\n\n\n semester_select",semester_select)
        return request.render("cfo_snr_jnr.time_table_template", {
            'time_table': time_table_ids, 'course_code_select': course_code,
            'campus_select': post.get('campus_select') if post.get('campus_select') else '',
            'option_select': post.get('option_select') if post.get('option_select') else '',
            'semester_select': post.get('semester_select') if post.get('semester_select') else '',
        })

    @http.route(['/view_lecturer/<int:lecturer_id>'], type='http', auth="public", website=True)
    def view_lecturer_detail(self, lecturer_id, **post):
        if lecturer_id:
            lecturer_id = request.env['res.partner'].sudo().browse([lecturer_id])
            return request.render("cfo_snr_jnr.view_lecturer_details", {'lecturer': lecturer_id})
