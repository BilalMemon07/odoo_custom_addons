import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class TextInputPopup extends Component {
    static template = "ideabox_salonplus_commission.TextInputPopup";
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
        this.pos = usePos();

        this.state = useState({
            service_type: "",
        });

        this.inputRefs = {
            service_type: useRef("service_type"),
        };

        onMounted(() => {
            this.inputRefs.service_type.el?.focus();
        });
    }

    confirm() {
        const { service_type } = this.state;
        const order = this.pos.get_order();
        if (!order) return;


        order.service_type = service_type;
        this.props.getPayload({
            service_type,
        });

        this.props.close();
    }

    close() {
        this.props.close();
    }
}
