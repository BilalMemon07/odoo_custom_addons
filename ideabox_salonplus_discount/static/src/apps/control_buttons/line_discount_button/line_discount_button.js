/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { LineDiscountPopup } from "@ideabox_salonplus_discount/apps/popups/line_discount_popup/line_discount_popup";
import { _t } from "@web/core/l10n/translation";
patch(ProductScreen.prototype, {
  async onNumpadClick(buttonValue) {
    if (buttonValue === "discount") {
      this.numberBuffer.capture();
      this.numberBuffer.reset();
      this.dialog.add(LineDiscountPopup, {
        title: _t("Apply Product Discount"),
        getPayload: async ({ discount_type, discount_value }) => {
          const order = this.pos.get_order();
          const selectedLine = order?.get_selected_orderline();
          if (!selectedLine) return;
          const value = parseFloat(discount_value);
          if (isNaN(value) || value <= 0) return;
          let percentage = value;
          if (discount_type === "fixed") {
            const line_total =
              selectedLine.get_unit_price() * selectedLine.get_quantity();
            if (line_total > 0) {
              percentage = (value / line_total) * 100;
            } else {
              percentage = 0;
            }
          }
          selectedLine.set_discount(percentage);
          const line_total_before_discount =
            selectedLine.get_unit_price() * selectedLine.get_quantity();
          const discount_amount =
            (line_total_before_discount * percentage) / 100;
          selectedLine.discount_amount = discount_amount;
        },
      });
      return;
    }
    return super.onNumpadClick(buttonValue);
  },
});
