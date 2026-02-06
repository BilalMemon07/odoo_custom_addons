from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    commission_applicable = fields.Boolean(string="Commission Applicable")
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
                    if commission_type == 'resource':
                        rec.show_commission_config = True
                    else:
                        rec.show_commission_config = False
            else:
                rec.show_commission_config = False


    commission_ids = fields.One2many("commission.lines", "employee_id", string="Commissions")
