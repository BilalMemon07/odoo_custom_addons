/** @odoo-module */
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";
import { useState, Component, xml } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(OrderReceipt.prototype, {
    setup(){
        console.log('setupp')
        super.setup();
        this.state = useState({
            template: true,
        })
        this.pos = useState(useService("pos"));

    },

    get templateProps() {
        console.log('templateProps')
        return {
            data: this.props.data,
            order: this.pos.get_order(),
            receipt: this.pos.get_order().export_for_printing(),
            orderlines: this.props.data.orderlines,
            paymentlines: this.pos.get_order().export_for_printing().paymentlines
        };
    },
    get templateComponent() {
        const customReceiptTemplate  = xml`
           <style>
.pos-receipt {
        width: 280px;
        background-color: white;
        padding: 15px;
    }

    .pos-receipt-logo {
        display: block;
        margin: 0 auto 10px;
        max-width: 150px;
        max-height: 80px;
    }

    .receipt-header {
        text-align: center;
        margin-bottom: 15px;
        border-bottom: 1px dashed #ddd;
        padding-bottom: 10px;
    }

    .company-name {
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 5px;
    }

    .receipt-info {
        margin-bottom: 15px;
        font-size: 12px;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 3px;
    }

    .info-label {
        font-weight: bold;
    }

    .receipt-orderlines {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 15px;
    }

    .receipt-orderlines th {
        border-bottom: 1px dashed #333;
        padding: 5px 0;
        text-align: left;
        font-size: 12px;
    }

    .receipt-orderlines td {
        padding: 5px 0;
        font-size: 12px;
        vertical-align: top;
    }

    .product-col {
        width: 55%;
        text-align: left;
    }

    .qty-col {
        width: 20%;
        text-align: left;
        padding-left: 2px;
    }

    .amount-col {
        width: 25%;
        text-align: right;
    }

    .product-name {
        font-weight: bold;
    }

    .discount-note {
        font-size: 10px;
        color: #666;
        font-style: italic;
    }

    .customer-note {
        font-size: 10px;
        color: #333;
        margin-top: 2px;
    }

    .receipt-totals {
        border-top: 1px dashed #333;
        padding-top: 10px;
        margin-bottom: 15px;
    }

    .total-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
        font-size: 12px;
    }

    .total-label {
        font-weight: bold;
    }

    .total-amount {
        font-weight: bold;
    }

    .grand-total {
        font-size: 14px;
        font-weight: bold;
        border-top: 1px solid #333;
        padding-top: 5px;
        margin-top: 5px;
    }

    .payment-section {
        border-top: 1px dashed #333;
        padding-top: 10px;
        margin-bottom: 10px;
    }

    .payment-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 10px;
    }

    .payment-table th {
        border-bottom: 1px dashed #333;
        padding: 5px 0;
        text-align: left;
        font-size: 12px;
    }

    .payment-table td {
        padding: 5px 0;
        font-size: 12px;
    }

    .payment-method-col {
        width: 60%;
        text-align: left;
    }

    .payment-amount-col {
        width: 40%;
        text-align: right;
    }

    .receipt-footer {
        text-align: center;
        margin-top: 15px;
        font-size: 12px;
        border-top: 1px dashed #ddd;
        padding-top: 10px;
    }

    .thank-you {
        font-weight: bold;
        margin-top: 10px;
    }

    .text-center {
        text-align: center;
    }

    .text-right {
        text-align: right;
    }

    .bold {
        font-weight: bold;
    }

    .italic {
        font-style: italic;
    }
    
    .pos-receipt-taxes {
        margin-top: 10px;
        margin-bottom: 10px;
    }
    
    .pos-receipt-amount {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
        font-size: 12px;
    }
    
    .pos-receipt-right-align {
        text-align: right;
    }
    
    .d-flex {
        display: flex;
        justify-content: space-between;
        margin-bottom: 3px;
        font-size: 12px;
    }
    
    .fw-bolder {
        font-weight: bolder;
    }
    
    .ms-auto {
        margin-left: auto;
    }
    
    .me-2 {
        margin-right: 10px;
    }
    
    .text-start {
        text-align: left;
    }
    
    .divider {
        text-align: center;
        margin: 5px 0;
    }
    
    .amount-due {
        font-weight: bold;
        color: #d9534f;
        border-top: 1px solid #333;
        padding-top: 5px;
        margin-top: 5px;
    }
</style>

<div class="pos-receipt">
    <!-- Logo Section -->
    <t t-if="env.services.pos.config.logo">
        <img t-att-src="'data:image/png;base64,' + env.services.pos.config.logo"
             alt="Logo" class="pos-receipt-logo"/>
    </t>
    
    <!-- Company Info -->
    <div class="receipt-header">
        <div class="company-name">
            <t t-esc="env.services.pos.company.name"/>
        </div>
        <div class="receipt-info">
            <div class="info-row">
                <span>Phone:</span>
                <span><t t-esc="env.services.pos.company.phone || 'N/A'"/></span>
            </div>
        </div>
    </div>
    
    <!-- Order Details -->
    <div class="receipt-info">
        <div class="info-row">
            <span class="info-label">Date:</span>
            <span>
                <t t-if="props.receipt.date">
                    <t t-esc="props.receipt.date"/>
                </t>
                <t t-else="">
                    <t t-esc="props.order.validation_date"/>
                </t>
            </span>
        </div>
        <div class="info-row">
            <span class="info-label">Order:</span>
            <span><t t-esc="props.data.cashier"/></span>
        </div>
        <div class="info-row">
            <span class="info-label">Cashier:</span>
            <span><t t-esc='props.order.cashier'/></span>
        </div>
        <t t-if="props.order.partner_id">
            <div class="info-row">
                <span class="info-label">Customer:</span>
                <span class="bold"><t t-esc='props.order.partner_id.name'/></span>
            </div>
        </t>
        <t t-if="props.order.partner_id">
            <div class="info-row">
                <span class="info-label">Phone:</span>
                <span class="bold"><t t-esc='props.order.partner_id.phone'/></span>
            </div>
        </t>
    </div>
    
    <!-- Header Message -->
    <t t-if="props.receipt.headerData.header">
        <div class="text-center receipt-info">
            <t t-esc="props.receipt.headerData.header" />
        </div>
    </t>
    
    <!-- Order Lines -->
    <table class='receipt-orderlines'>
        <thead>
            <tr>
                <th class="product-col">Product</th>
                <th class="qty-col">Qty</th>
                <th class="amount-col">Amount</th>
            </tr>
        </thead>
        <tbody>
            <t t-if="props.order and props.order.length and props.order and props.order.pos and props.order.pos.mainScreen and props.order.pos.mainScreen.props and props.order.pos.mainScreen.props.order and props.order.pos.mainScreen.props.order.orderlines and props.order.pos.mainScreen.props.order.orderlines.length">
                <t t-if="props.order.pos.mainScreen.props">
                    <tr t-foreach="props.order.pos.mainScreen.props.order.orderlines" t-as="orderline" t-key="index_orderlines">
                        <td class="product-col">
                            <div class="product-name"><t t-esc="orderline.productName"/></div>
                            <t t-if="orderline.discount > 0">
                                <div class="discount-note">
                                    <t t-esc="orderline.discount"/>% discount
                                </div>
                            </t>
                            <t t-if="orderline.customerNote">
                                <div class="customer-note" t-esc="orderline.customerNote"/>
                            </t>
                        </td>
                        <td class="qty-col"><t t-esc="orderline.qty"/></td>
                        <td class="amount-col"><t t-esc="orderline.price"/></td>
                    </tr>
                </t>
            </t>
            <t t-else="">
                <t t-if="props.orderlines and props.orderlines.length">
                    <tr t-foreach="props.orderlines" t-as="orderline" t-key="orderline_index">
                        <td class="product-col">
                            <div class="product-name"><t t-esc="orderline.productName"/></div>
                            <t t-if="orderline.discount > 0">
                                <div class="discount-note">
                                    <t t-esc="orderline.discount"/>% discount
                                </div>
                            </t>
                            <t t-if="orderline.customerNote">
                                <div class="customer-note" t-esc="orderline.customerNote"/>
                            </t>
                        </td>
                        <td class="qty-col"><t t-esc="orderline.qty"/></td>
                        <td class="amount-col"><t t-esc="orderline.price"/></td>
                    </tr>
                </t>
            </t>
        </tbody>
    </table>
    
    <!-- Odoo Tax and Total Section -->
    <t t-set="taxTotals" t-value="props.data.taxTotals"/>
    <t t-if="taxTotals and taxTotals.has_tax_groups">
        <div class="pos-receipt-taxes">
            <div class="divider">--------------------------------</div>
            <t t-foreach="taxTotals.subtotals" t-as="subtotal" t-key="subtotal.name">
                <div class="d-flex">
                    <span class="fw-bolder text-nowrap mw-100" t-out="subtotal.name"/>
                    <span t-esc="env.utils.formatCurrency(subtotal.base_amount_currency)" class="ms-auto"/>
                </div>

                <div t-foreach="subtotal.tax_groups" t-as="tax_group" t-key="tax_group.id" class="d-flex">
                    <span>
                        <span t-esc="tax_group.group_name"/>
                        <t t-if="!taxTotals.same_tax_base">
                            on
                            <span t-esc="env.utils.formatCurrency(tax_group.base_amount_currency)"/>
                        </t>
                    </span>
                    <span t-esc="env.utils.formatCurrency(tax_group.tax_amount_currency)" class="ms-auto"/>
                </div>
            </t>
        </div>
    </t>

    <div class="divider">--------------------------------</div>
    <div class="pos-receipt-amount receipt-total">
        <t t-out="props.data.label_total"/>
        <span t-esc="env.utils.formatCurrency(taxTotals.order_sign * taxTotals.order_total)" class="pos-receipt-right-align"/>
    </div>
    
    <t t-if="props.data.show_rounding">
        <div class="pos-receipt-amount receipt-rounding">
            <t t-out="props.data.label_rounding"/>
            <span t-esc="env.utils.formatCurrency(taxTotals.order_sign * taxTotals.order_rounding)" class="pos-receipt-right-align"/>
        </div>
        <div class="pos-receipt-amount receipt-to-pay">
            To Pay
            <span t-esc="env.utils.formatCurrency(taxTotals.order_sign * (taxTotals.order_total + taxTotals.order_rounding))" class="pos-receipt-right-align"/>
        </div>
    </t>

    <!-- Payment Section with Table Design -->
    <div class="payment-section">
        <table class="payment-table">
            <thead>
                <tr>
                    <th class="payment-method-col">Payment Method</th>
                    <th class="payment-amount-col">Amount</th>
                </tr>
            </thead>
            <tbody>
                <t t-foreach="props.data.paymentlines" t-as="line" t-key="line_index">
                    <tr>
                        <td class="payment-method-col"><t t-esc="line.name" /></td>
                        <td class="payment-amount-col"><t t-esc="env.utils.formatCurrency(line.amount)"/></td>
                    </tr>
                </t>
            </tbody>
        </table>
    </div>

    <!-- Change Amount -->
    <t t-if="props.data.show_change">
        <div class="pos-receipt-amount receipt-change">
            <t t-out="props.data.label_change"/>
            <span t-esc="env.utils.formatCurrency(props.data.order_change)" class="pos-receipt-right-align"/>
        </div>
    </t>
    <!-- Amount Due Section -->
    <t>
        <div class="divider">--------------------------------</div>
        <div class="pos-receipt-amount amount-due">
            <span>AMOUNT DUE:</span>
            <span t-esc="env.utils.formatCurrency(props.data.sh_amount_residual)" class="pos-receipt-right-align"/>
        </div>
    </t>
    

    <!-- Extra Payment Info -->
    <t t-if="props.data.total_discount">
        <div class="text-center">
            <t t-out="props.data.label_discounts"/>
            <span t-esc="env.utils.formatCurrency(props.data.total_discount)" class="pos-receipt-right-align"/>
        </div>
    </t>

    <div class="before-footer" />

    <!-- Footer -->
    <div class='receipt-footer'>
        
        <t t-if='!props.receipt.footer_html and props.receipt.footer'>
            <t t-esc='props.receipt.footer'/>
        </t>
        
        <t t-foreach='props.paymentlines' t-as='line' t-key="index_payment">
            <t t-if='line.ticket'>
                <div class="pos-payment-terminal-receipt">
                    <pre t-esc="line.ticket" />
                </div>
            </t>
        </t>
        
        <div class="thank-you">
            Thank You... Please Visit Again ...
        </div>
    </div>
</div>
        `
        console.log('templateComponent')
        var mainRef = this;
        return class extends Component {
            setup() {}
            // static template = customReceiptTemplate
            static template = xml`${mainRef.pos.config.design_receipt}`
        };
    },
    get isTrue() {
                console.log('isTrue')
        if (this.env.services.pos.config.is_custom_receipt == false) {
            return true;
        }
        return false;
    }
});
