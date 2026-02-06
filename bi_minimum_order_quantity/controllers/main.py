# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class searchProductQty(http.Controller):
    @http.route("/website/get_product_min_qty", type="json", auth="public")
    def search_product_min_qty(self, product_id, optional):
        if optional:
            product_id = request.env["product.template"].sudo().browse(int(product_id))
        else:
            product_id = request.env["product.product"].sudo().browse(int(product_id))
        product = {}
        if product_id:
            for rec in product_id:
                product = {
                    "min_qty": rec.min_qty,
                }
        return product

    @http.route(
        "/bi_minimum_order_quantity/get_combination_info", type="json", auth="public"
    )
    def get_combination_info_website(self, product_id):
        product_id = request.env["product.product"].browse(product_id)
        return product_id.min_qty

    @http.route("/get_prod", type="json", auth="public")
    def get_product(self, product_id):
        product_id = request.env["product.product"].browse(product_id)
        return product_id.min_qty
