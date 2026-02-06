from odoo.exceptions import UserError, AccessError
from odoo import _, api, fields, models


class DailySalesReport(models.AbstractModel):
    _name = "report.daily_sales_report.daily_sales_reports"
    _description = "Daily Sales Report"

    def _get_report_values(self, docids, data=None):

        result = []
        
        orders = self.env['pos.order'].search([
            ('date_order', '>=', data.get('date_from')),
            ('date_order', '<=', data.get('date_to')),
        ])
        for order in orders:
            services_total = sum(line.price_subtotal for line in order.lines if line.product_id.type == 'service')
            product_total = sum(line.price_subtotal for line in order.lines if line.product_id.type == 'consu' and line.product_id.name != 'Discount')
            discount_total = sum(line.discount_amount for line in order.lines)
            discount_total += sum(line.price_subtotal for line in order.lines if line.product_id.name == 'Discount')
            taxes = sum(line.price_subtotal_incl - line.price_subtotal for line in order.lines)
            tips = sum(tip.amount for tip in order.tip_ids)
            paid_amount = sum(line.amount for line in order.payment_ids) 
            bill_amount = order.amount_total
            balance = bill_amount - paid_amount
            payment_status = ''
            if balance <= 0:
                payment_status = 'Paid'
            elif paid_amount > 0 and balance > 0:
                payment_status = 'Partially Paid'
            else:
                payment_status = 'Unpaid'
                
            if data.get('payment_status') != 'All' and payment_status != data.get('payment_status'):
                continue
            
            result.append({
                'order_no': order.name,
                'date_order': order.date_order,
                'partner_id': order.partner_id.name,
                'services_total': services_total,
                'product_total': product_total,
                'discount_total': discount_total,
                'taxes': taxes,
                'tips': tips,
                'bill_amount': bill_amount,
                'paid_amount': paid_amount,
                'balance': balance,
                'payment_status': payment_status,
            })
            
        others = {
            "date_from": data.get("date_from"),
            "date_to": data.get("date_to"),
            "payment_status": data.get("payment_status"),
        }
        return {
            "others": others,
            "data": result,
        }
