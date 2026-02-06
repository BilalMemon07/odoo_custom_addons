from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError,UserError
import logging
_logger = logging.getLogger(__name__)

class PosTip(models.Model):
    _name = "pos.tip"
    _description = "Point of Sale Tip"

    name = fields.Char(string='Tip Name', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    amount = fields.Float(string='Tip Amount', required=True)
    pos_order_id = fields.Many2one('pos.order', string='POS Order', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Resource', readonly=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, readonly=True)
    payment_method = fields.Char(string="Payment Method")

    @api.model
    def create(self,vals):
        seq = self.env['ir.sequence'].next_by_code('seq.tip') or '/'
        vals['name'] = seq
        _logger.info(f"Created Tip: {vals['name']}")
        return super(PosTip, self).create(vals)