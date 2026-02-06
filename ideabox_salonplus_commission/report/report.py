from odoo.exceptions import UserError, AccessError
from odoo import _, api, fields, models


class CommissionReport(models.AbstractModel):
    _name = "report.ideabox_salonplus_commission.commission_reports"
    _description = "Commission Report"

    def _get_report_values(self, docids, data=None):

        employee_ids_str = ""
        if data["employee_ids"] != "[]":
            employee_ids_str = str(data["employee_ids"]).split("[")[-1].split("]")[0]
        query = f""" 
                select
                pos.name as order_no,
                pos.date_order as order_date,
                pos.amount_total as order_amount,
                com.amount as commission,
                pt.name as product_name,
                res.name as client_name,
                emp.name as employee_name
                
                from resource_commission com
                left join hr_employee emp on emp.id = com.employee_id
                left join pos_order pos on pos.id = com.pos_order_id
                left join product_product pp on pp.id = com.product_id
                left join res_partner res on res.id = pos.partner_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                where com.date between '{data.get('date_from')}' and '{data.get('date_to')}' and pt.name ->> 'en_US' != 'Discount' and pos.state != 'cancel'
                """

        if data["employee_ids"] != []:
            query += f"and emp.id in ({employee_ids_str})"
        query += "order by emp.id"

        cr = self._cr
        cr.execute(query)
        result = cr.dictfetchall()

        others = {
            "date_from": data.get("date_from"),
            "date_to": data.get("date_to"),
        }
        return {
            "others": others,
            "data": result,
        }
