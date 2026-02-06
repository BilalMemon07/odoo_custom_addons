# Part of Softhealer Technologies.

{
    "name": "Partner Address Autofill",
    "author": "Arne De Geeter",
    "website": "https://arne.odoo.com",
    "support": "support@softhealer.com",
    "category": "Extra Tools",
    "license": "OPL-1",
    "summary": "AutoFill Of Address Google Places ",
    "version": "18.0.0.0.03",
    "depends": ["contacts"],
    "application": True,
    "data": [
        "views/partner_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_company_views.xml",
    ],
    "assets": {
        "web.assets_backend": {
            "sh_contact_address_google_place/static/src/xml/google_place_widget.xml",
            "sh_contact_address_google_place/static/src/js/sh_address_auto_complete.js",
        }
    },
    "auto_install": False,
    "installable": True,
    "images": [
        "static/description/background.png",
    ],
}
