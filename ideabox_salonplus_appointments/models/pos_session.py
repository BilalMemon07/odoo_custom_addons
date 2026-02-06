from odoo import models


class PosSession(models.Model):
    """The class PosSession is used to inherit pos.session"""
    _inherit = 'pos.session'

    def _load_pos_data(self,data):
        """Load POS data and add `res_users` to the response dictionary.
        return: A dictionary containing the POS data.
        """
        res = super()._load_pos_data(data)
        res['hr_employeeList'] = self.env['hr.employee'].search_read(fields=['id','name'])
        return res