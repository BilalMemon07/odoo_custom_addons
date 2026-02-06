/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { useRef, useState, onWillStart, Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { MultiPosReceipt } from "@ideabox_pos_multi_receipt/app/receipts/multi_pos_receipt";
import { onMounted } from "@odoo/owl";


class MultiReceiptScreen extends ReceiptScreen {
    
    static template = "ideabox_pos_multi_receipt.MultiReceiptScreen";
    static components = { MultiPosReceipt };
    setup() {
        super.setup();
        this.pos=usePos();
        this.orm = useService("orm");
        this.printer = useService("printer");
        this.order = this.pos.get_order();
        if (this.props.barcode){
            let barcode = this.props.barcode;
            this.order.set_barcode(barcode)
            var data = barcode
            onMounted(() => {
                if(this.pos.get_order().get_screen_data().props.confirm_split_data){

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
    
    back() {
        this.pos.removeOrder(this.order);
        this.pos.add_new_order();
        this.pos.showScreen('ProductScreen');
    }
    
    async printReceipt() {
        const isPrinted = await this.printer.print(
            MultiPosReceipt,
            { 
                data: this.pos.get_order().export_for_printing(),
                order: this.pos.get_order(),
                receipt: this.pos.get_order().export_for_printing(),
                orderlines: this.pos.get_order().orderlines,
                paymentlines: this.pos.get_order().export_for_printing().paymentlines
            },
            { webPrintFallback: true }
        );
        
        const isPrinted2 = await this.printer.print(
            MultiPosReceipt,
            { 
                data: this.pos.get_order().export_for_printing(),
                order: this.pos.get_order(),
                receipt: this.pos.get_order().export_for_printing(),
                orderlines: this.pos.get_order().orderlines,
                paymentlines: this.pos.get_order().export_for_printing().paymentlines
            },
            { webPrintFallback: true }
        );
    }

    
}
registry.category("pos_screens").add("MultiReceiptScreen", MultiReceiptScreen);
