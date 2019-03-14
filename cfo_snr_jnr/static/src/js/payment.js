odoo.define('cfo_snr_jnr.payment', function(require) {
    "use strict";

    var payment = require('payment.payment_form')
    var ajax = require('web.ajax');
    var core = require('web.core');
    var Dialog = require("web.Dialog");
    var Widget = require("web.Widget");
    var rpc = require("web.rpc");
    var _t = core._t;

    var payment = payment.include({

        payEvent: function(ev) {
            ev.preventDefault();
            var form = this.el;
            var checked_radio = this.$('input[type="radio"]:checked');

            //            var checked_checkbox = this.$('input[type="checkbox"]:checked');
            //            console.log('checked_checkbox', checked_checkbox)
            var self = this;
            var button = ev.target;

            // first we check that the user has selected a payment method
            if (checked_radio.length === 2) {
                checked_radio = checked_radio[0];
                if ($('input[type="checkbox"]:checked').length === 1) {

                    // we retrieve all the input inside the acquirer form and 'serialize' them to an indexed array
                    var acquirer_id = this.getAcquirerIdFromRadio(checked_radio);
                    var acquirer_form = false;
                    if (this.isNewPaymentRadio(checked_radio)) {
                        acquirer_form = this.$('#o_payment_add_token_acq_' + acquirer_id);
                    } else {
                        acquirer_form = this.$('#o_payment_form_acq_' + acquirer_id);
                    }
                    var inputs_form = $('input', acquirer_form);
                    var ds = $('input[name="data_set"]', acquirer_form)[0];

                    // if the user is adding a new payment
                    if (this.isNewPaymentRadio(checked_radio)) {
                        if (this.options.partnerId === undefined) {
                            console.warn('payment_form: unset partner_id when adding new token; things could go wrong');
                        }
                        var form_data = this.getFormData(inputs_form);
                        var wrong_input = false;

                        inputs_form.toArray().forEach(function(element) {
                            //skip the check of non visible inputs
                            if ($(element).attr('type') == 'hidden') {
                                return true;
                            }
                            $(element).closest('div.form-group').removeClass('has-error');
                            $(element).siblings(".o_invalid_field").remove();
                            //force check of forms validity (useful for Firefox that refill forms automatically on f5)
                            $(element).trigger("focusout");
                            if (element.dataset.isRequired && element.value.length === 0) {
                                $(element).closest('div.form-group').addClass('has-error');
                                $(element).closest('div.form-group').append('<div style="color: red" class="o_invalid_field">' + _.str.escapeHTML("The value is invalid.") + '</div>');
                                wrong_input = true;
                            } else if ($(element).closest('div.form-group').hasClass('has-error')) {
                                wrong_input = true;
                                $(element).closest('div.form-group').append('<div style="color: red" class="o_invalid_field">' + _.str.escapeHTML("The value is invalid.") + '</div>');
                            }
                        });

                        if (wrong_input) {
                            return;
                        }

                        $(button).attr('disabled', true);
                        $(button).children('.fa-plus-circle').removeClass('fa-plus-circle')
                        $(button).prepend('<span class="o_loader"><i class="fa fa-refresh fa-spin"></i>&nbsp;</span>');

                        var verify_validity = this.$el.find('input[name="verify_validity"]');

                        if (verify_validity.length > 0) {
                            form_data.verify_validity = verify_validity[0].value === "1";
                        }

                        // do the call to the route stored in the 'data_set' input of the acquirer form, the data must be called 'create-route'
                        ajax.jsonRpc(ds.dataset.createRoute, 'call', form_data).then(function(data) {
                            // if the server has returned true
                            if (data.result) {
                                // and it need a 3DS authentication
                                if (data['3d_secure'] !== false) {
                                    // then we display the 3DS page to the user
                                    $("body").html(data['3d_secure']);
                                } else {
                                    checked_radio.value = data.id; // set the radio value to the new card id
                                    form.submit();
                                }
                            }
                            // if the server has returned false, we display an error
                            else {
                                if (data.error) {
                                    self.displayError(
                                        '',
                                        data.error);
                                } else { // if the server doesn't provide an error message
                                    self.displayError(
                                        _t('Server Error'),
                                        _t('e.g. Your credit card details are wrong. Please verify.'));
                                }
                            }
                            // here we remove the 'processing' icon from the 'add a new payment' button
                            $(button).attr('disabled', false);
                            $(button).children('.fa').addClass('fa-plus-circle')
                            $(button).find('span.o_loader').remove();
                        }).fail(function(message, data) {
                            // if the rpc fails, pretty obvious
                            $(button).attr('disabled', false);
                            $(button).children('.fa').addClass('fa-plus-circle')
                            $(button).find('span.o_loader').remove();

                            self.displayError(
                                _t('Server Error'),
                                _t("We are not able to add your payment method at the moment.") +
                                data.data.message
                            );
                        });
                    }
                    // if the user is going to pay with a form payment, then
                    else if (this.isFormPaymentRadio(checked_radio)) {
                        var $tx_url = this.$el.find('input[name="prepare_tx_url"]');
                        // if there's a prepare tx url set
                        if ($tx_url.length === 1) {
                            // if the user wants to save his credit card info
                            var form_save_token = acquirer_form.find('input[name="o_payment_form_save_token"]').prop('checked');
                            // then we call the route to prepare the transaction.
                            ajax.jsonRpc($tx_url[0].value, 'call', {
                                'acquirer_id': parseInt(acquirer_id),
                                'save_token': form_save_token,
                                'access_token': self.options.accessToken,
                                'success_url': self.options.successUrl,
                                'error_url': self.options.errorUrl,
                                'callback_method': self.options.callbackMethod,
                                'do_invoice': $('input[type=radio][name=shop_do_invoice]:checked').val(),
                                'company_name': $('input[type=text][name=company_name]').val(),
                                'vat_no': $('input[type=text][name=vat_no]').val(),
                            }).then(function(result) {
                                if (result) {
                                    // if the server sent us the html form, we create a form element
                                    var newForm = document.createElement('form');
                                    newForm.setAttribute("method", "post"); // set it to post
                                    newForm.setAttribute("provider", checked_radio.dataset.provider);
                                    newForm.hidden = true; // hide it
                                    newForm.innerHTML = result; // put the html sent by the server inside the form
                                    var action_url = $(newForm).find('input[name="data_set"]').data('actionUrl');
                                    newForm.setAttribute("action", action_url); // set the action url
                                    $(document.getElementsByTagName('body')[0]).append(newForm); // append the form to the body
                                    $(newForm).find('input[data-remove-me]').remove(); // remove all the input that should be removed
                                    if (action_url) {
                                        newForm.submit(); // and finally submit the form
                                    }
                                } else {
                                    self.displayError(
                                        _t('Server Error'),
                                        _t("We are not able to redirect you to the payment form.")
                                    );
                                }
                            }).fail(function(message, data) {
                                self.displayError(
                                    _t('Server Error'),
                                    _t("We are not able to redirect you to the payment form.<") +
                                    data.data.message
                                );
                            });
                        } else {
                            // we append the form to the body and send it.
                            this.displayError(
                                _t("Cannot set-up the payment"),
                                _t("We're unable to process your payment.")
                            );
                        }
                    } else { // if the user is using an old payment then we just submit the form
                        form.submit();
                    }
                } else {
                    alert('Please accept Terms & Conditions')
                }
            } else {
                this.displayError(
                    _t('No payment method selected'),
                    _t('Please select a payment method.')
                );
            }
        },
    });
});