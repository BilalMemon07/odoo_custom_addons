/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { TextInputPopup } from "@ideabox_salonplus_tips/app/custom_popup/text_input_popup";

patch(ControlButtons.prototype, {
    async onClickPopupSingleField() {
        const collectInputs = async (title) => {
            return new Promise((resolve) => {
                this.dialog.add(TextInputPopup, {
                    title: _t(title),
                        getPayload: async (inputs) => {
                            const { tip_amount, payment_method, employee_ids } = inputs;
                            resolve({ tip_amount, payment_method, employee_ids });
                        },
                });
            });
        };
        const tip_details = await collectInputs("Enter Tip Details");
        if (!tip_details) return;
    },
});
