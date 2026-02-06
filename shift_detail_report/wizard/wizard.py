from odoo import _, api, fields, models


class ShiftDetailReportWizard(models.TransientModel):
    _name = 'shift.detail.report'
    _description = 'Shift Details Report'
    
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    employee_ids = fields.Many2many('hr.employee', string="Employee")
    def print_report(self):
    
        data = {
            'date_from': self.from_date,
            'date_to': self.to_date,
            'employee_ids': self.employee_ids.ids if self.employee_ids else self.env['hr.employee'].search([]).ids,
        }

        return self.env.ref('shift_detail_report.shift_detail_report_pdf').with_context(landscape=False).report_action(self, data=data)

