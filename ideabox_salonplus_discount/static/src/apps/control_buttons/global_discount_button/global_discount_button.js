/** @odoo-module */
// Muhammad Bilal
import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { SelectCreateDialog } from "@web/views/view_dialogs/select_create_dialog";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { GlobalDiscountPopup } from "@ideabox_salonplus_discount/apps/popups/global_discount_popup/global_discount_popup";
import { NumberPopup } from "@point_of_sale/app/utils/input_popups/number_popup";

patch(ControlButtons.prototype, {
    setup() {
        super.setup(...arguments);
    },
   
    async onClick() {
        const collectInputs = async (title) => {
            return new Promise((resolve) => {
                this.dialog.add(GlobalDiscountPopup, {
                    title: _t(title),
                    getPayload: async (inputs) => {
                        const { discount_type, discount_value } = inputs;
                        resolve({ discount_type, discount_value });
                    },
                });
            });
        };
        const discount_details = await collectInputs("Enter Discount Details");
        if (!discount_details) return;
        const { discount_type, discount_value } = discount_details;
        console.log("✅ Discount saved to order:", {
            discount_type,
            discount_value,
        });
        this.manager_discount_approval(discount_type,parseFloat(discount_value))
    },

    async apply_global_discount(discount_type, discount_value) {
        const order = this.pos.get_order();
        const lines = order.get_orderlines();
        const product = this.pos.config.discount_product_id;
        if (product === undefined) {
            this.dialog.add(AlertDialog, {
                title: _t("No discount product found"),
                body: _t(
                    "The discount product seems misconfigured. Make sure it is flagged as 'Can be Sold' and 'Available in Point of Sale'."
                ),
            });
            return;
        }
        // Remove existing discounts
        lines.filter((line) => line.get_product() === product).forEach((line) => line.delete());
        // Calculate discount percentage based on type
        let discount_percentage;
        if (discount_type === 'percentage') {
            discount_percentage = parseFloat(discount_value);
        } else if (discount_type === 'fixed') {
            // Convert fixed amount to percentage
            const total_amount = order.get_total_without_tax();
            discount_percentage = (parseFloat(discount_value) / total_amount) * 100;
        } else {
            console.error("Invalid discount type:", discount_type);
            return;
        }
        // Add one discount line per tax group
        const linesByTax = order.get_orderlines_grouped_by_tax_ids();
        for (const [tax_ids, lines] of Object.entries(linesByTax)) {
            // Note that tax_ids_array is an Array of tax_ids that apply to these lines
            // That is, the use case of products with more than one tax is supported.
            const tax_ids_array = tax_ids
                .split(",")
                .filter((id) => id !== "")
                .map((id) => Number(id));
            const baseToDiscount = order.calculate_base_amount(
                lines.filter((ll) => ll.isGlobalDiscountApplicable())
            );
            const taxes = tax_ids_array
                .map((taxId) => this.pos.models["account.tax"].get(taxId))
                .filter(Boolean);
            // We add the price as manually set to avoid recomputation when changing customer.
            const discount = (-discount_percentage / 100.0) * baseToDiscount;
            if (discount < 0) {
                await this.pos.addLineToCurrentOrder(
                    { product_id: product, price_unit: discount, tax_ids: [["link", ...taxes]] },
                    { merge: false }
                );
            }
        }
    },

    async manager_discount_approval(order_dis_type,order_dis){
        var order = this.pos.get_order();
        var orderlines = this.currentOrder.get_orderlines()
        const get_cashier = await this.pos.getEmployee(this.pos.get_cashier()['id']);
        console.log(get_cashier)
        var employee_dis_percentage = get_cashier.limited_discount_percentage;
        var employee_dis_amount = get_cashier['limited_discount_amount'];
        var employee_name = this.pos.get_cashier()['name']
        var manager = get_cashier['parent_id']
        var flag = 1;
        if (employee_dis_percentage != 0 || employee_dis_amount !=0) {
            console.log(this.pos)
            orderlines.forEach((order) => {
                if (order_dis_type === "percentage"){
                    if(order_dis > employee_dis_percentage){
                        flag = 0;
                    }
                }
                if (order_dis_type === "fixed"){
                    if(order_dis > employee_dis_amount){
                        flag = 0;
                    }
                }
            });
        }
        if (flag != 1) {
            this.dialog.add(NumberPopup, {
                title: _t(employee_name + ', your discount is over the limit. \n Manager pin for Approval'),
                getPayload: async (num) => {
                    if (manager){
                        var output = this.pos.models["hr.employee"].filter((obj) => obj.id === manager );
                     if (Sha1.hash(num) == output[0]._pin) {
                            this.apply_global_discount(order_dis_type, order_dis)
                     } else {
                        this.notification.add(_t("Manager Restricted your discount"), {
                        type: "danger",
                            title: _t(employee_name + ", Your Manager pin is incorrect."),
                        });
                     }
                    } else {
                       this.notification.add(_t("Manager/Pin not set"), {
                        type: "danger",
                            title: _t(employee_name + ", Manager/Pin not set."),
                        });
                    }
                },
            });
        }else{
            this.apply_global_discount(order_dis_type, order_dis)
        }
    },
});
