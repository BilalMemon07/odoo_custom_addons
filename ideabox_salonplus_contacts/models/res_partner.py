from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    company_type = fields.Selection(string='Company Type',
        selection=[('person', 'Customer'), ('company', 'Company')],
        compute='_compute_company_type', inverse='_write_company_type')
    birthdate = fields.Date(string='Birthdate')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Others')
    ], string='Gender')
    married = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Married', required=True, default='no')
    age_limit = fields.Selection(selection=[
        ('18_and_below', '18 and below'),
        ('18_35', '18 - 35'),
        ('35_50', '35 - 50'),
        ('50_above', '50+'),
    ], string='')
    area_id = fields.Many2one('karachi.area',string='Area')
    block = fields.Many2one('karachi.area.block', string='Block', domain=[('area_id', '=', area_id)])
    referred_by = fields.Many2one('res.partner', string='Referred By')
    notes = fields.Text(string='Notes')
    subscribe_to_alert = fields.Boolean(string='Subscribe to Alert')
    add_to_blacklist = fields.Boolean(string='Add to blacklist')
    walk_in = fields.Boolean(string='Walk-in')
    # Set default contact type to Individual
    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        res['company_type'] = 'person'
        return res