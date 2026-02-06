from odoo import api, fields, models


class HrEmployee(models.Model):
    """Add field into hr employee"""
    _inherit = 'hr.employee'

    limited_discount_percentage = fields.Integer(string="Global Discount Limit Percentage",
                                      help="Provide discount limit to each "
                                           "employee")
    limited_discount_amount = fields.Integer(string="Global Discount Limit Amount",
                                      help="Provide discount limit to each "
                                           "employee")
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        """Loading fields"""
        result = super()._load_pos_data_fields(config_id)
        result.append('limited_discount_percentage')
        result.append('limited_discount_amount')
        result.append('parent_id')
        result.append('pin')
        return result

    def get_employee_data(self,rec_id):
        employee_record = self.env['hr.employee'].search([('id','=', rec_id)])
        return {
            'limited_discount_percentage':employee_record.limited_discount_percentage,
            'limited_discount_amount':employee_record.limited_discount_amount,
            'parent_id':employee_record.parent_id.id,
            'pin':employee_record.pin,
        }


