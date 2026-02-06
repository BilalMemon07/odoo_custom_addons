/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { TextInputPopup } from "@ideabox_salonplus_commission/app/custom_popup/text_input_popup";

// ✅ 1. Handle Popup & Store Value on Order
patch(ControlButtons.prototype, {
    async onClickPopupSingleFieldCommission() {
        const collectInputs = async (title) => {
            return new Promise((resolve) => {
                this.dialog.add(TextInputPopup, {
                    title: _t(title),
                    getPayload: async (inputs) => {
                        const { service_type } = inputs;
                        resolve({ service_type });
                    },
                });
            });
        };
        const { service_type } = await collectInputs("Service type");

        if (!service_type) return;

        // save on current order
        const order = this.pos.get_order();
        order.service_type = service_type;
    },
});

// ✅ 2. Prevent Payment if Not Set
patch(PosStore.prototype, {
    async pay() {
        const currentOrder = this.get_order();
        if (!currentOrder.service_type) {
            this.dialog.add(AlertDialog, {
                title: _t("Missing Service Type"),
                body: _t("Please select a service type before proceeding to payment."),
            });
        }
                else{
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
    }})