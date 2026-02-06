from odoo import models, fields, api

class KarachiArea(models.Model):
    _name = 'karachi.area'
    _description = 'Areas in Karachi'
    
    name = fields.Char(string='Area Name', required=True)

class KarachiArea(models.Model):
    _name = 'karachi.area.block'
    _description = 'Areas Blocks in Karachi'
    
    name = fields.Char(string='Block Name', required=True)
    area_id = fields.Many2one('karachi.area', string='Area Name', required=True)