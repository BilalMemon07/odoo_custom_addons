from odoo.exceptions import UserError, AccessError
from odoo import _, api, fields, models


class TipReport(models.AbstractModel):
    _name = "report.ideabox_salonplus_tips.tip_reports"
    _description = "Tips Report"

    def _get_report_values(self, docids, data=None):

        employee_ids_str = ""
        if data["employee_ids"] != "[]":
            employee_ids_str = str(data["employee_ids"]).split("[")[-1].split("]")[0]
        query = f""" 
                select
                pos.date_order as order_date,
                pos.amount_total as order_amount,
                res.name as client_name,
                tip.amount as tip,
                pos.services_str as services,
                emp.name as employee_name
                
                from pos_tip tip
                left join hr_employee emp on emp.id = tip.employee_id
                left join pos_order pos on pos.id = tip.pos_order_id
                left join res_partner res on res.id = pos.partner_id
                where pos.date_order between '{data.get('date_from')}' and '{data.get('date_to')}'""" 

        if data["employee_ids"] != []:
            query += f"and emp.id in ({employee_ids_str})"
        query += "order by emp.id"

        cr = self._cr
        cr.execute(query)
        result = cr.dictfetchall()

        others = {
            "date_from": data.get("date_from"),
            "date_to": data.get("date_to"),
            'billing_amount': data.get("billing_amount"),
            'client_name': data.get("client_name"),
        }
        return {
            "others": others,
            "data": result,
        }
