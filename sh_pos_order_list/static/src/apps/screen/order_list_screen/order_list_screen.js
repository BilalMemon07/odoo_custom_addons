/** @odoo-module **/

import { registry } from "@web/core/registry";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Component, useState } from "@odoo/owl";

export class OrderListScreen extends Component {
    static template = "sh_pos_order_list.OrderListScreen";
    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
        this.search_filter = false
        this.currentPage = 1;
        this.limit = 0
        this.totalCount = this.get_all_orders().length;
        this.nPerPage = this.pos.config.sh_how_many_order_per_page;
        this.offset = this.nPerPage + (this.currentPage - 1) * this.nPerPage;
        this.state = useState({
            search_word: "",
            status : "all",
            order_date : "",
        })
    }
    get_all_orders(){
        return this.pos.models['pos.order'].filter((order) => typeof order.id === "number")
    }
    get currentOrder() {
        if (this.pos.get_order()) {
            return this.pos.get_order()
        } else {
            return false
        }
    }
    async print_pos_order(order) {
        event.stopPropagation()
        if (order) {
            this.pos.printReceipt({ order: order, sh_reprint: true });
        }
    }
    async reorder_pos_order(order) {
        var self = this;
        event.stopPropagation()
        if (order) {
            var order_lines = self.pos.get_order().get_orderlines();
            [...order_lines].map(async (line) => await self.currentOrder.removeOrderline(line));
            if (order.partner_id){
                await self.currentOrder.set_partner(order.partner_id)
            }
            if (order.lines) {
                for (let line of order.lines) {
                    var product = line.product_id
                    if (product) {
                        await this.pos.addLineToCurrentOrder({
                            product_id: product,
                            qty: line.qty,
                            customerNote: line.customer_note || null,
                        }, {}, false);
                        if (line.discount) {
                            self.currentOrder.get_selected_orderline().set_discount(line.discount)
                        }
                    }
                }
                self.back()
            }
        }
    }
    sh_appy_search(search) {
        self = this
        if (self.state.order_date) {
            // Date wise Condition.
            search = self.state.search_word;
            if (this.state.status != "all") {
                return this.get_all_orders().filter(function (template) {
                    if ((template["state"] === self.state.status) && (template["date_order"].split(" ")[0] == self.state.order_date)) {
                        if (template.name.indexOf(search) > -1) {
                            return true;
                        }
                        if (template["pos_reference"] && template["pos_reference"].indexOf(search) > -1) {
                            return true;
                        }
                        if (template.partner_id) {
                            if (template.partner_id.name.indexOf(search) > -1 || template.partner_id.name.toLowerCase().indexOf(search) > -1) {
                                return true;
                            }
                        }
                        if (template["state"] && template["state"].indexOf(search) > -1) {
                            return true;
                        }
                        if (template["date_order"] && template["date_order"].indexOf(search) > -1) {
                            return true;
                        }
                        if(!search){
                            return true;
                        }
                    }
                    return false;
                })
            }else{
                return this.get_all_orders().filter(function (template) {
                    if (template["date_order"].split(" ")[0] == self.state.order_date) {
                        if (template.name.indexOf(search) > -1) {
                            return true;
                        }
                        if (template["pos_reference"] && template["pos_reference"].indexOf(search) > -1) {
                            return true;
                        }
                        if (template.partner_id) {
                            if (template.partner_id.name.indexOf(search) > -1 || template.partner_id.name.toLowerCase().indexOf(search) > -1) {
                                return true;
                            }
                        }
                        if (template["state"] && template["state"].indexOf(search) > -1) {
                            return true;
                        }
                        if (template["date_order"] && template["date_order"].indexOf(search) > -1) {
                            return true;
                        }
                        if(!search){
                            return true;
                        }
                    return false;
                    }
                })
            }
            
        }else{

            search = self.state.search_word;
            if (this.state.status != "all") {
                return this.get_all_orders().filter(function (template) {
                    if (template["state"] === self.state.status) {
                        if (template.name.indexOf(search) > -1) {
                            return true;
                        }
                        if (template["pos_reference"] && template["pos_reference"].indexOf(search) > -1) {
                            return true;
                        }
                        if (template.partner_id) {
                            if (template.partner_id.name.indexOf(search) > -1 || template.partner_id.name.toLowerCase().indexOf(search) > -1) {
                                return true;
                            }
                        }
                        if (template["state"] && template["state"].indexOf(search) > -1) {
                            return true;
                        }
                        if (template["date_order"] && template["date_order"].indexOf(search) > -1) {
                            return true;
                        }
                        if(!search){
                            return true;
                        }
                    }
                    return false;
                })
            }else{
                return this.get_all_orders().filter(function (template) {
    
                        if (template.name.indexOf(search) > -1) {
                            return true;
                        }
                        if (template["pos_reference"] && template["pos_reference"].indexOf(search) > -1) {
                            return true;
                        }
                        if (template.partner_id) {
                            if (template.partner_id.name.indexOf(search) > -1 || template.partner_id.name.toLowerCase().indexOf(search) > -1) {
                                return true;
                            }
                        }
                        if (template["state"] && template["state"].indexOf(search) > -1) {
                            return true;
                        }
                        if (template["date_order"] && template["date_order"].indexOf(search) > -1) {
                            return true;
                        }
                        if(!search){    
                            return true;
                        }
                    return false;
                })
            }

        }
       

    }
    get get_orders() {
        if (this.search_filter) {
            return this.filteredOrders.slice(this.limit, this.offset);
        } else {
            var orders =this.get_all_orders().slice(this.limit, this.offset)
            return orders.sort((a, b) => (b.id - a.id));
        }
    }
    async updateOrderList(event) {
        var search = event.target.value;
        this.state.search_word = search;
        var Orders = await this.sh_appy_search(search)
        this.search_filter = true
        this.filteredOrders = Orders
        // if (search) {
        //     var Orders = await this.sh_appy_search(search)
        //     this.search_filter = true
        //     this.filteredOrders = Orders
        // } else {
        //     this.search_filter = false
        //     this.filteredOrders = []
        // }
        this.render(true)
    }
    async change_date(event) {
        let search = event.target.value;
        var Orders = await this.sh_appy_search(search)
        this.search_filter = true
        this.filteredOrders = Orders
        this.render(true)

        // if (search) {
        //     var Orders = await this.sh_appy_search(search)
        //     this.search_filter = true
        //     this.filteredOrders = Orders
        //     this.render(true)
        // } else {
        //     this.search_filter = false
        //     this.filteredOrders = []
        // }
    }
    async ShApplyFilter(ev) {
        let search = ev.target.value;
        this.state.status = search;
        // if (search == "all") {
        //     this.search_filter = false
        //     this.filteredOrders = []
        // } else {
            this.search_filter = true
            var Orders = await this.sh_appy_search(search)
            this.filteredOrders = Orders
        // }
        this.render(true)
    }
    onNextPage() {
        if (this.currentPage <= this.lastPage) {
            this.currentPage += 1;
            this.limit = this.offset;
            this.offset = this.nPerPage + (this.currentPage - 1) * this.nPerPage;
            this.render()
        }
    }
    onPrevPage() {
        if (this.currentPage - 1 > 0) {
            this.currentPage -= 1;
            this.limit = this.nPerPage + (this.currentPage - 1 - 1) * this.nPerPage;
            this.offset = this.limit + this.nPerPage;
            this.render()
        }
    }
    get lastPage() {
        let nItems = 0
        if (this.search_filter) {
            nItems = this.filteredOrders.length;
            return Math.ceil(nItems / (this.nPerPage));
        } else {
            nItems = this.totalCount;
            return Math.ceil(nItems / (this.nPerPage));
        }
    }
    get pageNumber() {
        const currentPage = this.currentPage;
        const lastPage = this.lastPage;
        return isNaN(lastPage) ? "" : `(${currentPage}/${lastPage})`;
    }
    clear_search() {
        this.state.search_word = ""
        this.search_filter = false
        this.filteredOrders = []
        this.render(true)
    }
    clickLine(orderlist) {
        if(this.show_lines == orderlist.id){
            this.show_lines = 0
        }else{
            this.show_lines = orderlist.id
        }
        this.render(true)
    }
    back() {
        this.pos.showScreen('ProductScreen')
    }
}
registry.category("pos_screens").add("OrderListScreen", OrderListScreen);
