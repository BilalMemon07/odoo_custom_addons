# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import models, fields, api, _, Command
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round
from odoo.tools.misc import clean_context, OrderedSet


class SaleReturn(models.Model):
    _name = 'sale.return'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "sale return management"
    _order = 'id desc'

    @api.model
    def _get_default_journal(self):
        journal = self.env['account.journal'].sudo().search(
            [('type', '=', 'sale'), ('company_id', '=', self.env.company.id)], limit=1)
        if journal:
            return journal

    @api.model
    def _get_picking_type(self):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', self.env.company.id),
             ('return_picking_type_id.name', '=', 'Returns')])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'incoming'), ('warehouse_id', '=', False),
                 ('return_picking_type_id.name', '=', 'Returns')])
        return picking_type[:1]

    name = fields.Char(string="Name", copy=False, readonly=True, default=lambda x: _('New'))
    date_order = fields.Datetime('Order Date', required=True, default=fields.Datetime.now())
    # sale_order_id = fields.Many2one('sale.order', string="Sale Order", track_visibility='always')
    invoice_id = fields.Many2one('account.move', string="Customer Invoice", 
                            domain=[('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
                            track_visibility='always')
    location_id = fields.Many2one('stock.location', string="Return Location", track_visibility='always')
    picking_ids = fields.One2many('stock.picking', 'sale_return_id', string="Return Picking", track_visibility='always')
    partner_id = fields.Many2one("res.partner", string='Customer', track_visibility='always', required=True)
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='State', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    order_line_ids = fields.One2many('sale.return.line', 'order_id', string='Return Lines',
                                     states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    return_journal_id = fields.Many2one('account.journal', string='Return Journal', required=True,
                                        default=_get_default_journal)
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')
    picking_count = fields.Integer(string='Picking', compute='_compute_invoice_count')
    sale = fields.Boolean(string="From Sale Order")
    invoice_ids = fields.One2many('account.move', 'sale_return_id', string="Invoice")
    location_id = fields.Many2one('stock.location', 'Receive To')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, copy=False,
                                 default=lambda self: self.env.company.id)
    picking_type_id = fields.Many2one('stock.picking.type', 'Receive To',
                                      required=True, default=_get_picking_type, domain=[('code', '=', 'incoming')])
    warehouse_view_location_id = fields.Many2one(related='picking_type_id.warehouse_id.view_location_id',
                                                 string='Warehouse View Location',
                                                 readonly=True)
    default_location_dest_id_usage = fields.Selection(related='picking_type_id.default_location_dest_id.usage',
                                                      string='Destination Location Type',
                                                      readonly=True)
    reason_id = fields.Many2one('sale.return.reason', string="Reason", required=True, track_visibility='always')
    reference = fields.Char(string="Reference", track_visibility='always', copy=False)
    total = fields.Monetary(compute='_compute_total_amount', store=True, currency_field='currency_id')
    amount_tax = fields.Monetary(compute='_compute_total_amount', string="Tax", store=True,
                                 currency_field='currency_id')
    amount_untax = fields.Monetary(compute='_compute_total_amount', string="Amount Un Tax", store=True,
                                   currency_field='currency_id')
    sales_person_n = fields.Many2one('res.users', string='SalePersons')

    # pricelist_id = fields.Many2one(
    #     'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
    #     required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
    #     domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
    #     help="If you change the pricelist, only newly added lines will be affected.")
    # currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True)
    # show_update_pricelist = fields.Boolean(string='Has Pricelist Changed',
    #                                        help="Technical Field, True if the pricelist was changed;\n"
    #                                             " this will then display a recomputation button")
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id.id
    )       
    fiscal_position_id = fields.Many2one(
        comodel_name='account.fiscal.position',
        string="Fiscal Position",
        compute='_compute_fiscal_position_id',
        store=True, readonly=False, precompute=True, check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
             "The default value comes from the customer.",
        domain="[('company_id', '=', company_id)]")

    is_sale_return_manager = fields.Boolean(compute='_compute_group_return')

    @api.depends('partner_id')
    def _compute_group_return(self):
        for rec in self:
            if self.env.user.has_group('wedo_sale_return.group_sale_return_manager'):
                rec.is_sale_return_manager = True

            else:
                rec.is_sale_return_manager = False

    @api.depends('partner_id', 'company_id')
    def _compute_fiscal_position_id(self):
        """
        Trigger the change of fiscal position when the shipping address is modified.
        """
        cache = {}
        for order in self:
            if not order.partner_id:
                order.fiscal_position_id = False
                continue
            key = (order.company_id.id, order.partner_id.id)
            if key not in cache:
                cache[key] = self.env['account.fiscal.position'].with_company(order.company_id)._get_fiscal_position(
                    order.partner_id)
            order.fiscal_position_id = cache[key]

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id and self.partner_id.user_id:
            self.sales_person_n = self.partner_id.user_id
            if not self.sales_person_n.default_picking_type.id:
                raise ValidationError(
                    _("Please assign default picking type of the selected sales person attached with this customer"))
            else:
                self.picking_type_id = self.sales_person_n.default_picking_type.id
        else:
            self.sales_person_n = False
            self.picking_type_id = False
            self.location_id = False

    @api.onchange('sales_person_n')
    def set_picking_type(self):
        for rec in self:
            if rec.partner_id and rec.sales_person_n and not rec.sales_person_n.default_picking_type.id:
                raise ValidationError(_("Please assign default picking type of the selected sales person"))
            else:
                rec.picking_type_id = rec.sales_person_n.default_picking_type.id

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        self.location_id = self.picking_type_id.warehouse_id.lot_stock_id.id

    # @api.onchange('pricelist_id', 'order_line_ids')
    # def _onchange_pricelist_id(self):
    #     if self.order_line_ids and self.pricelist_id and not self.sale and self.partner_id.property_product_pricelist != self.pricelist_id:
    #         self.show_update_pricelist = True
    #     else:
    #         self.show_update_pricelist = False

    _sql_constraints = [
        ('reference_uniq', 'unique (reference)', "This Reference already exists !"),
    ]

    @api.depends('order_line_ids.price_subtotal', 'order_line_ids.tax_id')
    def _compute_total_amount(self):
        for rec in self:
            rec.amount_untax = sum(rec.order_line_ids.mapped('price_untax')) if rec.order_line_ids else 0.0
            rec.amount_tax = sum(rec.order_line_ids.mapped('price_tax')) if rec.order_line_ids else 0.0
            rec.total = sum(rec.order_line_ids.mapped('price_subtotal')) if rec.order_line_ids else 0.0

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise ValidationError(_("You can not delete confirmed Requests"))
            else:
                return super(SaleReturn, rec).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        records = super(SaleReturn, self).create(vals_list)
        for record in records:
            if not record.name or record.name == _('New'):
                record.name = self.env['ir.sequence'].sudo().next_by_code('sale.return.sequence') or _('New')
        return records

    def _compute_invoice_count(self):
        for rec in self:
            rec.picking_count = len(rec.picking_ids)
            rec.invoice_count = len(rec.invoice_ids)

    def action_open_picking_invoice(self):
        return {
            'name': 'Invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', self.invoice_ids.ids), ],
            'context': {'create': False},
            'target': 'current'
        }

    def action_open_picking(self):
        return {
            'name': 'Picking',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'res_model': 'stock.picking',
            'domain': [('id', '=', self.picking_ids.ids)],
            'target': 'current'
        }

    # @api.onchange('sale_order_id', 'sale')
    # def get_line(self):
    #     for rec in self:
    #         if rec.sale:
    #             if rec.sale_order_id:
    #                 rec.order_line_ids = False
    #                 rec.currency_id = False
    #                 lines = []
    #                 for order in rec.sale_order_id.order_line:
    #                     vals = self.get_line_vals(order)
    #                     lines.append((0, 0, vals))
    #                 rec.write({'order_line_ids': lines, 'pricelist_id': rec.sale_order_id.pricelist_id.id})
    #         else:
    #             rec.order_line_ids = False
    #             rec.sale_order_id = False

    @api.onchange('invoice_id', 'sale')
    def get_line(self):
        for rec in self:
            if rec.sale:
                if rec.invoice_id:
                    rec.order_line_ids = False
                    rec.currency_id = rec.invoice_id.currency_id.id
                    lines = []
                    for invoice_line in rec.invoice_id.invoice_line_ids:
                        vals = self.get_line_vals(invoice_line)
                        lines.append((0, 0, vals))
                    rec.write({
                        'order_line_ids': lines,
                        'partner_id': rec.invoice_id.partner_id.id
                    })
            else:
                rec.order_line_ids = False
                rec.invoice_id = False

    # def get_line_vals(self, order):
    #     vals = {
    #         'sale_order_id': order.id,
    #         'name': order.name,
    #         'display_type': order.display_type if order.display_type in ['line_section', 'line_note'] else False,
    #         'product_id': order.product_id.id,
    #         'product_qty': order.product_uom_qty,
    #         'qty_return': order.product_uom_qty - order.returned_qty,
    #         'product_uom': order.product_uom.id,
    #         'tax_id': [(6, 0, order.tax_id.ids)],
    #         'discount': order.discount,
    #         'price_unit': order.price_unit, }
    #     return vals

    def get_line_vals(self, invoice_line):
        vals = {
            'invoice_line_id': invoice_line.id,
            'name': invoice_line.name,
            'display_type': invoice_line.display_type if invoice_line.display_type in ['line_section', 'line_note'] else False,
            'product_id': invoice_line.product_id.id,
            'product_qty': invoice_line.quantity,
            'qty_return': invoice_line.quantity - invoice_line.returned_qty,
            'product_uom': invoice_line.product_uom_id.id,
            'tax_id': [(6, 0, invoice_line.tax_ids.ids)],
            'discount': invoice_line.discount,
            'price_unit': invoice_line.price_unit,
        }
        return vals
    
    @api.onchange('partner_id')
    def chang_partner(self):
        for rec in self:
            rec.order_line_ids = False
            rec.invoice_id = False
            # rec.pricelist_id = rec.partner_id.property_product_pricelist.id if not rec.sale else False

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'

    # def action_process(self):
    #     if self.order_line_ids:
    #         returns = self.order_line_ids.filtered(lambda r: r.qty_return > 0 and r.display_type == False)
    #         if returns:
    #             self.create_picking_returns(returns)
    #             if self.sale_order_id:
    #                 for line in self.order_line_ids:
    #                     if line.sale_order_id:
    #                         line.sale_order_id.returned_qty += line.qty_return
    #         else:
    #             raise ValidationError(_("No line to return picking"))
    #         self.state = 'done'
    #     else:
    #         raise ValidationError(_("No lines"))


    def action_process(self):
        if self.order_line_ids:
            returns = self.order_line_ids.filtered(lambda r: r.qty_return > 0 and r.display_type == False)
            if returns:
                self.create_picking_returns(returns)
                for line in self.order_line_ids:
                    if line.invoice_line_id:
                        line.invoice_line_id.returned_qty += line.qty_return
            else:
                raise ValidationError(_("No line to return picking"))
            self.state = 'done'
        else:
            raise ValidationError(_("No lines"))

    def action_cancel(self):
        for rec in self:
            if rec.state == 'done' and rec.picking_ids.filtered(lambda r: r.state == 'done'):
                raise ValidationError(_("You can not cancel processed request"))
            else:
                rec.state = "cancel"
                picks = rec.picking_ids.filtered(lambda r: r.state not in ['done', 'cancel'])
                if picks:
                    for picking_id in picks:
                        picking_id.sudo().action_cancel()

    def action_reset_draft(self):
        for rec in self:
            if rec.state == 'done' and rec.picking_ids.filtered(lambda r: r.state == 'done'):
                raise ValidationError(_("You can not reset processed request"))
            else:
                rec.state = 'draft'

    def create_picking_returns(self, returns_line):
        data = self.creat_pick()
        customer_picking = self.env['stock.picking'].sudo().create(data)

        for re in returns_line:
            vals = self.get_stock_vals(customer_picking, re)
            self.env['stock.move'].sudo().create(vals)
            customer_picking.sudo().action_assign()
            # immediate_transfer_line_ids = []
            # for line in self.customer_move:
            #     immediate_transfer_line_ids.append([0, False, {
            #     'picking_id': line.picking_id.id,
            #     'to_immediate': True
            #     }])
            # res = self.env['stock.immediate.transfer'].create({
            #  'pick_ids': [(4, p.picking_id.id) for p in self.move_lines],
            #
            # })customer_picking.sudo().button_validate()

    def creat_pick(self):
        data = {
            'location_id': self.picking_type_id.default_location_src_id.id if self.picking_type_id.default_location_src_id
            else self.partner_id.property_stock_customer.id,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'partner_id': self.partner_id.id,
            'picking_type_id': self.picking_type_id.id,
            'is_from_sale_return': True,
            'sale_return_id': self.id,
            'origin': self.name, }
        return data

    def get_stock_vals(self, customer_picking, re):
        vals = {
            'name': 'Sale Return',
            'location_id': self.partner_id.property_stock_customer.id if self.partner_id.property_stock_customer
            else self.picking_type_id.default_location_src_id.id,
            'location_dest_id': self.picking_type_id.default_location_dest_id.id,
            'product_id': re.product_id.id,
            'product_uom': re.product_uom.id,
            # 'price_unit': re.price_unit,
            'product_uom_qty': re.qty_return,
            'picking_id': customer_picking.id,
            'sale_return_line_id': re.id,
        }
        return vals

    # def update_prices(self):
    #     self.ensure_one()
    #     lines_to_update = []
    #     for line in self.order_line_ids.filtered(lambda line: not line.display_type):
    #         product = line.product_id.with_context(
    #             partner=self.partner_id,
    #             quantity=line.qty_return,
    #             date=self.date_order,
    #             pricelist=self.pricelist_id.id,
    #             uom=line.product_uom.id
    #         )
    #         price_unit = self.env['account.tax']._fix_tax_included_price_company(
    #             line._get_display_price(), line.product_id.taxes_id, line.tax_id, line.company_id)
    #         lines_to_update.append((1, line.id, {'price_unit': price_unit}))
    #     self.update({'order_line_ids': lines_to_update})
    #     self.show_update_pricelist = False
    #     self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ",
    #                              self.pricelist_id.display_name))

    @api.depends('invoice_ids', 'invoice_ids.state')
    def reconcile_return_move_line(self):
        if self.invoice_ids:
            account_move_lines = self.env['account.move.line']
            account = []
            flag = True
            for invoice in self.invoice_ids:
                if invoice.state != "posted":
                    flag = False
            if flag:
                for order in self.order_line_ids:
                    account.append(order.product_id.categ_id.property_stock_account_output_categ_id.id)
                for picking in self.picking_ids:
                    account_move_lines += account_move_lines.search([('ref', 'like', picking.name)])

                to_reconcile_account_move_lines = account_move_lines.filtered(
                    lambda l: not l.reconciled and l.account_id.id in account and l.account_id.reconcile)
                return to_reconcile_account_move_lines.reconcile()


