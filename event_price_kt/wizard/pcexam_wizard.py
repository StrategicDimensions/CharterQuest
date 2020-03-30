# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import date, datetime, timedelta


class pcexams_success(models.TransientModel):

    _name = "pcexams.success"

    name = fields.Text('Result')


class pcexams_wizard(models.Model):

    _name = "pcexams.wizard"

    name = fields.Char('Name')
    address_ids = fields.Many2many('res.partner', string='Location')
    type_pc_exam = fields.Many2one('pc.exam.type', 'Type of PC Exam')
    subject = fields.Many2one('event.subject', 'Subject')
    # type = fields.Many2one('event.type', 'Type Of Event')
    date_begin = fields.Datetime('Start Date')
    date_end = fields.Datetime('End Date')
    price = fields.Float('Course Fees')
    # semester = fields.Many2one('event.semester', string='Semester')
    qualification = fields.Many2one('event.qual', 'Qualification Level')
    seats_max = fields.Integer('Maximum Available Seats')
    # user_id = fields.Many2one('res.users', 'Responsible User')
    # email_registration_id = fields.Many2one('mail.template', string='Registration Confirmation Email',domain=[('model', '=', 'event.registration')])
    # email_confirmation_id = fields.Many2one('mail.template', string='Event Confirmation Email',domain=[('model', '=', 'event.registration')])


    @api.multi
    def create_events(self):
          test = ''
          for record in self.browse(self.id):
                print("\n\n\n\n\n======record=====",record)
                count =0
                start_date = record.date_begin
                test = int(start_date[:4])
               
                last_date = date(test, 12, 31)
                 
                #last_date1 = str(datetime.strptime(str(last_date),"%Y-%m-%d"))  
                
                last_date1 = str(last_date)+' 23:59:59'
                end_date = record.date_end
                dic = {}
                data = []
                while(str(start_date) < str(last_date1)):
                    dic = {
                        'name':record.name,
                        'address_ids':[(6, None, record.address_ids.ids)] or False,
                        'type_pc_exam':record.type_pc_exam.id or False,
                        'subject':record.subject.id or False,
                        # 'type':record.type.id or False,
                        'date_begin':start_date,
                        'date_end':end_date,
                        'price':record.price,
                        # 'semester':record.semester,
                        'qualification':record.qualification.id or False,
                        'seats_max':record.seats_max,
                        'pc_exam':True,
                        # 'user_id':record.user_id.id or False,
                        # 'email_registration_id':record.email_registration_id.id or False,
                        # 'email_confirmation_id':record.email_confirmation_id.id or False
                       }
                    data.append(dic)
                    count = count + 1
                    start_date = str(datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S') + timedelta(days=7) )
                    end_date = str(datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S') + timedelta(days=7) )
                if data:
                   test = 'events Successfully created'
                else:
                   test = 'events not created'    
                for data1 in data:
                    
                    self.env['event.event'].create(data1)
            
          success_id = self.env['pcexams.success'].create({'name': test})
          return {
            'res_id': success_id.id,
            'name': test,
            'view_mode': 'form',
            'res_model': 'pcexams.success',
            'type': 'ir.actions.act_window',
            'target': 'new',
            }