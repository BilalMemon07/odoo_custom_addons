/** @odoo-module **/
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

// Patch the PosOrder model for partial payment functionality
patch(PosOrder.prototype, {
    /**
     * Initialize the order with partial payment properties
     */
    setup(vals) {
        super.setup(vals);
        
        // Initialize partial payment properties
        this.partial_payment = vals.partial_payment || false;
        this.is_partial_payment = vals.is_partial_payment || false;
    },

    /**
     * Set order suggestion for partial payment
     * @param {boolean} is_partial_payment - Whether this is a partial payment
     */
    set_order_suggestion(is_partial_payment) {
        this.is_partial_payment = is_partial_payment;
    },

    /**
     * Override serialize method to include partial payment data
     * This replaces the old export_as_JSON method
     * @returns {Object} Serialized order data
     */
    serialize() {
        const data = super.serialize(...arguments);
        data.is_partial_payment = this.is_partial_payment;
        return data;
    },

    /**
     * Override update method to handle partial payment data
     * This handles data coming from the server (replaces init_from_JSON functionality)
     * @param {Object} vals - Data to update from
     */
    update(vals) {
        super.update(vals);
        
        if ('is_partial_payment' in vals) {
            this.is_partial_payment = vals.is_partial_payment;
        }
    },

    /**
     * Override export_for_printing to include partial payment info in receipts
     * @param {string} baseUrl - Base URL for the application
     * @param {Object} headerData - Header data for printing
     * @returns {Object} Data for printing
     */
    export_for_printing(baseUrl, headerData) {
        const printData = super.export_for_printing(baseUrl, headerData);
        
        // Add partial payment information to print data
        printData.is_partial_payment = this.is_partial_payment;
        printData.partial_payment_info = this.partial_payment ? "Partial Payment" : "";
        
        return printData;
    }
});