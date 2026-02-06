/** @odoo-module */
// Muhammad Bilal
import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";

patch(PosOrderline.prototype, {
    setup(_defaultObj) {
        super.setup(...arguments);
        this.rpc = rpc;
    },

    async get_resources() {
        if (typeof (this.id) != 'string' && this.resource_id) {
            await rpc("/get_pos_resource", {
                resource_id: this.resource_id,
                pos_order_line_id: this.id,
            });
        }
    },
    getDisplayData() {
        this.get_resources();
        return {
            ...super.getDisplayData(),
            resource_name: this.resource_name || '',
        };
    },
})