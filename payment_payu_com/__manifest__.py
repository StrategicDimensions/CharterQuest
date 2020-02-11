# -*- coding: utf-8 -*-
{
    'name': 'PayU',
    'version': '11.0.1',
    'depends': ['payment'],
    'author': 'Strategic Dimensions',
    'category': 'payment',
    'summary': "PayU South Africa",
    'description': """
    PayU
    """,
    'website': 'http://www.odoo.com',
    'images': ['images/main-screenshot.png'],
    'data': [
                'views/payu_template.xml',
                'data/payu_data.xml',
                'views/payu.xml',
                'views/emailtemplate_view.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
