/** @odoo-module **/

import {registry} from "@web/core/registry";
import {_t} from "@web/core/l10n/translation";
import {CharField, charField} from "@web/views/fields/char/char_field";
import {useInputField} from "@web/views/fields/input_field_hook";
const {useRef} = owl;
import {renderToElement} from "@web/core/utils/render";
import {debounce} from "@web/core/utils/timing";
import {rpc} from "@web/core/network/rpc";

export class ShAddressAutoComplete extends CharField {
    /**
     * The purpose of this extension
     * is to allow initialize component
     * @override
     */
    setup() {
        super.setup();
        this.inputRef = useRef("input");
        useInputField({
            getValue: () => this.props.value || "",
            parse: (v) => this.parse(v),
            ref: this.inputRef,
        });
        this.onInputEventAddress = debounce(this.onInputEventAddress, 200);
    }

    _hideAddressesDropdown(container) {
        const addressDropdown = container.querySelector(".js_cls_address_dropdown");
        if (addressDropdown) {
            addressDropdown.remove();
        }
    }

    async _renderAddressDropdown() {
        var self = this;
        if (self.inputRef.el.value) {
            const results = await rpc(
                "/sh_contact_address_google_place/partial_address",
                {partial_address: self.inputRef.el.value}
            );
            console.log(results);
            if (results.length) {
                var data = renderToElement(
                    "sh_contact_address_google_place.AddressDropDown",
                    {
                        results: results,
                    }
                );
                if (data) {
                    self.addressDropdown =
                        data instanceof HTMLElement ||
                        (typeof data === "string" && data.trim().length)
                            ? typeof data === "string"
                                ? new DOMParser().parseFromString(data, "text/html")
                                      .body.firstChild
                                : data
                            : false;
                    return self.addressDropdown;
                }
            }
        }
        if (self.inputRef.el.parentNode) {
            self._hideAddressesDropdown(self.inputRef.el.parentNode);
        }
    }

    async onInputEventAddress() {
        const self = this;
        const response = await self._renderAddressDropdown();

        if (response) {
            const inputC = self.inputRef.el.parentNode;
            if (inputC) {
                self._hideAddressesDropdown(inputC);
                inputC.appendChild(response);

                const addressDropdownItems = inputC.querySelectorAll(
                    ".js_cls_address_dropdown > .js_cls_address_result_item"
                );
                if (addressDropdownItems.length) {
                    addressDropdownItems.forEach((item) => {
                        item.addEventListener(
                            "click",
                            self.onClickDropdownItem.bind(self)
                        );
                    });
                }
            }
        }
    }

    async onClickDropdownItem(ev) {
        const self = this;
        self.inputRef.el.value = ev.currentTarget.innerText;

        const addressDropdownItem = self.inputRef.el.parentNode;
        const addressContainer = addressDropdownItem.parentNode;
        self._hideAddressesDropdown(addressContainer);

        const results = await rpc("/sh_contact_address_google_place/fill_address", {
            address: self.inputRef.el.value || ev.currentTarget.innerText,
            place_id: ev.currentTarget.dataset.placeId,
        });

        if (results) {
            const address = typeof results === "object" ? results : JSON.parse(results);

            // Update input for 'sh_contact_place_text'
            const el1 = document.querySelector(
                'div[name="sh_contact_place_text"] input'
            );
            if (el1) {
                el1.value = JSON.stringify(address);
                el1.dispatchEvent(new InputEvent("input", {bubbles: true}));
                el1.dispatchEvent(new InputEvent("enter", {bubbles: true}));
                el1.dispatchEvent(new InputEvent("change", {bubbles: true}));
            }

            // Update input for 'sh_contact_place_text_main_string'
            const el2 = document.querySelector(
                'div[name="sh_contact_place_text_main_string"] input'
            );
            if (el2) {
                el2.value = self.inputRef.el.value.trim();
                el2.dispatchEvent(new InputEvent("input", {bubbles: true}));
                el2.dispatchEvent(new InputEvent("enter", {bubbles: true}));
                el2.dispatchEvent(new InputEvent("change", {bubbles: true}));
            }
        }
    }
}

ShAddressAutoComplete.template = "sh_contact_address_google_place.CharField";
export const shAddressAutoComplete = {
    ...charField,
    component: ShAddressAutoComplete,
};
registry.category("fields").add("sh_address_auto_complete", shAddressAutoComplete);
