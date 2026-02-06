from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    allow_commission = fields.Boolean(string="Allow Commission", readonly=False, config_parameter='ideabox_salonplus_commission.allow_commission')
    commission_type = fields.Selection([('products','Products'),('resource','Resource')],string="Commission Type", readonly=False,config_parameter='ideabox_salonplus_commission.commission_type', default='products')
    