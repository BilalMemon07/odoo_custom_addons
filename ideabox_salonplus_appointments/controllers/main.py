# -*- coding: utf-8 -*-
# Muhammad Bilal
from odoo import http
from odoo.http import request


class PosResourceController(http.Controller):

    @http.route('/get_pos_resource', type='json', auth='user', methods=['POST'])
    def get_pos_sales_person(self, resource_id, pos_order_line_id):
        if resource_id:
            request.env['pos.order.line'].sudo().browse(int(pos_order_line_id)).write({
                'resource_id': resource_id
            })
            return resource_id
        
        
    @http.route('/get_appointment', type='json', auth='user', methods=['POST'])
    def get_appointment(self, order_id=None, appointment_ids=None):
        order = request.env['pos.order'].browse(order_id)
        for appointment_id in appointment_ids:
                appointment = request.env['appointment.appointment'].browse(appointment_id)
                appointment.state = 'done'
        commands = [(4, app_id) for app_id in appointment_ids]
        order.write({'appointment_ids': commands})

        return True
    
