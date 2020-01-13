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


from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_lecturer = fields.Boolean(string="Lecturer ?")


class CFOCourseOption(models.Model):
    _name = 'cfo.course.option'

    name = fields.Char(string="Course Option")
    active = fields.Boolean(string="Active", default=True)


class CFOSemesterInformation(models.Model):
    _name = 'cfo.semester.information'

    name = fields.Char(string="Name")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    sequence=fields.Integer(string="Sequence")
    active = fields.Boolean(string="Active", default=True)

class CFOCourseCode(models.Model):
    _name = 'cfo.course.code'

    name = fields.Char(string="Course Code")
    description = fields.Text(string="Description")
    short_description = fields.Char(string="Short Description")
    lecturer_ids = fields.Many2many('res.partner', string="Lecturer(s)")
    campus_id = fields.Many2one('res.partner', string="Campus")
    active = fields.Boolean(string="Active", default=True)


class CFOTimeTable(models.Model):
    _name = "cfo.time.table"

    name = fields.Char(string="Name")
    course_option_id = fields.Many2one('cfo.course.option', string="Course Option", required=True)
    qualification_id = fields.Many2one("event.qual", string="Qualification", required=True)
    semester_id = fields.Many2one('cfo.semester.information', string="Semester", required=True)
    description = fields.Text(string="Description")
    time_table_line_ids = fields.One2many("cfo.time.table.line", 'time_table_id', string="Time Table Lines")
    active = fields.Boolean(string="Active", default=True)
    event_id=fields.Many2one("event.type",string="Event Categories")


class CFOTimeTableLines(models.Model):
    _name = "cfo.time.table.line"
    _rec_name = "course_code_id"

    course_code_id = fields.Many2one('cfo.course.code', string="Course Code")
    start_time = fields.Float(string="Start Time")
    end_time = fields.Float(string="End Time")
    day_selection = fields.Selection([
        ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'),
        ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')
    ], string="Day")
    time_table_week_ids = fields.One2many("cfo.time.table.weeks", 'time_table_line_id', string="Time Table Weeks")
    time_table_id = fields.Many2one('cfo.time.table', string="Time Table")


class CFOTimeTableWeeks(models.Model):
    _name = "cfo.time.table.weeks"

    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    color=fields.Char(string="color")
    time_table_line_id = fields.Many2one('cfo.time.table.line', string="Time Table Line")


class ResCompany(models.Model):
    _inherit="res.company"

    disclaimer_text=fields.Text(string="Disclaimer")
    session_text=fields.Text(string="")




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
