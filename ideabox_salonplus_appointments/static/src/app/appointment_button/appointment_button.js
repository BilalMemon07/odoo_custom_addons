/** @odoo-module */
// Muhammad Bilal
import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";


patch(ControlButtons.prototype, {
    onClickAppointment() {
        const order = this.pos.get_order();
        const partner = order.get_partner();
        const searchDetails = partner ? [partner.id] : [];
        this.dialog.add(SelectCreateDialog, {
            resModel: "appointment.appointment",
            noCreate: true,
            multiSelect: false,
            domain: [
                ["partner_id", "in", searchDetails],
                ["state", "=", 'confirmed'],
            ],
            onSelected: async (resIds) => {
                await this.pos.onClickAppointment(resIds[0]);
            },
        });
    },
});
