/** @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

patch(PosOrder.prototype, {
    async wait_for_push_order() {
        const result = super.wait_for_push_order(...arguments);
        if (this.id && this.appointment_ids?.length) {
            await rpc("/get_appointment", {
                order_id: this.id,
                appointment_ids: this.appointment_ids,
            });
        }

        return result;
    },
});
