# -*- coding: utf-8 -*-

{
    'name': 'Website Events Changes',
    'version': '12.5',
    'sequence':6,
    'website': 'https://www.odoo.com/page/events',
    'category': 'Tools',
    'summary': 'Trainings, Conferences, Meetings, Exhibitions, Registrations',
    'description': """
    """,
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'depends': ['event', 'website_event', 'event_sale', 'stock', 'website_sale'],
    'auto_install': False,
    'data': ['views/website_event_view.xml',
             'views/templates.xml',
             'views/subscriptions_view.xml',
             'views/vue_exam_report.xml'],
}
