# -*- coding: utf-8 -*-
# Muhammad Bilal
from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError

class PosOrder(models.Model):
    _inherit = "pos.order"


    appointment_id = fields.Many2one('appointment.appointment',string="Appointment")
    
class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    resource_id = fields.Many2one('hr.employee', string="Resource")
    resourse_name = fields.Char(string="Resource")

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['resource_id','resourse_name']
        return params





