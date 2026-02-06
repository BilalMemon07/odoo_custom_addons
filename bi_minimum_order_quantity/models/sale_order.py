# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_uom_qty")
    def onchange_product_uom_qty_set_qty(self):
        for line in self:
            if line.product_id.min_qty:
                if line.product_uom_qty < line.product_id.min_qty:
                    raise ValidationError(
                        _("Minimum Order Quantity for '%s' is %s.")
                        % (self.product_id.display_name, self.product_id.min_qty)
                    )

    @api.constrains("product_uom_qty")
    def _check_sale_product_min_qty(self):
        invalid_products = [
            (line.product_id.display_name, line.product_id.min_qty)
            for line in self
            if line.product_id.min_qty
            and line.product_id.min_qty > line.product_uom_qty
        ]

        if invalid_products:
            invalid_product_str = ", ".join(
                [
                    "'%s' (Min Qty: %s)" % (product_name, min_qty)
                    for product_name, min_qty in invalid_products
                ]
            )
            raise ValidationError(
                _("Minimum Order Quantity for the following products is : %s")
                % invalid_product_str
            )
