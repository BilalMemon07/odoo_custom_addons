/** @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
   setup(_defaultObj, options) {
        super.setup(...arguments);
        this.barcode = this.barcode || "";
        this.set_barcode();
        this.split_data = this.split_data || false;
        this.split_data_confirm = this.split_data_confirm || false;
    },
    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        this.barcode = json.barcode;
        this.split_data = json.split_data;
    },
    get_barcode(){
        return this.barcode 
    },
    set_barcode(){
        var self = this;
        var temp = Math.floor(100000000000+ Math.random() * 9000000000000)
        self.barcode =  temp.toString();
    },
    set_split_data_confirm(split_data_confirm){
        this.split_data_confirm = split_data_confirm;
    },
    get_split_data_confirm(){
        return this.split_data_confirm;
    },
    set_split_data(split_data){
        this.split_data = split_data;
    },
    get_split_data(){
        return this.split_data;
    },
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.barcode = this.barcode;
        json.split_data = this.split_data;
        json.split_data_confirm = this.split_data_confirm
        return json
    },
    export_for_printing(){
        const json = super.export_for_printing(...arguments);
        json.barcode = this.barcode;
        json.split_data = this.split_data;
        json.split_data_confirm = this.split_data_confirm;
        return json;
    },

});