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

    async get_resourses(){
      if (typeof this.id !='string'){
        if (this.resource_id){
                await rpc("/get_pos_resourse", {
                    resource_id : this.resource_id,
                    pos_order_line_id : this.id
                });
            }
        }
    },

    getDisplayData() {
        this.get_resourses()
        return {
            ...super.getDisplayData(),
            resource_name : this.resource_name,
        };
    },
})