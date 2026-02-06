/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup();
        this.pos=usePos();
        this.orm = useService("orm");
    },
    
   print_multi_receipt() {
        let self = this;
        let order = this.pos.get_order();
        let orderlines = this.pos.get_order().get_orderlines();              
        this.pos.showScreen('MultiReceiptScreen',{});
    
    },
});