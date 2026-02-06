# Part of Softhealer Technologies.

import json
import logging

import requests

from odoo import http
from odoo.http import request
from odoo.osv.expression import AND

GOOGLE_MAP_PLACES = "https://maps.googleapis.com/maps/api/place"
GOOGLE_MAP_PLACES_2 = "https://places.googleapis.com/v1/places:autocomplete"
GOOGLE_MAP_DETAILS = "https://places.googleapis.com/v1/places"
_logger = logging.getLogger(__name__)


class CustomController(http.Controller):
    def get_google_fields_mapping(self):

        return {
            "country": ["country"],
            "street_number": ["number"],
            "administrative_area_level_3": ["city"],
            "neighborhood": [""],
            "locality": ["city"],
            "route": ["street"],
            "sublocality_level_1": ["street2"],
            "postal_code": ["zip"],
            "administrative_area_level_1": ["state", "city"],
            "administrative_area_level_2": ["state", "country"],
        }

    def _convert_to_standard_address(self, g_fields):

        address_vals = {}
        google_fields_mapping = self.get_google_fields_mapping()
        for g_field in g_fields:
            fields_standard = (
                google_fields_mapping[g_field["type"]]
                if g_field["type"] in google_fields_mapping
                else []
            )

            for s_field in fields_standard:
                if s_field in address_vals:
                    continue
                if s_field == "country":
                    country = request.env["res.country"].search(
                        [("code", "=", g_field["shortText"].upper())], limit=1
                    )
                    address_vals[s_field] = country.id if country else False
                    address_vals["country_code"] = country.code if country else False
                elif s_field == "state":
                    domain = [("code", "=", g_field["shortText"].upper())]
                    if address_vals["country"]:
                        domain = AND(
                            [domain, [("country_id.id", "=", address_vals["country"])]]
                        )
                    state = request.env["res.country.state"].search(domain)
                    if len(state) == 1:
                        address_vals[s_field] = state.id
                else:
                    address_vals[s_field] = g_field["longText"]
        return address_vals

    @http.route(
        "/sh_contact_address_google_place/partial_address",
        type="json",
        auth="public",
        website=True,
    )
    def sh_get_partial_address(self, partial_address):

        company = request.env.user.company_id or request.env.company

        country_code_list = company.sh_restricted_country_ids.mapped("code")
        if country_code_list:
            result = ["country:" + str(item) + "|" for item in country_code_list]
            ["".join(result)]

        if (
            company
            and company.sh_is_enable_google_api_key
            and company.sh_google_api_key
        ):
            body = {
                "input": partial_address,
                "locationBias": {
                    "circle": {
                        "center": {
                            "latitude": company.partner_id.partner_latitude,
                            "longitude": company.partner_id.partner_longitude,
                        },
                        "radius": 10000,
                    }
                },
            }
            headers = {
                "Content-Type": "application/json",
                "X-Goog-FieldMask": "*",
                "X-Goog-Api-Key": company.sh_google_api_key,
            }

            try:
                results = requests.post(
                    f"{GOOGLE_MAP_PLACES_2}",
                    data=json.dumps(body),
                    headers=headers,
                    timeout=2.5,
                ).json()

            except (TimeoutError, ValueError):
                return []
            results = results.get("suggestions", [])
            list_result = [
                {
                    "description": result["placePrediction"]["text"]["text"],
                    "place_id": result["placePrediction"]["placeId"],
                }
                for result in results
            ]
            return list_result

        return []

    @http.route(
        "/sh_contact_address_google_place/fill_address",
        type="json",
        auth="public",
        website=True,
    )
    def sh_fill_address(self, address, place_id):
        company = request.env.user.company_id or request.env.company
        is_display_street_reverse = company.sh_is_display_street_reverable

        if (
            address
            and company
            and company.sh_is_enable_google_api_key
            and company.sh_google_api_key
        ):
            headers = {
                "X-Goog-Api-Key": company.sh_google_api_key,
                "X-Goog-FieldMask": "addressComponents",
            }

            try:
                results = requests.get(
                    f"{GOOGLE_MAP_DETAILS}/{place_id}", headers=headers, timeout=2.5
                ).json()
                results = results["addressComponents"]

                for res in results:
                    res["type"] = res.pop("types")[0]

            except (TimeoutError, ValueError):
                return {}

            sequence = list(self.get_google_fields_mapping().keys())
            results.sort(
                key=lambda result: sequence.index(result["type"])
                if result["type"] in sequence
                else 143
            )
            complete_address = self._convert_to_standard_address(results)

            # To avoid missing any type of user-inputted number
            if "number" not in complete_address:
                house_number = (
                    address.replace(complete_address.get("zip", ""), "")
                    .replace(complete_address.get("street", ""), "")
                    .replace(complete_address.get("city", ""), "")
                    .replace("-", "")
                )
                complete_address["number"] = house_number.split(",")[0].strip()
                complete_address[
                    "formatted_street"
                ] = f'{complete_address.get("street", "")} {complete_address["number"]}'
            else:
                if is_display_street_reverse:
                    street = (
                        f'{complete_address["number"]}'
                        f' {complete_address.get("street", "")}'
                    )
                else:
                    street = (
                        f'{complete_address.get("street", "")}'
                        f' {complete_address["number"]}'
                    )
                complete_address["formatted_street"] = street
            return complete_address if complete_address else {}
        return {}
