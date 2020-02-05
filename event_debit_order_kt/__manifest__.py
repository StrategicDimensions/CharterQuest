{
    "name": "Debit Order Customization",
    "version": "11.0.1",
    "sequence":3,
    "depends": ["base", "account", "account_voucher", "event_price_kt"],
    "author": "Acespritech Solutions Pvt. Ltd.",
    "category": "Custom",
    "description": "Adds a custom Pricing debit orders to OpenERP events",
    "data": [
            'security/security.xml',
            'security/ir.model.access.csv',
            'views/cssfile.xml',
            'views/account_debit_order_view.xml',
            'views/account_invoice_view.xml',
            'views/sales_view.xml',
            'views/email_templates_view.xml',
            'views/debit_order_two_days_template_view.xml',
            ],
    "update_xml":[],
    "installable": True,
}

