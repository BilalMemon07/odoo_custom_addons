/** @odoo-module **/
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { patch } from "@web/core/utils/patch";
import { makeAwaitable } from "@point_of_sale/app/store/make_awaitable_dialog";
import { useService } from "@web/core/utils/hooks";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";


patch(ControlButtons.prototype, {
    setup() {
        super.setup()
        this.orm = useService("orm");
    },
    
    async onClickResource() {
        const orderline = this.pos.get_order().get_selected_orderline();
        if (!orderline) {
            this.dialog.add(AlertDialog, {
                title: _t("No orderline selected."),
                body: _t("Select orderline to add Resouces"),
            });
            return;
        }
        this.hr_employee = await this.orm.call("hr.employee", "search_read", [[], ['id', 'name']]);
        const hr_employeeList = this.hr_employee.map((employee) => ({
            id: employee.id,
            item: employee,
            label: employee.name,
            isSelected: false,
        }));
        const confirmed = await makeAwaitable(this.dialog, SelectionPopup, {
            title: _t("Select the Resource"),
            list: hr_employeeList,

        });
        if (confirmed) {
            orderline.resource_name = confirmed.name;
            orderline.resource_id = confirmed.id;
        }
    }
});
