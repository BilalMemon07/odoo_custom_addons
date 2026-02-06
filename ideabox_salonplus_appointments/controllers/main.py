# -*- coding: utf-8 -*-
# Muhammad Bilal
from odoo import http
from odoo.http import request


class PosResourceController(http.Controller):

    @http.route('/get_pos_resourse', type='json', auth='user', methods=['POST'])
    def get_pos_sales_person(self, resource_id, pos_order_line_id):
        if resource_id:
            request.env['pos.order.line'].sudo().browse(int(pos_order_line_id)).write({
                'resource_id': resource_id
            })
            return resource_id