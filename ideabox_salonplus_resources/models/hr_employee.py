# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    product_commission_applicable = fields.Boolean(string="Product Commission Applicable")
    services = fields.Many2many('product.product', string="Services")
    blood_group = fields.Selection([
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')], string="Blood Group")
    emergency_contact_relation = fields.Char(string="Relation")
    father_name = fields.Char(string="Father Name")

