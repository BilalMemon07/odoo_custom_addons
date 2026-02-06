# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sh_allow_multi_user = fields.Boolean(
        related="company_id.sh_allow_multi_user",
        string="Allow Multi User To Start Task",
        readonly=False,
    )

    sh_allow_without_description = fields.Boolean(
        related="company_id.sh_allow_without_description",
        string="Allow Default Description",
        readonly=False,
    )
