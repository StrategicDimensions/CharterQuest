{
    "name": "Event Price",
    "version": "20.1",
    "depends": ["base", "sale_management", "event_sale", "event"],
    "author": "Acespritech Solutions Pvt. Ltd.",
    "category": "Custom",
    "description": "Adds a custom Pricing to OpenERP events",
    "data": [
        'security/ir.model.access.csv',
        'views/event_view_inh.xml',
        'wizard/sale_make_invoice_advance.xml',
            ],
    "test": [],
    "installable": True,
    "active": False
}
