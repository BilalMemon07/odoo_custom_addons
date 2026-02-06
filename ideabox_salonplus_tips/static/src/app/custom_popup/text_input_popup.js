import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class TextInputPopup extends Component {
    static template = "ideabox_salonplus_tips.TextInputPopup";
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
            payment_method: "",
            resources: this.getResourcesWithTips(),
        });

        this.inputRefs = {
            payment_method: useRef("payment_method"),
        };

        onMounted(() => {
            this.inputRefs.payment_method.el?.focus();
        });
    }

    // ✅ Compute resources dynamically from order lines
    getResourcesWithTips() {
        const order = this.pos.get_order();
        if (!order || !order.lines) return [];

        const seen = new Set();
        return order.lines
            .map((line) => {
                if (!line.resource_name) return null;
                let id = line.resource_id;
                if (typeof id === "string" && id.startsWith("hr.employee")) {
                    const match = id.match(/\d+/);
                    id = match ? parseInt(match[0]) : null;
                }
                if (!id || seen.has(id)) return null;
                seen.add(id);
                return {
                    id,
                    name: line.resource_name,
                    tip_amount: "", // each employee gets its own tip input
                };
            })
            .filter((r) => r !== null);
    }

    onTipChange(id, value) {
        // ✅ Update tip amount for the right employee
        this.state.resources = this.state.resources.map((res) =>
            res.id === id ? { ...res, tip_amount: value } : res
        );
    }

    confirm() {
        const { payment_method, resources } = this.state;
        const order = this.pos.get_order();
        if (!order) return;

        // ✅ Map into proper payload format
        const employee_ids = resources.map((r) => r.id);
        const tips_by_employee = resources.map((r) => ({
            id: r.id,
            tip_amount: parseFloat(r.tip_amount) || 0,
        }));

        // ✅ Attach to order (for internal reference)
        order.employee_ids_char = tips_by_employee;

        // ✅ Send to backend
        this.props.getPayload({
            payment_method,
            employee_ids,
            tips_by_employee,
        });

        this.props.close();
    }

    close() {
        this.props.close();
    }
}
