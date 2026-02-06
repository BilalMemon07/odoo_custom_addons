/** @odoo-module **/
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    async pay() {
        const currentOrder = this.get_order();
        const currentPartner = currentOrder.get_partner();
        if (!currentPartner){
            this.dialog.add(AlertDialog, {
                title: _t("Customer Not Found"),
                body: _t("Please Select Customer"),
            });
        }else{
            if (!currentOrder.canPay()) {
                return;
            }
    
            if (
                currentOrder.lines.some(
                    (line) => line.get_product().tracking !== "none" && !line.has_valid_product_lot()
                ) &&
                (this.pickingType.use_create_lots || this.pickingType.use_existing_lots)
            ) {
                const confirmed = await ask(this.env.services.dialog, {
                    title: _t("Some Serial/Lot Numbers are missing"),
                    body: _t(
                        "You are trying to sell products with serial/lot numbers, but some of them are not set.\nWould you like to proceed anyway?"
                    ),
                });
                if (confirmed) {
                    this.mobile_pane = "right";
                    this.env.services.pos.showScreen("PaymentScreen", {
                        orderUuid: this.selectedOrderUuid,
                    });
                }
            } else {
                this.mobile_pane = "right";
                this.env.services.pos.showScreen("PaymentScreen", {
                    orderUuid: this.selectedOrderUuid,
                });
            }
        }
    }
})



    