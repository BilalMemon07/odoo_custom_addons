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


class CalendarEvent(models.Model):
    _inherit = "calendar.event"
    
    service_ids = fields.Many2many('product.product', string="Services",readonly=True,store=True)    
    resource_id = fields.Many2one('hr.employee', string="Resource",readonly=True,store=True)
    appointment_id = fields.Many2one('appointment.appointment', string="Appointment", ondelete='cascade', index=True,readonly=True,store=True)
    