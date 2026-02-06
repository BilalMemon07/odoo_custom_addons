from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
import json
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    total_commission = fields.Float(string="Total Commission")
    commission_count = fields.Integer(string="Commissions",compute="compute_commission_count")
    service_type = fields.Char(string="Service Type",readonly=True,store=True)
    employee_ids_char_commission = fields.Char(string="employee ids char commission")
    commission_ids = fields.One2many('resource.commission','pos_order_id', string='Commissions', readonly=True)

    
    @api.model
    def _process_order(self, order, existing_order):
        res = super()._process_order(order, existing_order)
        if not existing_order:
            pos_order = self.env['pos.order'].search([('id','=',res)])
            # raise UserError(str(order))  
            if 'commission_ids' in str(order):
                commission_list = order['commission_ids']
                order.pop('commission_ids')
                commissions = self.env['resource.commission'].search([('pos_order_id','=',pos_order.id)])
        
                if commissions:
                    commissions.unlink()
                for i in commission_list:
                    obj = {
                        'name': 'New',
                        'pos_order_id': pos_order.id,
                        'amount': i[2]['amount'],
                        'employee_id':i[2]['employee_id'],
                    }
                    if i[2]['amount'] > 0:
                        self.env['resource.commission'].create(obj)
            pos_order = pos_order.with_company(pos_order.company_id)
        return res
    
    @api.model
    def sync_from_ui(self,orders):
        data = orders[0].get('employee_ids_char_commission')
        if data:
            list_data = json.loads(data)
            commission_commands = [
                (0, 0, {
                    'employee_id': item['id'],
                    'amount': item['commission_amount'],
                })
                for item in list_data
            ]
            orders[0].update({
                'commission_ids': commission_commands
            })
        res = super().sync_from_ui(orders)
        return res


    def action_view_commission(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Commissions',
            'res_model': 'resource.commission', 
            'view_mode': 'list,form',         
            'target': 'current',       
            'domain': [('pos_order_id', '=', self.id)]
        }
        
    @api.depends('total_commission','name')
    def compute_commission_count(self):
        for i in self:
            i['commission_count'] = i.env['resource.commission'].search_count([('pos_order_id','=',i.id)])
            
            