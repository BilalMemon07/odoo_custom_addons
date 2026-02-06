from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class CommissionDisbursement(models.TransientModel):
    _name = 'commission.disbursement'
    _description = 'Commission Disbursement'

    employee_id = fields.Many2one('hr.employee', string='Resources', required=True)
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    remaining_amount = fields.Float(string='Remaining Amount', readonly=True)
    amount_paid = fields.Float(string='Amount Paid', readonly=True)
    amount_total = fields.Float(string='Amount')
    
    @api.onchange('employee_id','date_from','date_to')
    def _onchange_employee_id(self):
        for rec in self:
            if rec.employee_id and rec.date_from and rec.date_to:
                entries = self.env['account.move'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('move_type', '=', 'entry'),
                    ('state', '=', 'posted'),
                    ('date', '>=', rec.date_from),
                    ('date', '<=', rec.date_to)
                ])
                paid_amount = sum(entries.mapped('amount_total'))
                comms = self.env['resource.commission'].search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('date', '>=', rec.date_from),
                    ('date', '<=', rec.date_to)
                ])
                amount_total = sum(comms.mapped('amount'))
                remaining = amount_total - paid_amount
                rec.remaining_amount = remaining
                rec.amount_paid = paid_amount
            else:
                rec.remaining_amount = 0.0
                rec.amount_paid = 0.0

    def confirm(self):
        self.ensure_one()
        if self.employee_id and self.date_from and self.date_to:
            entries = self.env['account.move'].search([
                ('employee_id', '=', self.employee_id.id),
                ('move_type', '=', 'entry'),
                ('state', '=', 'posted'),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to)
            ])
            paid_amount = sum(entries.mapped('amount_total'))
            comms = self.env['resource.commission'].search([
                ('employee_id', '=', self.employee_id.id),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to)
            ])
            amount_total = sum(comms.mapped('amount'))
            remaining = amount_total - paid_amount
            total_amount = self.amount_total
            
            self.remaining_amount = remaining
            self.amount_paid = paid_amount
            
            journal = self.env['account.journal'].search([('code', '=', 'MISC')], limit=1)
            payable_account = self.env['account.account'].search([('code', '=', '211000')], limit=1)
            commission_account = self.env['account.account'].search([('code', '=', '652000')], limit=1)
            move_vals = {
                'journal_id': journal.id,
                'date': fields.Date.context_today(self),
                'ref': 'Commission Payment for ' + self.employee_id.name,
                'company_id': self.env.company.id,
                'employee_id': self.employee_id.id,
                'move_type': 'entry',
                'line_ids': [
                    (0, 0, {
                        'name': 'Debit: Commission Expense',
                        'account_id': commission_account.id,
                        'debit': total_amount,
                        'credit': 0.0,
                        'partner_id': False,
                    }),
                    (0, 0, {
                        'name': 'Credit: Commission Payable',
                        'account_id': payable_account.id,
                        'debit': 0.0,
                        'credit': total_amount,
                        'partner_id': False,
                    }),
                ],
            }
            move = self.env['account.move'].create(move_vals)
        
        if not self.employee_id:
            raise UserError("Please select a resource.")
        if self.amount_total <= 0:
            raise UserError("Total amount must be greater than zero.")
        if self.amount_total > self.remaining_amount:
            raise UserError("Amount exceeds remaining commission.")
        return {'type': 'ir.actions.act_window_close'}

    def close(self):
        return {'type': 'ir.actions.act_window_close'}
    