from odoo import _, api, fields, models


class ResourceScheduleReportWizard(models.TransientModel):
    _name = 'resource.schedule.report'
    _description = 'Resource Schedule Report'

    employee_ids = fields.Many2many('hr.employee', string="Employee")
    def print_report(self):
    
        data = {
            'employee_ids': self.employee_ids.ids if self.employee_ids else self.env['hr.employee'].search([]).ids,
        }

        return self.env.ref('resource_schedule_report.resource_schedule_report_pdf').with_context(landscape=False).report_action(self, data=data)

