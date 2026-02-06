import { patch } from "@web/core/utils/patch";
import { AccountReportFilters } from "@account_reports/components/account_report/filters/filters";
import { _t } from "@web/core/l10n/translation";

patch(AccountReportFilters.prototype, {
    setup() {
        super.setup();
        
        // Ensure payment_date structure exists and matches Odoo's pattern
        this.controller.options.payment_date = this.controller.options.payment_date || {
            date_from: null,
            date_to: null,
            filter: 'custom',
            mode: 'range',
            string: _t("Payment Date")
        };
    },
    
    // Getters
    paymentDateFrom() {
        return this.controller.options.payment_date.date_from 
            ? luxon.DateTime.fromISO(this.controller.options.payment_date.date_from) 
            : null;
    },

    paymentDateTo() {
        return this.controller.options.payment_date.date_to 
            ? luxon.DateTime.fromISO(this.controller.options.payment_date.date_to) 
            : null;
    },

    // Setters
    setPaymentDate(type, date) {
        if (date) {
            this.controller.options.payment_date[`date_${type}`] = date;
            this.controller.options.payment_date.filter = 'custom';
            this.applyFilters('payment_date');
        }
    },

    setPaymentDateFrom(dateFrom) {
        this.setPaymentDate('from', dateFrom);
    },

    setPaymentDateTo(dateTo) {
        this.setPaymentDate('to', dateTo);
    },
});
