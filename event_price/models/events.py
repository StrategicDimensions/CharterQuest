
from functools import reduce
from odoo import fields, models, _, api
import logging
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
log = logging.getLogger(__name__)
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import time


class event_registration(models.Model):
    """Event Registration"""
    _inherit= 'event.registration'

    event_campus = fields.Many2one(related='event_id.address_id', string="campus", readonly=True)
    event_body = fields.Many2one(related='event_id.event_type_id', string="Professional Body", readonly=True)
    semester_id = fields.Many2one(related='event_id.semester_id', string='Semester', readonly=True)

class event_event(models.Model):
    """Extends the event model with an extra price fields."""
    _inherit = 'event.event'

    @api.one
    @api.depends('online_registration_ids')
    def get_online_register(self):
        """Get Confirm or uncofirm register value.
        @param ids: List of Event registration type's id
        @param fields: List of function fields(register_current and register_prospect).
        @param context: A standard dictionary for contextual values
        @return: Dictionary of function fields value.
        """
        res = {}
        count = 0
        for event in self.browse(self.id):
            res[event.id] = {}
            for registration in event.online_registration_ids:
                count += 1
            res[event.id] = count
        self.online_register_current = count
        return res

    address_ids = fields.Many2many('res.partner', string='Locations')
    price = fields.Float('Course Fees', help="Fees of the Course.")
    semester_id = fields.Many2one('event.semester', string="Semester")
    qualification = fields.Many2one('event.qual', string='Qualification Level')
    ## study = fields.Many2one('event.options', string='Study Options')
    online_registration_ids = fields.One2many('event.online.registration', 'event_id', string='Online Registrations abc',
                                            required=True)
    online_register_current = fields.Float(compute='get_online_register', string='Online Registrations Current',
                                           required=True, default=0.0, store=True)


class event_qual(models.Model):

    _name = 'event.qual'

    name = fields.Char('Qualification Level', size=64, required=True)
    order = fields.Integer(string='Qualification Level Order')

    @api.constrains('order')
    def check_order(self):
        for record in self:
            obj = self.search([('order', '=', record.order), ('id', '!=', record.id)])
            if obj:
                raise ValidationError("Order must be unique")


class event_options(models.Model):
    """Study Options for Course"""
    
    _name = 'event.options'

    name =  fields.Char('Study Options', size=64, required=True)
    description = fields.Text('Description')
    order = fields.Integer('Sequence')


class event_feetype(models.Model):
    """Study Options for Course"""
    
    _name = 'event.feetype'

    name = fields.Char(string='Fee Type', size=64, required=True)


