from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    duration = fields.Float(string="Service Duration",store=True)
    internal_use = fields.Boolean(string="Internal Use", default=False)
    
class ProductProduct(models.Model):
    _inherit = 'product.product'

    duration = fields.Float(string="Service Duration", related='product_tmpl_id.duration', store=True)
    internal_use = fields.Boolean(string="Internal Use", related='product_tmpl_id.internal_use',store=True)