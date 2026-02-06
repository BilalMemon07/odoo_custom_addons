from odoo import fields, models, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    discount_amount = fields.Float(string="Discount Amount", readonly=True, compute='compute_discount_amount',store=True)
    
    @api.depends('price_unit', 'qty', 'discount')
    def compute_discount_amount(self):
        for line in self:
            line.discount_amount = (line.price_unit * line.qty) * (line.discount / 100)