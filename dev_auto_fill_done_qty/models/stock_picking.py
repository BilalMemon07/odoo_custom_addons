from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_dev_fill_qty(self):
        for picking in self:
            for line in picking.move_ids_without_package:
                if line.availability:
                    line.quantity = line.availability
