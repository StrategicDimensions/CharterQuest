# -*- coding: utf-8 -*-

from odoo import fields, models, api,  _
from datetime import date,datetime,timedelta
# from dateutil.relativedelta import relativedelta



class event_semester(models.Model):
    _name = "event.semester"

    name = fields.Char("Name",size=56)
    date_begin = fields.Date("Start Date")
    date_end = fields.Date("End Date")
    semester = fields.Selection([('1', '1st Semester'), ('2', '2nd Semester'), ('3','3rd Semester')],
                                'Semester', help="Semester in which the course takes place")

class terms_conditions(models.Model):
    _name = "terms.conditions"
    _description = "Terms and Conditions"

    name = fields.Char('Name', size=60)
    type = fields.Selection([('Enrolements', 'ENrolements'), ('PC Exams', 'PC Exams'),
                             ('CharterBooks','CharterBooks')], 'Type')
    terms_condition = fields.Html('Terms & Conditions')


class debitorder_interest(models.Model):
    _name = "debitorder.interest"
    _description = "DebitOrder Interests"

    no_months = fields.Integer('No of payment months desired?')
    interest_per = fields.Float('Interest %')


class pcexams_voucher(models.Model):
    _name = 'pcexams.voucher'
    _description = 'PCExams Vocuher'
    _order = 'id desc'

    voucher_no = fields.Char(string='Voucher No')
    create_date = fields.Datetime('Date')
    student_id = fields.Many2one('res.partner', 'Student')
    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    expiry_date = fields.Date('Expiry Date')
    voucher_value = fields.Float('Voucher Value')
    prof_body = fields.Many2one('event.type', 'Professional Body')
    qualification_id = fields.Many2one('event.qual', 'Qualification Level')
    campus_id = fields.Many2one('res.partner', 'Campus')
    status = fields.Selection([('Issued', 'Issued'), ('Redeemed', 'Redeemed'), ('Cancelled', 'Cancelled'),
                               ('Expired', 'Expired')], 'Status')
    redeemed_invoice = fields.Many2one('account.invoice', 'Redeemed Invoice')

    @api.model
    def pcexams_expiry_notification(self):
    # '''Send Voucher Expiry notifications to Student'''
        todaydate = date.today()

        voucher_ids = self.search([('status', '=', 'Issued')])

        for voucher in voucher_ids:
            expiry_date = datetime.strptime(str(voucher.expiry_date), "%Y-%m-%d").date()-timedelta(days=30)

            if str(expiry_date) == str(todaydate):
               template_id = self.env['mail.template'].search([('name', '=', "PC Exam Voucher Expiring in 30 days!")])
               if template_id:
                   template_id.send_mail(voucher)
            expiry_date1 = datetime.strptime(str(voucher.expiry_date), "%Y-%m-%d").date()-timedelta(days=7)

            if str(expiry_date1) == str(todaydate):
               template_id = self.env['mail.template'].search([('name', '=', "PC Exam Voucher Expiring in 7 days!")])
               if template_id:
                   template_id.send_mail(voucher)
            #expiry_date2 = datetime.strptime(str(voucher.expiry_date), "%Y-%m-%d").date()
            expiry_date2 = datetime.strptime(str(voucher.expiry_date), "%Y-%m-%d").date() + timedelta(days=1)
            if str(expiry_date2) == str(todaydate):
                ## Raaj 27th april updated the template name
                   #template_id = self.pool.get('email.template').search(cr,uid,[('name','=',"PC Exam Expiry Notification")])
                template_id = self.env['mail.template'].search([('name', '=', "PC Exam Voucher Expired!")])
                if template_id:
                    template_id.send_mail(voucher)
                    voucher.write({'status': 'Expired'})
        return True