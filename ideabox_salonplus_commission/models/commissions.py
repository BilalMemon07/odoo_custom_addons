from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError,UserError
import logging
_logger = logging.getLogger(__name__)


class ResourceCommission(models.Model):
    _name = "resource.commission"
    _description = "Resource Commission"

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    amount = fields.Float(string='Amount', required=True)
    pos_order_id = fields.Many2one('pos.order', string='POS Order', readonly=True,required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Resource', readonly=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
    commission_type = fields.Selection([
        ('onsite', 'Onsite Service'),
        ('offsite', 'Offsite Service'),
        ('referral', 'Referral'),
    ], string="Commission Type", readonly=True)
    
    @api.model
    def create(self,vals):
        seq = self.env['ir.sequence'].next_by_code('seq.commission') or '/'
        vals['name'] = seq
        _logger.info(f"Created Commission: {vals['name']}")
        return super(ResourceCommission, self).create(vals)
    
    