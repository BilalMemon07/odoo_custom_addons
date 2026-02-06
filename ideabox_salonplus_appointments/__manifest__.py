# -*- coding: utf-8 -*-
{
    "name": "Salon Plus - Appointment Management",
    "version": "0.1",
    "category": "Customization",
    "summary": "Enhanced Appointment Scheduling for Salon Plus",
    "description": """
Salon Plus Appointment Management
=================================

This module customizes and extends Odoo's Appointment module 
to support Salon Plus operations with improved appointment handling, 
resource allocation, and Point of Sale integration.
    """,

    # Author Information
    "author": "Ideabox Pvt. Ltd.",
    "website": "https://www.ideabox.technology",
    "license": "LGPL-3",

    # Dependencies
    "depends": [
        "base",
        "hr",
        "hr_holidays",
        "resource",
        "product",
        "appointment",
        "point_of_sale",
        "web",
        "ideabox_salonplus_contacts"
    ],

    # Data Files
    "data": [
        "security/ir.model.access.csv",
        "views/appointment_appointment_views.xml",
        "views/resource_services_views.xml",
        "views/pos_order_views.xml",
        "views/product_template.xml",
        "data/data.xml",
    ],

    # Assets for POS Extension
    "assets": {
        "point_of_sale._assets_pos": [
            "ideabox_salonplus_appointments/static/src/app/appointment_button/appointment_button.js",
            "ideabox_salonplus_appointments/static/src/app/appointment_button/appointment_button.xml",
            "ideabox_salonplus_appointments/static/src/app/resources_button/resources_button.js",
            "ideabox_salonplus_appointments/static/src/app/resources_button/resources_button.xml",
            "ideabox_salonplus_appointments/static/src/app/order_lines/order_line.js",
            "ideabox_salonplus_appointments/static/src/app/order_lines/order_line.xml",
            "ideabox_salonplus_appointments/static/src/app/pos_order_line.js",
            "ideabox_salonplus_appointments/static/src/app/pos_order.js",
            "ideabox_salonplus_appointments/static/src/app/pos_store.js",
        ],
    },

    # Installation
    "application": True,
    "installable": True,
}