class SaleReturnLine(models.Model):
    _name = 'sale.return.line'

    sequence = fields.Integer(string='Sequence', default=10)
    product_qty = fields.Float(string='Sale Quantity', digits='Product Unit of Measure')
    product_id = fields.Many2one('product.product', string='Product')
    order_id = fields.Many2one('sale.return', string='Return Order', index=True,
                               ondelete='cascade')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    name = fields.Text(string='Description', required=True)

    # sale_order_id = fields.Many2one('sale.order.line', string='Sale Order line', )
    invoice_line_id = fields.Many2one('account.move.line', string='Invoice line')
    state = fields.Selection(related='order_id.state', store=True, )
    qty_return = fields.Float("Return Qty", digits='Product Unit of Measure')
    received_qty = fields.Float("Received Qty", compute="get_qty_amount", store=True, digits='Product Unit of Measure')
    invoiced_qty = fields.Float("Invoiced Qty", compute="get_qty_amount", store=True, digits='Product Unit of Measure')
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True)
    date_order = fields.Datetime(related='order_id.date_order', string='Order Date')
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)],
                              compute="_compute_tax_id",
                              store=True, readonly=False,
                              precompute=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    price_unit = fields.Float('Unit Price', digits='Product Price', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', currency_field='currency_id',
                                     readonly=True, store=True)
    currency_id = fields.Many2one("res.currency", related='order_id.currency_id', string="Currency", readonly=True,
                                  store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    price_untax = fields.Float(compute='_compute_amount', string='UnTax', store=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, copy=False,
                                 related='order_id.company_id')
    # pricelist_item_id = fields.Many2one(
    #     comodel_name='product.pricelist.item',
    #     compute='_compute_pricelist_item_id')
    product_uom_qty = fields.Float(
        string="Quantity",
        compute='_compute_product_uom_qty',
        digits='Product Unit of Measure', default=1.0,
        store=True, readonly=False, required=True, precompute=True)
    product_packaging_qty = fields.Float(
        string="Packaging Quantity",
        compute='_compute_product_packaging_qty',
        store=True, readonly=False, precompute=True)
    product_packaging_id = fields.Many2one(
        comodel_name='product.packaging',
        string="Packaging",
        compute='_compute_product_packaging_id',
        store=True, readonly=False, precompute=True,
        domain="[('sales', '=', True), ('product_id','=',product_id)]",
        check_company=True)
    product_no_variant_attribute_value_ids = fields.Many2many(
        comodel_name='product.template.attribute.value',
        string="Extra Values",
        # compute='_compute_no_variant_attribute_values',
        # store=True, readonly=False, precompute=True,
        ondelete='restrict')

    discount = fields.Float(
        string="Discount (%)",
        digits='Discount', )

    @api.depends('product_id', 'company_id')
    def _compute_tax_id(self):
        taxes_by_product_company = defaultdict(lambda: self.env['account.tax'])
        lines_by_company = defaultdict(lambda: self.env['sale.return.line'])
        cached_taxes = {}
        for line in self:
            lines_by_company[line.company_id] += line
        for product in self.product_id:
            for tax in product.taxes_id:
                taxes_by_product_company[(product, tax.company_id)] += tax
        for company, lines in lines_by_company.items():
            for line in lines.with_company(company):
                taxes = taxes_by_product_company[(line.product_id, company)]
                if not line.product_id or not taxes:
                    # Nothing to map
                    line.tax_id = False
                    continue
                fiscal_position = line.order_id.fiscal_position_id
                cache_key = (fiscal_position.id, company.id, tuple(taxes.ids))
                if cache_key in cached_taxes:
                    result = cached_taxes[cache_key]
                else:
                    result = fiscal_position.map_tax(taxes)
                    cached_taxes[cache_key] = result
                # If company_id is set, always filter taxes by the company
                line.tax_id = result

    @api.depends('product_packaging_id', 'product_uom', 'product_uom_qty')
    def _compute_product_packaging_qty(self):
        for line in self:
            if not line.product_packaging_id:
                line.product_packaging_qty = False
            else:
                packaging_uom = line.product_packaging_id.product_uom_id
                packaging_uom_qty = line.product_uom._compute_quantity(line.product_uom_qty, packaging_uom)
                line.product_packaging_qty = float_round(
                    packaging_uom_qty / line.product_packaging_id.qty,
                    precision_rounding=packaging_uom.rounding)

    @api.depends('product_id', 'product_uom_qty', 'product_uom')
    def _compute_product_packaging_id(self):
        for line in self:
            # remove packaging if not match the product
            if line.product_packaging_id.product_id != line.product_id:
                line.product_packaging_id = False
            # Find biggest suitable packaging
            if line.product_id and line.product_uom_qty and line.product_uom:
                line.product_packaging_id = line.product_id.packaging_ids.filtered(
                    'sales')._find_suitable_product_packaging(line.product_uom_qty,
                                                              line.product_uom) or line.product_packaging_id

    @api.depends('display_type', 'product_id', 'product_packaging_qty')
    def _compute_product_uom_qty(self):
        for line in self:
            if line.display_type:
                line.product_uom_qty = 0.0
                continue

            if not line.product_packaging_id:
                continue
            packaging_uom = line.product_packaging_id.product_uom_id
            qty_per_packaging = line.product_packaging_id.qty
            product_uom_qty = packaging_uom._compute_quantity(
                line.product_packaging_qty * qty_per_packaging, line.product_uom)
            if float_compare(product_uom_qty, line.product_uom_qty, precision_rounding=line.product_uom.rounding) != 0:
                line.product_uom_qty = product_uom_qty

    @api.depends('order_id.invoice_ids', 'order_id.picking_ids', 'order_id.picking_ids.state')
    def get_qty_amount(self):
        for rec in self:
            rec.invoiced_qty = sum(
                rec.order_id.invoice_ids.invoice_line_ids.filtered(lambda r: r.sale_return_line_id == rec).mapped(
                    'quantity'))
            rec.received_qty = sum(rec.order_id.picking_ids.move_ids_without_package.filtered(
                lambda r: r.sale_return_line_id == rec and r.picking_id.state == 'done').mapped('quantity'))

    @api.depends('qty_return', 'price_unit', 'discount', 'currency_id', 'tax_id')
    def _compute_amount(self):
        for line in self:
            price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(
                price_reduce, 
                line.order_id.currency_id, 
                line.qty_return,
                product=line.product_id, 
                partner=line.order_id.partner_id
            )
            line.price_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
            line.price_untax = line.qty_return * price_reduce
            line.price_subtotal = line.qty_return * price_reduce + line.price_tax
   
    @api.constrains("product_id")
    def _check_product_id(self):
        for line in self:
            if line.product_id.standard_price == 0.0:
                raise ValidationError(
                    _(
                        "The product must be Costed"
                    )
                )

    @api.onchange('product_id')
    def get_unit_uom(self):
        self.product_uom = self.product_id.uom_id.id
        self.name = self.product_id.name if self.product_id else ""

    # @api.depends('product_id', 'product_uom', 'product_uom_qty')
    # def _compute_pricelist_item_id(self):
    #     for line in self:
    #         if not line.product_id or line.display_type or not line.order_id.pricelist_id:
    #             line.pricelist_item_id = False
    #         else:
    #             line.pricelist_item_id = line.order_id.pricelist_id._get_product_rule(
    #                 line.product_id,
    #                 line.product_uom_qty or 1.0,
    #                 uom=line.product_uom,
    #                 date=line.order_id.date_order,
    #             )

    # def _get_pricelist_price(self):
    #     self.ensure_one()
    #     self.product_id.ensure_one()
    #     pricelist_rule = self.pricelist_item_id
    #     order_date = self.order_id.date_order or fields.Date.today()
    #     product = self.product_id.with_context(**self._get_product_price_context())
    #     qty = self.product_uom_qty or 1.0
    #     uom = self.product_uom or self.product_id.uom_id
    #     price = pricelist_rule._compute_price(
    #         product, qty, uom, order_date, currency=self.currency_id)

    #     return price

    # def _get_display_price(self):
    #     self.ensure_one()
    #     pricelist_price = self._get_pricelist_price()
    #     if self.order_id.pricelist_id.discount_policy == 'with_discount':
    #         return pricelist_price
    #     if not self.pricelist_item_id:
    #         # No pricelist rule found => no discount from pricelist
    #         return pricelist_price
    #     base_price = self._get_pricelist_price_before_discount()
    #     # negative discounts (= surcharge) are included in the display price
    #     return max(base_price, pricelist_price)

    # def _get_product_price_context(self):
    #     """Gives the context for product price computation.

    #     :return: additional context to consider extra prices from attributes in the base product price.
    #     :rtype: dict
    #     """
    #     self.ensure_one()
    #     res = {}

    #     # It is possible that a no_variant attribute is still in a variant if
    #     # the type of the attribute has been changed after creation.
    #     no_variant_attributes_price_extra = [
    #         ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
    #             lambda ptav:
    #             ptav.price_extra and
    #             ptav not in self.product_id.product_template_attribute_value_ids
    #         )
    #     ]
    #     if no_variant_attributes_price_extra:
    #         res['no_variant_attributes_price_extra'] = tuple(no_variant_attributes_price_extra)

    #     return res

    # @api.onchange('product_uom', 'qty_return','product_id','order_id.pricelist_id')
    # def product_uom_change(self):
    #     if self.order_id.pricelist_id and self.order_id.partner_id:
    #         product = self.product_id.with_context(
    #             lang=self.order_id.partner_id.lang,
    #             partner=self.order_id.partner_id,
    #             quantity=self.qty_return,
    #             date=self.order_id.date_order,
    #             pricelist=self.order_id.pricelist_id.id,
    #             uom=self.product_uom.id,
    #             fiscal_position=self.env.context.get('fiscal_position')
    #         )
    #         self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(),
    #                                                                                   product.taxes_id, self.tax_id,
    #                                                                                   self.company_id)
    @api.onchange('product_uom', 'product_id')
    def product_uom_change(self):
        """Simplified version without pricelist considerations"""
        if not self.product_id:
            return
        self.price_unit = self.product_id.lst_price
        self.product_uom = self.product_id.uom_id.id

    # @api.onchange('qty_return')
    # def onchange_qty_return(self):
    #     for rec in self:
    #         if rec.sale_order_id and rec.qty_return > 0:
    #             if (rec.sale_order_id.returned_qty + rec.qty_return) > rec.sale_order_id.product_uom_qty:
    #                 raise ValidationError(_("Return quantity should be less than or equal to the bought quantity"))

    @api.onchange('qty_return')
    def onchange_qty_return(self):
        for rec in self:
            if rec.invoice_line_id and rec.qty_return > 0:
                if (rec.invoice_line_id.returned_qty + rec.qty_return) > rec.invoice_line_id.quantity:
                    raise ValidationError(_("Return quantity should be less than or equal to the invoiced quantity"))
                
class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_return_id = fields.Many2one('sale.return', string='Return')
    picking_id = fields.Many2one("stock.picking", string="Picking")
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft', store=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sale_return_line_id = fields.Many2one('sale.return.line', string='Sale Return')

    def _stock_account_get_anglo_saxon_price_unit(self):
        self.ensure_one()
        price_unit = super(AccountMoveLine, self)._stock_account_get_anglo_saxon_price_unit()
        if self.move_id.move_type == 'out_refund' and self.move_id.picking_id and self.sale_return_line_id:
            scraps = self.env['stock.scrap'].search([('picking_id', '=', self.move_id.picking_id.id)])
            domain = [('product_id', '=', self.product_id.id),
                      ('id', 'in', (self.move_id.picking_id.move_ids + scraps.move_id).stock_valuation_layer_ids.ids)]
            valuation = self.env['stock.valuation.layer'].search(domain, limit=1)
            if valuation:
                price_unit = valuation.unit_cost

        return price_unit


class SaleReturnReason(models.Model):
    _name = 'sale.return.reason'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "sale return reason"
    _order = 'sequence'

    name = fields.Char(string="Reason", required=True, track_visibility='always')
    sequence = fields.Integer(string="Sequence", default=10)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "This Reason already exists !"),
    ]