class event_online_registration(models.Model):
    """logs all online Registrations"""
    
    _name = 'event.online.registration'

    id = fields.Integer(string='ID')
    event_id = fields.Many2one('event.event', string='Event', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    namee = fields.Char(string='Name')
    email = fields.Char(string='email')


class sale_order(models.Model):
    """Extends the Sale Order with an field for type of enrollment"""

    _inherit = 'sale.order'

    quote_type = fields.Selection([('freequote', 'Free Quote'), ('enrolment', 'Enrolment'),
                                   ('PC Exam', 'PC Exam'), ('CharterBooks', 'CharterBooks')], string='Quote type')
    affiliation = fields.Selection([('1', 'Self Sponsored'), ('2', 'Company')], string= 'Sponsorship')
    campus = fields.Many2one('res.partner', string= 'Campus')
    prof_body = fields.Many2one('event.type', string= 'Professional Body')
    # semester = fields.Selection([('1', '1st Semester'), ('2', '2nd Semester'), ('3', '3rd Semester')],
    #                             string= 'Semester', help="Semester in which the course takes place")
    student_number = fields.Char(string='Student No', size=64)
    semester_id = fields.Many2one('event.semester', string='Semester')

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(sale_order, self).onchange_partner_id()
        if self.partner_id:
            self.update({'student_number': self.partner_id.student_number})
        return res

    @api.model
    def create(self, vals):
        if vals.get('name')== False:
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
        return super(sale_order, self).create(vals)

    @api.multi
    def action_confirm(self):
        super(sale_order, self).action_confirm()
        return True

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].sudo().precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    invoice = inv_obj.sudo().create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                    invoice['sale_order_id'] = order.id
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(
                            ', ') and order.client_order_ref != invoices[group_key].name:
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].sudo().write(vals)
                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoices[group_key]] |= order
        if not invoices:
            raise UserError(_('There is no invoiceable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoiceable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                                           values={'self': invoice, 'origin': references[invoice]},
                                           subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]


class res_partner(models.Model):
    """Extends the res_partner model (mainly for customer in this case) with an extra m2m
       field type of event"""

    _inherit = 'res.partner'

    event_type_id = fields.Many2one('event.type', string= 'Professional Body')
    idpassport = fields.Char(string='ID/Passport No.')
    vat_no_comp = fields.Char(string='VAT No.')
    cq_password = fields.Char(string='Portal Password')
    findout = fields.Selection([
                             ('1', 'Friend or Colleague'),
                             ('2', 'Institute'),
                             ('3', 'Internet Search Engine'),
                             ('4', 'Advertisement'),
                             ('5', 'Other')], string='Find Out')


class sale_order_line(models.Model):
    """Extends the sale.order.line model to add onchange function to that adds the price when event is chosen"""

    _inherit = 'sale.order.line'

    @api.model
    def create(self, values):
        for each in self.event_id:
            if not each.event_id:
                event = self.env['event.event'].browse(each.event_id.id)
                if not event.pc_exam:
                    each.name = event.name
        return super(sale_order_line, self).create(values)

    @api.onchange('event_id', 'product_id')
    def event_change(self):
        if not self.event_id:
            self.name = ''
        else:
            event_obj =self.env['event.event']
            event = event_obj.browse(self.event_id.id)
            self.price_unit = event.price
            if not event.pc_exam:
                name = event.name
                # if event.study:
                #     name += " - " +event.study.name
                self.name = name

class product(models.Model):

    _inherit = 'product.product'

    fee_ok = fields.Boolean(string='Remmittance Fee', help='Determine if a product is a fee and if its linked to events and qualification levels')
    event_rem = fields.Many2one('event.event', string='Remittance Event ')
    event_type_rem = fields.Many2one('event.type', string='Remittance Course Category')
    event_qual_rem = fields.Many2one('event.qual', string='Remittance Qualification Category')
    event_feetype_rem = fields.Many2one('event.feetype', string='Fee Type')


class event_portal_reg(models.Model):
    """Event Portal Registration"""
    _name = 'event.portal.reg'
      
    prof_body = fields.Many2one('event.type', string='Professional Body')
    campus = fields.Many2one('res.partner', string='Campus')
    course = fields.Many2many('event.event', string='Courses')
    fees = fields.Many2many('product.product', string='Fees')
    spons = fields.Boolean(string='Sponsorship')
    student = fields.Many2one('res.partner', string='Student')
    quotation = fields.Many2one('sale.order', string='Sales Order')
    invoice = fields.Many2one('account.invoice', string='Invoice')
    reg = fields.Many2one('event.registration', string='Event Registration')


class account_invoice_inh(models.Model):

    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line_ids')
    def _check_for_fees(self):
        for invoice in self:
          for line in invoice.invoice_line_ids:
            if line['product_id']['fee_ok']:
              self.fee_on_invoice = True

    sale_order_id = fields.Many2one('sale.order', 'Sale Order Link')
    paid_body = fields.Boolean('Paid Body')
    fee_on_invoice = fields.Boolean(compute='_check_for_fees',
                                      store=True,
                                      string='Fees on Invoice')
    quote_type = fields.Selection(related='sale_order_id.quote_type', string='Quote type', readonly=True)
    # semester = fields.Selection(related='sale_order_id.semester_id', string='Semester', readonly=True)
    affiliation = fields.Selection(related='sale_order_id.affiliation', string='Sponsorship', readonly=True)
    campus = fields.Many2one(related='sale_order_id.campus', relation='res.partner', string='Campus', readonly=True)
    prof_body = fields.Many2one(related='sale_order_id.prof_body', type='many2one', relation='event.type',
                                string='Prof Body', readonly=True)
    semester_id = fields.Many2one(related='sale_order_id.semester_id',string='Semester', readonly=True)

    @api.multi
    def action_paid_body(self):
        self.paid_body = True
        return True
