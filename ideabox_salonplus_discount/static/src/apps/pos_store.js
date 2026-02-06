/** @odoo-module */
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    
    async getEmployee(id) {
        const employee = await this.data.call("hr.employee", "get_employee_data", [
            [id],
            id,
        ]);
        return employee;
    },
})