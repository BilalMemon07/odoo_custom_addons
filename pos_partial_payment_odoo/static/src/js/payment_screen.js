/** @odoo-module **/

import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { _t } from "@web/core/l10n/translation";
import { useRef } from "@odoo/owl";

// Patch the PaymentScreen class for partial payment functionality
patch(PaymentScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.partialPaymentRef = useRef('PartialPayment');
        this.partialPaymentButtonRef = useRef('PartialPaymentButton');
    },

    /**
     * Partial Payment Button Functionality
     * Toggles partial payment mode for the current order
     */
    PartialPaymentButton() {
        // Check if partner is selected
        if (!this.currentOrder.get_partner()) {
            this.dialog.add(AlertDialog, {
                title: _t("No partner selected"),
                body: _t("Please select partner."),
            });
            return false;
        }

        console.log(this.partialPaymentRef.el, "this.partialPaymentRef.el");
        console.log(this.partialPaymentButtonRef.el, "this.partialPaymentButtonRef.el");

        // Toggle partial payment state
        if (this.currentOrder.partial_payment === true) {
            this.currentOrder.partial_payment = false;
            const validateElement = this.partialPaymentRef.el || this.partialPaymentButtonRef.el;
            if (validateElement) {
                validateElement.classList.add('disabled');
            }
        } else if (this.currentOrder.get_partner()) {
            this.currentOrder.partial_payment = true;
            const validateElement = this.partialPaymentRef.el || this.partialPaymentButtonRef.el;
            if (validateElement) {
                validateElement.classList.remove('disabled');
            }
        }
    },

    /**
     * Override validateOrder to handle partial payment validation
     * @param {boolean} isForceValidate - Whether to force validation
     */
    async validateOrder(isForceValidate) {
        // If not partial payment, use normal validation
        if (!this.currentOrder.partial_payment) {
            return await super.validateOrder(isForceValidate);
        }

        // Partial payment validation logic
        const partner = this.currentOrder.get_partner();
        
        // Check if partner allows partial payments
        if (partner && partner.prevent_partial_payment) {
            this.dialog.add(AlertDialog, {
                title: _t("Partial Payment Not Allowed"),
                body: _t("The Customer is not allowed to make Partial Payments."),
            });
            return false;
        }

        // Check if invoice is selected
        if (!this.currentOrder.to_invoice) {
            this.dialog.add(AlertDialog, {
                title: _t("Cannot Validate This Order"),
                body: _t("You need to Set Invoice for Validating Partial Payments."),
            });
            return false;
        }

        // debugger;

        // Check if amount is fully paid
        if (!this.currentOrder.get_due()) {
            this.dialog.add(AlertDialog, {
                title: _t("Cannot Validate This Order"),
                body: _t("The Amount is Fully Paid. Disable Partial Payment to Validate this Order."),
            });
            return false;
        }

        // Set partial payment flag and validate
        this.currentOrder.is_partial_payment = true;
        await this._isOrderValid(isForceValidate);
        await this._finalizeValidation();
        
    }
});