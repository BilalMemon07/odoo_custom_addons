/** @odoo-module **/

import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class LineDiscountPopup extends Component {
    static template = "ideabox_salonplus_discount.LineDiscountPopup";
    static components = { Dialog };
    static props = {
        title: String,
        buttons: { type: Array, optional: true },
        getPayload: Function,
        close: Function,
    };
    static defaultProps = {
        buttons: [],
    };
    setup() {
        this.state = useState({
            discount_type: "percentage",
            discount_value: "",
        });
        this.inputRefs = {
            discount_value: useRef("discount_value"),
        };

        onMounted(() => {
            setTimeout(() => {
                this.inputRefs.discount_value.el?.focus();
            }, 0);
        });
    }
    confirm() {
        const { discount_type, discount_value } = this.state;
        this.props.getPayload({
            discount_type,
            discount_value,
        });

        this.props.close();
    }
    close() {
        this.props.close();
    }
}
