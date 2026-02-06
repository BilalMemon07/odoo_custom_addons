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


class Appointment(models.Model):
    _name = "appointment.appointment"
    
    name = fields.Char(string="Appointment Reference", required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date_from = fields.Datetime(string="Start Date", required=True, index=True, default=fields.Date.context_today,)
    date_to = fields.Datetime(string="End Date", required=True, index=True,)
    partner_id = fields.Many2one('res.partner', string="Client", ondelete='cascade', index=True,required=True,store=True,)
    appointment_type_id = fields.Many2one('appointment.type', string="Appointment Type", ondelete='set null', index=True,)
    resource_line_ids = fields.One2many('resource.and.service', 'appointment_id', string="Resource and Services",)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string="Status", readonly=True, copy=False, index=True, default='draft', track_visibility='onchange')    
        
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('seq.app')
        res = super(Appointment, self).create(vals)
        # if vals.get('name', _('New')) == _('New'):
        return res 
    
    
    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                continue
            record.state = 'confirmed'
            resource_map = defaultdict(list)

            for line in record.resource_line_ids:
                resource_map[line.resource_id].append(line)

            for resource, lines in resource_map.items():
                lines = sorted(lines, key=lambda l: l.date_from)

                service_ids = [(4, l.product_id.id) for l in lines]
                date_from = lines[0].date_from

                date_to = lines[-1].date_to

                a = self.env['calendar.event'].create({
                    'name': resource.name,
                    'start': date_from,
                    'stop': date_to,
                    'allday': False,
                    'partner_id': record.partner_id.id,
                    'partner_ids': [(4, record.partner_id.id)],
                    'resource_id': resource.id,
                    'service_ids': service_ids,
                    'appointment_id': record.id,
                    'res_model': 'appointment.type',
                })
        return True
    
    def action_done(self):
        for record in self:
            if record.state != 'confirmed':
                continue
            record.state = 'done'
        return True
    
    def action_cancel(self):
        for record in self:
            if record.state == 'done':
                continue
            record.state = 'cancelled'
        return True
    
    def action_draft(self):
        for record in self:
            if record.state != 'cancelled':
                continue
            record.state = 'draft'
        return True
    

    # Muhammad Bilal add this function to get data from Appointment
    def get_appointment_data(self,rec_id):
        all_appointment = self.env['appointment.appointment'].search([('id','=', rec_id)])
        appointment  = {
            'partner_id': all_appointment.partner_id,
            'resource_line_ids' : [{
                'product_id':line.product_id.id,
                'price': line.product_id.list_price,
                'quantity': 1,
                'resource_id': line.resource_id.id,
                'resourse_name': line.resource_id.name,
            }for line in all_appointment.resource_line_ids]
        }
        return appointment