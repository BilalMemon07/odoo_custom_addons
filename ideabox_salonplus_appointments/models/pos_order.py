# -*- coding: utf-8 -*-
# Muhammad Bilal
from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = "pos.order"

    appointment_ids = fields.One2many(
        'appointment.appointment', 
        'pos_order_id', 
        string='Appointments'
    )
    appointment_count = fields.Integer(
        string='Appointments Count',
        compute='_compute_appointment_ids'
    )

    @api.depends('appointment_ids')
    def _compute_appointment_ids(self):
        for order in self:
            order.appointment_count = len(order.appointment_ids)
            
    # Action to open appointments from smart button
    def action_view_appointments(self):
        self.ensure_one()
        return {
            'name': 'Appointments',
            'type': 'ir.actions.act_window',
            'res_model': 'appointment.appointment',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.appointment_ids.ids)],
            'context': dict(self.env.context),
        }
    
    
class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    resource_id = fields.Many2one('hr.employee', string="Resource")
    resource_name = fields.Char(string="Resource")

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['resource_id','resource_name']
        return params