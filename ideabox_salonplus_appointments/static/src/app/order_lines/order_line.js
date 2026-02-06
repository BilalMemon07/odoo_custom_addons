/** @odoo-module */
// Muhammad Bilal
import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

patch(Orderline, {
    props: {
        ...Orderline.props,
        line: {
            ...Orderline.props.line,
            shape: {
                ...Orderline.props.line.shape,
                resource_name: { type: String, optional: true }, 
                resource_id:{ type: Number, optional: true },
              
            },
        },
    },
});
