# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    min_qty = fields.Integer(string="Minimum Quantity Order", default=1)
    set_qty = fields.Integer(string="Set Quantity", compute="compute_set_qty")

    def compute_set_qty(self):
        min_qty = 1
        for product in self:
            product.set_qty = 1
            if not product.min_qty:
                product.write({"min_qty": min_qty})

    def _get_combination_info(
        self,
        combination=False,
        product_id=False,
        add_qty=1.0,
        parent_combination=False,
        only_template=False,
    ):
        res = super(ProductTemplate, self)._get_combination_info(
            combination, product_id, add_qty, parent_combination, only_template
        )
        product_id = self.env["product.product"].browse(res.get("product_id"))
        res.update({"default_min_qty": product_id.min_qty if product_id else False})
        return res
