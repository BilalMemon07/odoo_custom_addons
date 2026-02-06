/** @odoo-module **/

import {QuantityButtons} from "@sale/js/quantity_buttons/quantity_buttons";
import {rpc} from "@web/core/network/rpc";
import {patch} from "@web/core/utils/patch";
import {_t} from "@web/core/l10n/translation";

QuantityButtons.props = {
    ...QuantityButtons.props,
    min_qty: {type: Number, optional: true},
    multiplier_qty: {type: Number, optional: true},
};

patch(QuantityButtons.prototype, {
    async setup() {
        super.setup();

        const productTmplId = $(this)[0].__owl__.parent.component.props.product_tmpl_id;
        if (productTmplId) {
            const data = await rpc("/website/get_product_min_qty", {
                product_id: productTmplId,
                optional: true,
            });
            if (data) {
                this.props.min_qty = data.min_qty || 1;
                this.props.multiplier_qty = data.multiplier_qty || 1;
                this.props.quantity = this.props.quantity || data.min_qty || 1;
                this.render();
            }
        }
    },

    async increaseQuantity() {
        const multi = this.props.multiplier_qty || 1;
        const productTmplId = $(this)[0].__owl__.parent.component.props.product_tmpl_id;
        const newQuantity = this.props.quantity + multi;
        const data = await rpc("/website/get_product_min_qty", {
            product_id: productTmplId,
            optional: true,
        });
        if (data) {
            this.props.min_qty = data.min_qty || 1;
            this.props.multiplier_qty = data.multiplier_qty || 1;
            this.props.quantity = data.min_qty || 1;
            this.render();
        }
        this.props.setQuantity(newQuantity);
    },

    async decreaseQuantity() {
        const productTmplId = $(this)[0].__owl__.parent.component.props.product_tmpl_id;
        const data = await rpc("/website/get_product_min_qty", {
            product_id: productTmplId,
            optional: true,
        });
        if (data) {
            this.props.min_qty = data.min_qty || 1;

            this.props.multiplier_qty = data.multiplier_qty || 1;
            this.props.quantity = this.props.quantity || data.min_qty;
            this.render();
        }
        const min = this.props.min_qty || 1;
        const multi = this.props.multiplier_qty || 1;
        let newQuantity = this.props.quantity - multi;
        if (newQuantity < min) {
            this._showPopover(_t(`Minimum Quantity is ${min}`));
            newQuantity = min;
        }
        this.props.setQuantity(newQuantity);
    },

    _showPopover(message) {
        const $element = $(".o_sale_product_configurator_qty .quantity");
        $element.popover({
            animation: true,
            title: _t("Quantity Error"),
            container: "body",
            trigger: "manual",
            placement: "top",
            html: true,
            content: message,
        });
        $element.popover("show");
        setTimeout(() => $element.popover("hide"), 2000);
    },
});