# class StockMoveInherit(models.Model):
#     _inherit = 'stock.move'
#
#     def _action_confirm(self, merge=False, merge_into=False):
#         """ Confirms stock move or put it in waiting if it's linked to another move.
#         :param: merge: According to this boolean, a newly confirmed move will be merged
#         in another move of the same picking sharing its characteristics.
#         """
#         # Use OrderedSet of id (instead of recordset + |= ) for performance
#         move_create_proc, move_to_confirm, move_waiting = OrderedSet(), OrderedSet(), OrderedSet()
#         to_assign = defaultdict(OrderedSet)
#         for move in self:
#             if move.state != 'draft':
#                 continue
#             # if the move is preceded, then it's waiting (if preceding move is done, then action_assign has been called already and its state is already available)
#             if move.move_orig_ids:
#                 move_waiting.add(move.id)
#             else:
#                 if move.procure_method == 'make_to_order':
#                     move_create_proc.add(move.id)
#                 else:
#                     move_to_confirm.add(move.id)
#             if move._should_be_assigned():
#                 key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
#                 to_assign[key].add(move.id)
#
#         move_create_proc, move_to_confirm, move_waiting = self.browse(move_create_proc), self.browse(
#             move_to_confirm), self.browse(move_waiting)
#
#         # create procurements for make to order moves
#         procurement_requests = []
#         for move in move_create_proc:
#             values = move._prepare_procurement_values()
#             origin = move._prepare_procurement_origin()
#             procurement_requests.append(self.env['procurement.group'].Procurement(
#                 move.product_id, move.product_uom_qty, move.product_uom,
#                 move.location_id, move.rule_id and move.rule_id.name or "/",
#                 origin, move.company_id, values))
#         self.env['procurement.group'].run(procurement_requests,
#                                           raise_user_error=not self.env.context.get('from_orderpoint'))
#
#         move_to_confirm.write({'state': 'confirmed'})
#         (move_waiting | move_create_proc).write({'state': 'waiting'})
#         # procure_method sometimes changes with certain workflows so just in case, apply to all moves
#         (move_to_confirm | move_waiting | move_create_proc).filtered(
#             lambda m: m.picking_type_id.reservation_method == 'at_confirm') \
#             .write({'reservation_date': fields.Date.today()})
#
#         # assign picking in batch for all confirmed move that share the same details
#         for moves_ids in to_assign.values():
#             self.browse(moves_ids).with_context(clean_context(self.env.context))._assign_picking()
#         new_push_moves = self.filtered(lambda m: not m.picking_id.immediate_transfer)._push_apply()
#         self._check_company()
#         moves = self
#         if merge:
#             moves = self._merge_moves(merge_into=merge_into)
#
#         # Transform remaining move in return in case of negative initial demand
#         neg_r_moves = moves.filtered(lambda move: float_compare(
#             move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding) < 0)
#         for move in neg_r_moves:
#             move.location_id, move.location_dest_id = move.location_dest_id, move.location_id
#             orig_move_ids, dest_move_ids = [], []
#             for m in move.move_orig_ids | move.move_dest_ids:
#                 from_loc, to_loc = m.location_id, m.location_dest_id
#                 if float_compare(m.product_uom_qty, 0, precision_rounding=m.product_uom.rounding) < 0:
#                     from_loc, to_loc = to_loc, from_loc
#                 if to_loc == move.location_id:
#                     orig_move_ids += m.ids
#                 elif move.location_dest_id == from_loc:
#                     dest_move_ids += m.ids
#             move.move_orig_ids, move.move_dest_ids = [(6, 0, orig_move_ids)], [(6, 0, dest_move_ids)]
#             move.product_uom_qty *= -1
#             if move.picking_type_id.return_picking_type_id:
#                 move.picking_type_id = move.picking_type_id.return_picking_type_id
#             # We are returning some products, we must take them in the source location
#             move.procure_method = 'make_to_stock'
#         neg_r_moves._assign_picking()
#
#         # call `_action_assign` on every confirmed move which location_id bypasses the reservation + those expected to be auto-assigned
#         moves.filtered(lambda move: not move.picking_id.immediate_transfer
#                                     and move.state in ('confirmed', 'partially_available')
#                                     and (move._should_bypass_reservation()
#                                          or move.picking_type_id.reservation_method == 'at_confirm'
#                                          or (move.reservation_date and move.reservation_date <= fields.Date.today()))) \
#             ._action_assign()
#         if new_push_moves:
#             neg_push_moves = new_push_moves.filtered(
#                 lambda sm: float_compare(sm.product_uom_qty, 0, precision_rounding=sm.product_uom.rounding) < 0)
#             (new_push_moves - neg_push_moves)._action_confirm()
#             # Negative moves do not have any picking, so we should try to merge it with their siblings
#             neg_push_moves._action_confirm(merge_into=neg_push_moves.move_orig_ids.move_dest_ids)
#
#         return moves

