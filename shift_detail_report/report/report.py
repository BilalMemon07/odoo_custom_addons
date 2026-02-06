from datetime import timedelta,datetime
from odoo.exceptions import UserError, AccessError
from odoo import _, api, fields, models


class ShiftDetailReport(models.AbstractModel):
    _name = "report.shift_detail_report.shift_detail_reports"
    _description = "Shift Details Report"

    def _get_report_values(self, docids, data=None):
        result = []
        date_from = fields.Date.from_string(data.get("date_from"))
        date_to = fields.Date.from_string(data.get("date_to"))

        for emp in data.get("employee_ids"):
            current_date = date_from
            employee = self.env['hr.employee'].browse(emp)
            while current_date <= date_to:
                attendance = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', datetime.combine(current_date, datetime.min.time())),
                    ('check_in', '<', datetime.combine(current_date + timedelta(days=1), datetime.min.time()))
                ])
                if attendance:
                    for record in attendance:
                        day = current_date.strftime('%A')
                        result.append({
                            'employee_name': employee.name,
                            'day': day,
                            'date': current_date,
                            'start_time': record.check_in,
                            'end_time': record.check_out,
                            'status': 'Present'
                        })
                else:
                    day = current_date.strftime('%A')
                    result.append({
                        'employee_name': employee.name,
                        'day': day,
                        'date': current_date,
                        'start_time': '-',
                        'end_time': '-  ',
                        'status': 'Absent'
                    })
                current_date += timedelta(days=1)

        others = {
            "date_from": data.get("date_from"),
            "date_to": data.get("date_to"),
            "payment_status": data.get("payment_status"),
        }
        # raise UserError(_("result...%s") % result)
        return {
            "others": others,
            "data": result,
        }
