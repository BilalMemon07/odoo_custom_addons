/** @odoo-module **/

import {_t} from "@web/core/l10n/translation";
import publicWidget from "@web/legacy/js/public/public_widget";
import {session} from "@web/session";
import {rpc} from "@web/core/network/rpc";
import VariantMixin from "@website_sale/js/sale_variant_mixin";
import {patch} from "@web/core/utils/patch";

publicWidget.registry.WebsiteSale.include({
    init: function () {
        this._super.apply(this, arguments);
        this.orm = this.bindService("orm");
        this.is_update = false;
    },

    _submitForm: async function () {
        const params = this.rootProduct;
        const $product = $("#product_detail");
        const productTrackingInfo = $product.data("product-tracking-info");
        if (productTrackingInfo) {
            productTrackingInfo.quantity = params.quantity;
            $product.trigger("add_to_cart_event", [productTrackingInfo]);
        }
        const viewObjects = await rpc("/website/get_product_min_qty", {
            product_id: this.rootProduct.product_id,
            optional: false,
        });
        const min_qty = viewObjects.min_qty;

        if (params.quantity < min_qty) {
            console.log("set");
            params.add_qty = min_qty;
        } else {
            params.add_qty = params.quantity;
        }
        params.product_custom_attribute_values = JSON.stringify(
            params.product_custom_attribute_values
        );
        params.no_variant_attribute_values = JSON.stringify(
            params.no_variant_attribute_values
        );
        delete params.quantity;
        return this.addToCart(params);
    },

    _onChangeCombination: function (ev, $parent, combination) {
        this._super.apply(this, arguments);
        self = this;
        var combination_data = rpc("/bi_minimum_order_quantity/get_combination_info", {
            product_id: combination.product_id,
        }).then((result) => {
            console.log(self.is_update);
            console.log(result);
            this.is_update = false;
        });
    },

    /**
     * Hack to add and remove from cart with json
     *
     * @param {MouseEvent} ev
     */
    onClickAddCartJSON: function (ev) {
        this._super.apply(this, arguments);
        this.is_update = true;
    },
});

publicWidget.registry.websiteSaleCart.include({
    _onClickDeleteProduct: function (ev) {
        ev.preventDefault();
        session.is_delete = true;
        $(ev.currentTarget)
            .closest(".o_cart_product")
            .find(".js_quantity")
            .val(0)
            .trigger("change");
    },
});

publicWidget.registry.DeliveryPreference = publicWidget.Widget.extend({
    selector: ".oe_website_sale",

    events: {
        "change  .qty_add": "_onChangeInputQty",
        "change .js_quantity, .js_main_product": "_onChangeInputQtyCartLine",
        "change .td-qty": "_onChangeInputQtyCartLineopt",
    },

    _onChangeInputQtyCartLineopt: async function (event) {
        var uniqueId = $("tr.js_product.in_cart");
        uniqueId.each(function (index, element) {
            var qty_input_ = $(this).find('input[name="add_qty"]');
            var qty = qty_input_.val();
            var opMinQtyValue = $(this).find(".op_min_qty");
            var min_qty = parseInt(opMinQtyValue.text());

            if ($(".js_product").length) {
                if (!session.is_delete) {
                    if (min_qty > parseInt(qty)) {
                        var qty = qty_input_.val(min_qty).html(min_qty);
                    }
                }
            }
        });
    },

    _onChangeInputQty: function (event) {
        const product_configurator_qty = $(
            ".o_sale_product_configurator_qty .quantity"
        );
        if (product_configurator_qty.length <= 0) {
            var qty_input = $(event.currentTarget)
                .closest(".input-group")
                .find("input");
            var qty = qty_input.val();
            console.log("qty", qty);
            var $form_data = $("div.js_product").closest("form");
            var min_qty = $("#o_wsale_cta_wrapper").find('input[name="min_qty"]').val();
            console.log(qty_input);
            if (min_qty > parseFloat(qty || 0)) {
                var qty = $(event.target)
                    .closest("form")
                    .find('input[name="add_qty"]')
                    .val(parseInt(min_qty))
                    .html(parseInt(min_qty));
                qty_input.popover("dispose");
                qty_input.popover({
                    animation: true,
                    title: _t("DENIED"),
                    container: "body",
                    trigger: "focus",
                    placement: "top",
                    html: true,
                    content: _t("Minimum Quantity is " + parseInt(min_qty)),
                });
                console.log(`---< parseInt(min_qty): ${parseInt(min_qty)}`);
                qty_input.popover("show");
                setTimeout(function () {
                    qty_input.popover("hide");
                }, 2000);
            } else {
                qty_input.popover("dispose");
            }
        }
    },

    _onChangeInputQtyCartLine: function (event) {
        var qty_input = $(event.currentTarget).closest(".input-group").find("input");
        var qty = qty_input.val();
        var line_id = qty_input.attr("data-line-id");
        var min_qty_cart = $(".min_qty_" + line_id + "");

        if ($(".js_cart_lines").length) {
            if (!session.is_delete) {
                if (parseInt(min_qty_cart.val()) > parseInt(qty)) {
                    var qty = qty_input
                        .val(min_qty_cart.val())
                        .html(min_qty_cart.val());
                    qty_input.popover("dispose");
                    qty_input.popover({
                        animation: true,
                        title: _t("DENIED2"),
                        container: "body",
                        trigger: "focus",
                        placement: "top",
                        html: true,
                        content: _t("Minimum Quantity is " + min_qty_cart.val()),
                    });
                    qty_input.popover("show");
                    setTimeout(function () {
                        qty_input.popover("hide");
                    }, 2000);
                }
            }
        }
    },
});
