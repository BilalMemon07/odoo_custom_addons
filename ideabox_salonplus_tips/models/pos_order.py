from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
import json
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    tip_ids = fields.One2many('pos.tip','pos_order_id', string='Tips', readonly=True)
    employee_ids_char = fields.Char(string="employee ids char")
    tip_count = fields.Integer(string="Tips",compute="compute_tip_count")
    services_str = fields.Char(string="Services", readonly=True,compute='_compute_services_str', store=True)
    services_total = fields.Float(string="Services Total", readonly=True, compute='_compute_total', store=True)
    products_total = fields.Float(string="Products Total", readonly=True, compute='_compute_total', store=True)
    partner_phone = fields.Char(string="Customer Phone", related='partner_id.phone', readonly=True,store=True)
    
    def _compute_total(self):
        for order in self:
            services_total = sum(line.price_subtotal for line in order.lines if line.product_id.type == 'service')
            product_total = sum(line.price_subtotal for line in order.lines if line.product_id.type == 'consu' and line.product_id.name != 'Discount')
            order.services_total = services_total
            order.products_total = product_total
    
    @api.depends('lines')
    def _compute_services_str(self):
        for order in self:
            services = order.lines.mapped('product_id')
            order.services_str = ', '.join(services.mapped('name')) if services else 'No Services'
    
    
    @api.model
    def _process_order(self, order, existing_order):
        res = super()._process_order(order, existing_order)
        if not existing_order:
            # raise UserError(str(order))
            pos_order = self.env['pos.order'].search([('id','=',res)])
            if 'tip_ids' in str(order):
                tip_list = order['tip_ids']
                order.pop('tip_ids')
                tips = self.env['pos.tip'].search([('pos_order_id','=',pos_order.id)])
        
                # raise UserError(str(tips))  
                if tips:
                    tips.unlink()
                for i in tip_list:
                    obj = {
                        'name': 'New',
                        'pos_order_id': pos_order.id,
                        'partner_id': pos_order.partner_id.id if pos_order.partner_id.id else False,
                        'amount': i[2]['amount'],
                        'employee_id':i[2]['employee_id'],
                    }
                    if i[2]['amount'] > 0:
                        self.env['pos.tip'].create(obj)
            pos_order = pos_order.with_company(pos_order.company_id)
        return res

    @api.model
    def sync_from_ui(self,orders):
        data = orders[0].get('employee_ids_char')
        if data:
            list_data = json.loads(data)
            tip_commands = [
                (0, 0, {
                    'employee_id': item['id'],
                    'amount': item['tip_amount'],
                })
                for item in list_data
            ]
            orders[0].update({
                'tip_ids': tip_commands
            })
        res = super().sync_from_ui(orders)
        return res
        
    def action_view_tips(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tips',
            'res_model': 'pos.tip', 
            'view_mode': 'list,form',         
            'target': 'current',       
            'domain': [('pos_order_id', '=', self.id)]
        }
        
    @api.depends('tip_amount','name')
    def compute_tip_count(self):
        for i in self:
            i['tip_count'] = i.env['pos.tip'].search_count([('pos_order_id','=',i.id)])

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    total_profit = fields.Float(string="Total Profit", readonly=True, compute='_compute_total_profit', store=True)

    @api.depends('total_amount','date','employee_id','name')
    def _compute_total_profit(self):
        pos_orders = self.env['pos.order'].search([])
        hr_expenses = self.env['hr.expense'].search([])

        sales = sum(pos_orders.mapped('amount_paid')) if pos_orders else 0.0
        expenses = sum(hr_expenses.mapped('total_amount')) if hr_expenses else 0.0
        profit = sales - expenses

        share = profit / len(hr_expenses) if hr_expenses else 0.0
        for expense in hr_expenses:
            expense.total_profit = share
