from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    show_commission_config = fields.Boolean(
        string="Allow Commission (Global)",
        compute="_compute_show_commission_config"
    )

    @api.depends()
    def _compute_show_commission_config(self):
        allow_commission = self.env['ir.config_parameter'].sudo().get_param('ideabox_salonplus_commission.allow_commission', default=False)
        commission_type = self.env['ir.config_parameter'].sudo().get_param('ideabox_salonplus_commission.commission_type', default=False)
        for rec in self:
            if allow_commission:
                if allow_commission == 'False':
                    rec.show_commission_config = False
                else:
                    if commission_type == 'products':
                        rec.show_commission_config = True
                    else:
                        rec.show_commission_config = False
            else:
                rec.show_commission_config = False

    commission_applicable = fields.Boolean(string="Commission Applicable",store=True)
    commission_percentage = fields.Float(string="Commission Percentage",store=True)
    commission_fixed = fields.Float(string="Fixed Commission Amount",store=True)
    commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Commission Type", default='percentage', store=True)
    
    @api.constrains('commission_percentage')
    def _check_commission_percentage(self):
        for record in self:
            if record.commission_type == 'percentage':
                if record.commission_percentage < 0 or record.commission_percentage > 100:
                    raise ValidationError("Commission percentage must be between 0 and 100.")
    @api.constrains('commission_fixed')
    def _check_commission_fixed(self):
        for record in self:
            if record.commission_type == 'fixed':
                if record.commission_fixed < 0:
                    raise ValidationError("Fixed commission amount must be non-negative.")
                
    @api.onchange('commission_applicable')
    def empty_commission_type(self):
        if self.commission_applicable == False:
            self.commission_type = False
            self.commission_percentage = False
            self.commission_fixed = False
            
class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    commission_applicable = fields.Boolean(string="Commission Applicable", related='product_tmpl_id.commission_applicable', store=True)
    commission_percentage = fields.Float(string="Commission Percentage", related='product_tmpl_id.commission_percentage', store=True)
    commission_fixed = fields.Float(string="Fixed Commission Amount", related='product_tmpl_id.commission_fixed', store=True)
    commission_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount')
    ], string="Commission Type", related='product_tmpl_id.commission_type', store=True)