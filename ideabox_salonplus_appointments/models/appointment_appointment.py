# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import api, fields, models, _
from datetime import datetime, timedelta

class Appointment(models.Model):
    _name = "appointment.appointment"
    _description = "Appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string="Client",
        copy=False,
        readonly=True,
        index=True,
        tracking=1,
        compute='_compute_name',
        store=True,
    )
    @api.depends('partner_id','partner_id.phone')
    def _compute_name(self):
        for record in self:
            if record.partner_id:
                record.name = record.partner_id.name + ' - ' + str(record.partner_id.phone)
            else:
                record.name = 'New'
    appointment_ref = fields.Char(
        string="Appointment Reference",
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New'),
        tracking=1
    )
    last_services = fields.Char(
        string="Last Services",
        compute='_compute_last_services',
        store=True,
        readonly=True
    )
    @api.depends('partner_id')
    def _compute_last_services(self):
        for record in self:
            if record.partner_id:
                last_appointment = self.search([('partner_id', '=', record.partner_id.id),('id','!=',record.id)], order='date desc', limit=1)
                if last_appointment and last_appointment.services_str:
                    record.last_services = last_appointment.services_str
                else:
                    record.last_services = 'No previous appointments'
            else:
                record.last_services = 'No previous appointments'
    last_served_by = fields.Char(
        string="Last Served By",
        compute='_compute_last_served_by',
        store=True,
        readonly=True
    )
    @api.depends('partner_id')
    def _compute_last_served_by(self):
        for record in self:
            if record.partner_id:
                last_appointment = self.search([('partner_id', '=', record.partner_id.id),('id','!=',record.id)], order='date desc', limit=1)
                if last_appointment and last_appointment.resources_str:
                    record.last_served_by = last_appointment.resources_str
                else:
                    record.last_served_by = 'No previous appointments'
            else:
                record.last_served_by = 'No previous appointments'
                
    date = fields.Date(
        string="Appointment Date",
        required=True,
        index=True,
        tracking=1,
        default=fields.Date.context_today,
    )
    appointment_from = fields.Datetime(
        string="From",
        readonly=True,
        compute='_compute_appointment_time',
        store=True,
    )
    appointment_to = fields.Datetime(
        string="To",
        readonly=True,
        compute='_compute_appointment_time',
        store=True,)  
    appointment_duration = fields.Char(
        string="Duration",
        compute='_compute_appointment_time',
        store=True,
    )
    @api.depends('resource_line_ids.date_from', 'resource_line_ids.date_to')
    def _compute_appointment_time(self):
        for record in self:
            if record.resource_line_ids:
                record.appointment_from = min(record.resource_line_ids.mapped('date_from')) - timedelta(hours=5)
                record.appointment_to = max(record.resource_line_ids.mapped('date_to')) - timedelta(hours=5)
                from_str = fields.Datetime.to_string(record.appointment_from)
                to_str = fields.Datetime.to_string(record.appointment_to)
                from_str = fields.Datetime.context_timestamp(record, record.appointment_from).strftime("%H:%M")
                to_str = fields.Datetime.context_timestamp(record, record.appointment_to).strftime("%H:%M")
                record.appointment_duration = f"{from_str} - {to_str}" 
            else: 
                record.appointment_from = False
                record.appointment_to = False
                record.appointment_duration = False
    partner_id = fields.Many2one(
        'res.partner',
        string="Client",
        ondelete='cascade',
        index=True,
        required=True,
        tracking=1,
        store=True,
    )
    client_notes = fields.Text(related='partner_id.notes', string="Client Notes")
    existing_client = fields.Boolean(string="Existing Client ?", compute='_compute_existing_client', store=True)
    @api.depends('partner_id','partner_id.create_date')
    def _compute_existing_client(self):
        for record in self:
            if record.partner_id and record.partner_id.create_date.date() == fields.Date.today():
                record.existing_client = False
            else:
                record.existing_client = True
                
    services_str = fields.Char(
        string="Services",
        compute='_compute_services_string',
        store=True,
        tracking=1,)
    @api.depends('resource_line_ids.product_id')
    def _compute_services_string(self):
        for record in self:
            services = record.resource_line_ids.mapped('product_id.name')
            record.services_str = ', '.join(services) if services else ''
    resources_str = fields.Char(
        string="Resources",
        compute='_compute_resources_string',
        store=True,
        tracking=1,)
    @api.depends('resource_line_ids.resource_id')
    def _compute_resources_string(self):
        for record in self:
            resources = record.resource_line_ids.mapped('resource_id.name')
            record.resources_str = ', '.join(resources) if resources else ''
    appointment_type_id = fields.Many2one(
        'appointment.type',
        string="Appointment Type",
        ondelete='set null',
        index=True,
        tracking=1,
    )
    resource_line_ids = fields.One2many(
        'resource.services',
        'appointment_id',
        tracking=1,
        string="Resource and Services",
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show')
        ],
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        default='draft',
        track_visibility='onchange',
        tracking=1,
    )
    pos_order_id = fields.Many2one('pos.order', string='POS Order')
    @api.model
    def create(self, vals):
        vals['appointment_ref'] = self.env['ir.sequence'].next_by_code('seq.app')
        res = super(Appointment, self).create(vals)
        res['name'] = res.partner_id.name + ' - ' + str(res.partner_id.phone)
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
                self.env['calendar.event'].create({
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
    
    def action_no_show(self):
        for record in self:
            if record.state != 'confirmed':
                continue
            record.state = 'no_show'
        return True

    # Muhammad Bilal: added this function to get data from Appointment
    def get_appointment_data(self, rec_id):
        appointment_rec = self.env['appointment.appointment'].browse(rec_id)
        appointment = {
            'partner_id': appointment_rec.partner_id.id,
            'resource_line_ids': [
                {
                    'product_id': line.product_id.id,
                    'price': line.product_id.list_price,
                    'quantity': 1,
                    'resource_id': line.resource_id.id,
                    'resource_name': line.resource_id.name,
                }
                for line in appointment_rec.resource_line_ids
            ]
        }
        return appointment
