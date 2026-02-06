/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { TextInputPopupCommission } from "@ideabox_salonplus_commission/app/custom_popup/commission_popup";

patch(ControlButtons.prototype, {
    async onClickPopupSingleFieldCommissions() {
        const collectInputs = async (title) => {
            return new Promise((resolve) => {
                this.dialog.add(TextInputPopupCommission, {
                    title: _t(title),
                        getPayload: async (inputs) => {
                            const { commission_amount, employee_ids } = inputs;
                            resolve({ commission_amount, employee_ids });
                        },
                });
            });
        };
        const commission_details = await collectInputs("Enter Commission Details");
        if (!commission_details) return;
    },
});
