/** @odoo-module */
// Muhammad Bilal
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async onClickAppointment(clickedOrderId) {
        const appointment_appointment = await this._getAppointment(clickedOrderId);
        for (let i = 0; i < appointment_appointment.resource_line_ids.length; ++i) {
            const line = appointment_appointment.resource_line_ids[i];
            const newLineValues = {
                    product_id: line.product_id,
                    qty: line.quantity,
                    price_unit: line.price,
                    price_type: "automatic",
                    order_id: this.get_order(),
                    resource_id : line.resource_id,
                    resourse_name : line.resourse_name,
                };
                await this.addLineToCurrentOrder(newLineValues, {}, false);
            }
    },
    async _getAppointment(id) {
        const appointment_appointment = await this.data.call("appointment.appointment", "get_appointment_data", [
            [id],
            id,
        ]);
        return appointment_appointment;
    },
})