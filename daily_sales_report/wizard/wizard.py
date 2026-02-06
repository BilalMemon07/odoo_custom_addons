from odoo import _, api, fields, models


class DailySalesReportWizard(models.TransientModel):
    _name = 'daily.sales.report'
    _description = 'Daily Sales Report'
    
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    payment_status = fields.Selection([
        ('All', 'All'),
        ('Paid', 'Paid'),
        ('Partially Paid', 'Partially Paid'),
        ('Unpaid', 'Unpaid'),
    ], string='Payment Status', default='All')

    def print_report_word(self):
    
        data = {
            'date_from': self.from_date,
            'date_to': self.to_date,
            'payment_status': self.payment_status,
        }

        return self.env.ref('daily_sales_report.daily_sales_report_pdf').with_context(landscape=True).report_action(self, data=data)