class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    def _action_confirm(self, merge=False, merge_into=False):
        """ Confirms stock move or put it in waiting if it's linked to another move.
        :param: merge: According to this boolean, a newly confirmed move will be merged
        in another move of the same picking sharing its characteristics.
        """
        move_create_proc, move_to_confirm, move_waiting = OrderedSet(), OrderedSet(), OrderedSet()
        to_assign = defaultdict(OrderedSet)
        for move in self:
            if move.state != 'draft':
                continue
            if move.move_orig_ids:
                move_waiting.add(move.id)
            elif move.procure_method == 'make_to_order':
                move_create_proc.add(move.id)
            else:
                move_to_confirm.add(move.id)
            if move._should_be_assigned():
                key = (move.group_id.id, move.location_id.id, move.location_dest_id.id)
                to_assign[key].add(move.id)

        move_create_proc, move_to_confirm, move_waiting = self.browse(move_create_proc), self.browse(
            move_to_confirm), self.browse(move_waiting)

        procurement_requests = []
        for move in move_create_proc:
            values = move._prepare_procurement_values()
            origin = move._prepare_procurement_origin()
            procurement_requests.append(self.env['procurement.group'].Procurement(
                move.product_id, move.product_uom_qty, move.product_uom,
                move.location_id, move.rule_id and move.rule_id.name or "/",
                origin, move.company_id, values))
        self.env['procurement.group'].run(procurement_requests,
                                          raise_user_error=not self.env.context.get('from_orderpoint'))

        move_to_confirm.write({'state': 'confirmed'})
        (move_waiting | move_create_proc).write({'state': 'waiting'})
        (move_to_confirm | move_waiting | move_create_proc).filtered(
            lambda m: m.picking_type_id.reservation_method == 'at_confirm') \
            .write({'reservation_date': fields.Date.today()})

        for moves_ids in to_assign.values():
            self.browse(moves_ids).with_context(clean_context(self.env.context))._assign_picking()

        self._check_company()
        moves = self
        if merge:
            moves = self._merge_moves(merge_into=merge_into)

        neg_r_moves = moves.filtered(lambda move: float_compare(
            move.product_uom_qty, 0, precision_rounding=move.product_uom.rounding) < 0)

        neg_to_push = neg_r_moves.filtered(
            lambda move: move.location_final_id and move.location_dest_id != move.location_final_id)
        new_push_moves = neg_to_push._push_apply() if neg_to_push else self.env['stock.move']

        for move in neg_r_moves:
            move.location_id, move.location_dest_id, move.location_final_id = move.location_dest_id, move.location_id, move.location_id
            orig_move_ids, dest_move_ids = [], []
            for m in move.move_orig_ids | move.move_dest_ids:
                from_loc, to_loc = m.location_id, m.location_dest_id
                if float_compare(m.product_uom_qty, 0, precision_rounding=m.product_uom.rounding) < 0:
                    from_loc, to_loc = to_loc, from_loc
                if to_loc == move.location_id:
                    orig_move_ids += m.ids
                elif move.location_dest_id == from_loc:
                    dest_move_ids += m.ids
            move.move_orig_ids, move.move_dest_ids = [Command.set(orig_move_ids)], [Command.set(dest_move_ids)]
            move.product_uom_qty *= -1
            if move.picking_type_id.return_picking_type_id:
                move.picking_type_id = move.picking_type_id.return_picking_type_id
            move.procure_method = 'make_to_stock'
        neg_r_moves._assign_picking()

        moves.filtered(lambda move: move.state in ('confirmed', 'partially_available') and (
                move._should_bypass_reservation() or move.picking_type_id.reservation_method == 'at_confirm' or (
                move.reservation_date and move.reservation_date <= fields.Date.today()))) \
            ._action_assign()

        if new_push_moves:
            neg_push_moves = new_push_moves.filtered(
                lambda sm: float_compare(sm.product_uom_qty, 0, precision_rounding=sm.product_uom.rounding) < 0)
            (new_push_moves - neg_push_moves)._action_confirm()
            neg_push_moves._action_confirm(merge_into=neg_push_moves.move_orig_ids.move_dest_ids)

        return moves

class ResUserInheritForWarehouse(models.Model):
    _inherit = 'res.users'

    def _get_picking_domain(self):
        return [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', self.env.company.id),
                ('return_picking_type_id.name', '=', 'Returns')]

    default_picking_type = fields.Many2one('stock.picking.type', domain=lambda self: self._get_picking_domain())


class SaleOrderLineInheritForReturns(models.Model):
    _inherit = 'sale.order.line'

    returned_qty = fields.Float(string='Returned quantity')


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    returned_qty = fields.Float(string='Returned quantity')
    sale_return_line_id = fields.Many2one('sale.return.line', string='Sale Return')