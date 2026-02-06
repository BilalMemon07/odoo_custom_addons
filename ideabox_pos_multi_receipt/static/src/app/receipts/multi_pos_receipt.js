/** @odoo-module */

import { Component, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { ReceiptHeader } from "@point_of_sale/app/screens/receipt_screen/receipt/receipt_header/receipt_header";


export class MultiPosReceipt extends Component {
    static template = "ideabox_pos_multi_receipt.MultiPosReceipt";
    static components = { ReceiptHeader }
    
    setup() {
        super.setup();
        this.pos = usePos();
        this.order = this.pos.get_order();
        if (this.props.barcode){
            let barcode = this.props.barcode;

            this.order.set_barcode(barcode)
            var data = barcode
            onMounted(() => {
                if(this.order.get_screen_data().props.confirm_split_data){

                    JsBarcode("#barcode", data, {
                        lineColor: "#000000",
                        width: 1,
                        height: 50,
                        displayValue: true,
                        fontSize: 15,
                    });
                }
            });
        }
    }
    
    get products() {
        let prods = this.order.get_screen_data().props.orderlines;
        let products = [];
        $.each(prods, function(i, prd) {products.push(prd)});
        return products;
    }
    
}
// registry.category("pos_screens").add("MultiPosReceipt", MultiPosReceipt);   



