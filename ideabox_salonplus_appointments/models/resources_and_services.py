# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast
import calendar as cal
import random
import pytz
from datetime import datetime, timedelta, time
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from babel.dates import format_datetime, format_time
from werkzeug.urls import url_encode, url_join

from odoo import api, fields, models, _, Command
from odoo.exceptions import ValidationError,UserError
from odoo.osv import expression
from odoo.tools import float_compare, frozendict
from odoo.tools.misc import babel_locale_parse, get_lang
from odoo.addons.base.models.res_partner import _tz_get
from collections import defaultdict




class ResourceAndServices(models.Model):
    _name = "resource.and.service"
    _description = "Resource and Services"

    name = fields.Char(string="Description", readonly=True)
    resource_id = fields.Many2one('hr.employee', string="Resource", ondelete='cascade', index=True,required=True)
    product_id = fields.Many2one('product.product', string="Service", ondelete='cascade', index=True,required=True)
    date_from = fields.Datetime(string="Date From", required=True)
    date_to = fields.Datetime(string="Date To", required=True)
    duration = fields.Char(string="Duration", readonly=True,compute='_compute_duration')
    appointment_id = fields.Many2one('appointment.appointment', string="Appointment", ondelete='cascade', index=True)
    
    @api.depends('date_from','date_to')
    def _compute_duration(self):
        for record in self:
            if record.date_from and record.date_to:
                start = fields.Datetime.from_string(record.date_from)
                end = fields.Datetime.from_string(record.date_to)
                duration = end - start
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                record.duration = f"{int(hours)}h {int(minutes)}m"
                record.name = f"{record.resource_id.name} - {record.product_id.name}"
            else:
                record.duration = "0h 0m"
                
    @api.constrains('date_from','date_to','resource_id')
    def _check_resource_overlap(self):
        for record in self:
            if record.date_from and record.date_to and record.resource_id:
                domain = [
                    ('id', '!=', record.id),
                    ('resource_id', '=', record.resource_id.id),
                    ('date_from', '<', record.date_to),
                    ('date_to', '>', record.date_from),
                    ('appointment_id.state', '=', 'confirmed'),
                    
                ]
                overlap = self.search_count(domain)
                if overlap:
                    raise ValidationError(
                        _("The resource '%s' is already booked to another appointment during this time.") % record.resource_id.name
                    )

    