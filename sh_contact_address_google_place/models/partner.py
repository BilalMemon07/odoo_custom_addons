# Part of Softhealer Technologies.

import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    sh_contact_google_location = fields.Char("Enter Location")

    sh_contact_place_text = fields.Char("Enter location", copy=False)
    sh_contact_place_text_main_string = fields.Char("Enter location ", copy=False)

    # @api.onchange("sh_contact_place_text_main_string")
    # def onchange_technical_google_text_main_string(self):
    #     _logger.info("in first onchange")
    #     if self.sh_contact_place_text_main_string:
    #         _logger.info(self.sh_contact_place_text_main_string)
    #         self.sh_contact_google_location = self.sh_contact_place_text_main_string
    #         _logger.info(self.sh_contact_google_location)

    @api.onchange("sh_contact_place_text")
    def onchange_technical_google_text(self):
        _logger.info("in second onchange")
        if self.sh_contact_place_text:
            google_place_dict = json.loads(self.sh_contact_place_text)
            if google_place_dict:
                self.zip = google_place_dict.get("zip", "")
                self.street = (
                    google_place_dict.get("formatted_street", "")
                    or f"{google_place_dict.get('number', '')}"
                    f" {google_place_dict.get('street', '')}"
                )
                self.country_code = google_place_dict.get("country_code", "")
                self.city = google_place_dict.get("city", "")
                self.country_id = google_place_dict.get("country", False)
                self.state_id = google_place_dict.get("state", False)
