from odoo import api, fields, models


class HrEmployeePublic(models.Model):
    """Add field into hr employee"""
    _inherit = 'hr.employee.public'

    limited_discount_percentage = fields.Integer(string="Global Discount Limit percentage",
                                      help="Provide discount limit to each "
                                           "employee",
                                      related="employee_id.limited_discount_percentage")
    limited_discount_amount = fields.Integer(string="Global Discount Limit percentage",
                                      help="Provide discount limit to each "
                                           "employee",
                                      related="employee_id.limited_discount_amount")