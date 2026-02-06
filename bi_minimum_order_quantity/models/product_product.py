# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    min_qty = fields.Integer(string="Minimum Quantity Order", default=1)
    set_qty = fields.Integer(string="Set Quantity", compute="compute_set_qty")

    def compute_set_qty(self):
        min_qty = 1
        for product in self:
            product.set_qty = 1
            if not product.min_qty:
                product.write({"min_qty": min_qty})
