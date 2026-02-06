# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re
from datetime import datetime, timedelta

def generate_time_slots():
    slots = []
    for hour in range(0, 24):  # 0 to 23 hours
        for minute in range(0, 60, 15):  # 15-minute intervals
            # 24-hour format for internal value
            time_str = f"{hour:02d}:{minute:02d}"

            # Convert to 12-hour format with AM/PM for display
            display_hour = hour % 12 or 12
            am_pm = "AM" if hour < 12 else "PM"
            display = f"{display_hour:02d}:{minute:02d} {am_pm}"

            slots.append((time_str, display))
    return slots


class ResourceAndServices(models.Model):
    _name = "resource.services"
    _description = "Resource and Services"
    
    _inherit = ['mail.thread', 'mail.activity.mixin']
    


    name = fields.Char(string="Description", readonly=True)
    resource_id = fields.Many2one(
        'hr.employee',
        string="Resource",
        ondelete='cascade',
        index=True,
        required=True,
        tracking=1,
    )
    product_id = fields.Many2one(
        'product.product',
        string="Service",
        ondelete='cascade',
        index=True,
        required=True,
        tracking=1,
        domain=[('available_in_pos', '=', True)]
    )
    date_from = fields.Datetime(string="Date From", readonly=True, tracking=1,compute='_compute_datetimes',store=True)
    date_to = fields.Datetime(string="Date To", readonly=True, tracking=1,compute='_compute_datetimes',store=True)
    time_from = fields.Selection(
        selection=generate_time_slots(),
        string="Time From",
        required=True,
        tracking=1
    )
    time_to = fields.Selection(
        selection=generate_time_slots(),
        string="Time To",
        required=True,
        tracking=1
    )
    duration = fields.Char(
        string="Duration",
        readonly=True,
        compute='_compute_duration'
    )
    appointment_id = fields.Many2one(
        'appointment.appointment',
        string="Appointment",
        ondelete='cascade',
        index=True,
        tracking=1,
    )
    notes = fields.Text(string="Notes", tracking=1)
    partner_id = fields.Many2one(
        'res.partner',
        related="appointment_id.partner_id",
        string="Customer",
        ondelete='cascade',
        index=True,
        tracking=1
    )
    service_duration = fields.Char(
        string="Service Duration",
        readonly=True,
        compute="_compute_service_duration"
    )
    
    @api.depends('product_id','product_id.duration')
    def _compute_service_duration(self):
        for record in self:
            if record.product_id and record.product_id.duration:
                hours = int(record.product_id.duration)
                minutes = int((record.product_id.duration - hours) * 60)
                record.service_duration = f"{hours}h {minutes}m"
            else:
                record.service_duration = "0h 0m"
    
    

    @api.depends('time_from', 'time_to', 'appointment_id.date')
    def _compute_datetimes(self):
        for line in self:
            if line.appointment_id.date and line.time_from:
                # Combine date + time_from
                hour, minute = map(int, line.time_from.split(':'))
                dt_from = datetime.combine(line.appointment_id.date, datetime.min.time()).replace(
                    hour=hour, minute=minute
                )
                line.date_from = dt_from
            else:
                line.date_from = False

            if line.appointment_id.date and line.time_to:
                # Combine date + time_to
                hour, minute = map(int, line.time_to.split(':'))
                dt_to = datetime.combine(line.appointment_id.date, datetime.min.time()).replace(
                    hour=hour, minute=minute
                )
                line.date_to = dt_to
            else:
                line.date_to = False


    @api.depends('date_from', 'date_to','time_from','time_to')
    def _compute_duration(self):
        for record in self:
            if record.date_from and record.date_to:
                duration = record.date_to - record.date_from
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                record.duration = f"{int(hours)}h {int(minutes)}m"
                record.name = f"{record.resource_id.name} - {record.product_id.name}"
            else:
                record.duration = "0h 0m"
                
    

    @api.constrains('date_from', 'date_to', 'resource_id')
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
                        _("The resource '%s' is already booked to another appointment during this time.")
                        % record.resource_id.name
                    )
    @api.constrains('date_from','date_to','resource_id')
    def _check_resource_availability(self):
        for record in self:
            # Check if the resource has any time off during the specified period
            leave_domain = [
                ('employee_id', '=', record.resource_id.id),
                ('state', '=', 'validate'),
                ('date_from', '<', record.date_to),
                ('date_to', '>', record.date_from),
            ]
            leave_overlap = self.env['hr.leave'].search_count(leave_domain)
            if leave_overlap:
                raise ValidationError(
                    _("The resource '%s' is on leave during this time.") % record.resource_id.name
                )
                
    @api.constrains('date_from','date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from and record.date_from < fields.Datetime.now():
                raise ValidationError(
                    _("The Appointment date cannot be in the past.")
                )
                
    @api.constrains('date_from','date_to')
    def _check_date_overlap(self):
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from.date() != record.date_to.date():
                    raise ValidationError(
                        _("The Start and End time must be on the same day.")
                    )
    
    @api.constrains('date_from', 'date_to')
    def _check_dates_repetation(self):
        for record in self:
            if record.date_from and record.date_to:
                if record.date_from >= record.date_to:
                    raise ValidationError("End date must be after start date.")
                # if record.appointment_id:
                #     siblings = record.appointment_id.resource_line_ids.filtered(lambda l: l.id != record.id)
                #     for line in siblings:
                #         if line.date_to > record.date_from and line.date_from < record.date_to:
                #             raise ValidationError(
                #                 _("The time slots for services in the same appointment must not overlap.")
                #             )
    @api.constrains('product_id','time_from','time_to','duration', 'service_duration')
    def _check_duration(self):
        for rec in self:
            if rec.duration and rec.service_duration:
                duration_min = rec._to_minutes(rec.duration)
                service_duration_min = rec._to_minutes(rec.service_duration)

                if duration_min < service_duration_min:
                    raise ValidationError(
                        "The service %s requires at least %s, it can not be lesser than that." % (rec.product_id.name, rec.service_duration)
                    )

    def _to_minutes(self, text):
        hours = 0
        minutes = 0
        match = re.findall(r'(\d+)\s*h', text)
        if match:
            hours = int(match[0])
        match = re.findall(r'(\d+)\s*m', text)
        if match:
            minutes = int(match[0])
        return hours * 60 + minutes