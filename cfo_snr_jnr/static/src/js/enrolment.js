odoo.define('cfo_snr_jnr.enrolment', function(require) {
    var ajax = require('web.ajax');

    $(document).ready(function() {
    	
    	if (window.location.pathname == '/payment') {
    		 if (parseInt($('#inputPaypercentage').val()) != 100) {
    			 $('#debitrequiredcheckbox').prop("required", true);
    		 }else{
    			 $('#debitrequiredcheckbox').prop("required", false);
    		 }
    	
        }

        function profbody_campus_sem(data) {
            ajax.jsonRpc("/get_event_data", 'call', {
                'professional_body': data
            }).then(
                function(result) {
                    var select = document.getElementById("select_campus");
                    select.options.length = 0;
                    var select = document.getElementById("select_semester");
                    select.options.length = 0;
                    var locationoptions = "";
                    for (var i = 0; i < result['location'].length; i++) {
                        locationoptions += "<option id='" + result['location'][i]['id'] + "' value='" + result['location'][i]['id'] + "'>" + result['location'][i]['name'] + "</option>";
                    }
                    $('select[id="select_campus"]').append(locationoptions);

                    var semesteroptions = "";
                    for (var i = 0; i < result['semester'].length; i++) {
                        semesteroptions += "<option id='" + result['semester'][i]['id'] + "' value='" + result['semester'][i]['id'] + "'>" + result['semester'][i]['name'] + "</option>";
                    }
                    $('select[id="select_semester"]').append(semesteroptions);
                });
        }

        if ($('select[id="professional_body"]').val() == '') {
            $('#reg_campus_info').hide();
            $('#reg_campus').hide();
            $('#reg_enrol_for').hide();
            $('#reg_sem').hide();
            
        }
        
        $('select[name="do_invoice"]').on('change', function() {
            if ($('select[name="do_invoice"]').val() == 'Yes') {
                $('#inputCompany').show();
                $('#inputVat').show();
                $('#stud_company').show();
                $('#vat_number').show();
                $(document).find('#vatNumber').parents('.form-group').show()
                $(document).find('#company').parents('.form-group').show()

            } else {
                $('#inputCompany').hide();
                $('#inputVat').hide();
                $('#stud_company').hide();
                $('#vat_number').hide();
                $(document).find('#vatNumber').parents('.form-group').hide()
                $(document).find('#company').parents('.form-group').hide()
            }
        });

        $('input[type=radio][name=pm_id]').change(function() {
            if ($(this).attr('data-provider') == 'transfer'){
                $('.shop_invoice').show()
                var do_invoice = $('input[type=radio][name=shop_do_invoice]:checked').val()
                if(do_invoice == 'yes'){
                    $('.shop_company_div').show()
                    $('.shop_vat_div').show()
                }
                else{
                    $('.shop_company_div').hide()
                    $('.shop_vat_div').hide()
                }
              }
              else{
                $('.shop_invoice').hide()
                $('.shop_company_div').hide()
                $('.shop_vat_div').hide()
            }
        });

        $('input[type=radio][name=shop_do_invoice]').change(function() {
            if (this.value == 'yes'){
                $('.shop_company_div').show()
                $('.shop_vat_div').show()
              }
              else{
                $('.shop_company_div').hide()
                $('.shop_vat_div').hide()
            }
        });

        $('select[id="professional_body"]').on('change', function() {
            if ($('select[id="professional_body"]').val() == '') {
                $('#reg_campus_info').hide();
                $('#reg_campus').hide();
                $('#reg_enrol_for').hide();
                $('#reg_sem').hide();
            } else {
                $('#reg_campus_info').show();
                $('#reg_campus').show();
                $('#reg_enrol_for').show();
                $('#reg_sem').show();
            }
            profbody_campus_sem($(this).val())
        });

        if ($(document).find("#EmailAddress").css("display") != 'none') {
            $("#EmailAddress").keyup(function() {
                var text = $("#EmailAddress").val();
                if (text.length >= 1) {
                    document.getElementById("stdnumbr").style.display = 'none';
                    document.getElementById("Studentnumber").required = false;
                } else {
                    document.getElementById("stdnumbr").style.display = 'table-row';
                    document.getElementById("Studentnumber").required = true;
                }
            });
        }

        $('#contactus_recaptcha').on('submit', function(e) {

            var response = grecaptcha.getResponse();
            if (response.length == 0) {
                $('.g-recaptcha').css('border', '1px solid red');
                e.preventDefault();
                $('button[type="submit"]').removeAttr('disabled');
            }
        });
        ///        grecaptcha.ready(function() {
        //            grecaptcha.execute('6Ld_voIUAAAAAPPtBmHjiXkQOXQjLilUcVY2aLg8', {action: 'action_name'})
        //            .then(function(token) {
        //            // Verify the token on the server.
        //            });
        //        });

        if ($('.selectdiv').length) {
            var state_options = $("select[name='inputState']:enabled option:not(:first)");
            $('.selectdiv').on('change', "select[name='country_id']", function() {
                var select = $("select[name='inputState']");
                state_options.detach();
                var displayed_state = state_options.filter("[data-country_id=" + ($(this).val() || 0) + "]");
                var nb = displayed_state.appendTo(select).show().size();
                select.parent().toggle(nb >= 1);
                if (nb <= 0){
                    $('.country_class').addClass("hidden");
                    }
                    else if( nb >= 1){
                    if ($('.country_class').hasClass('hidden'))
                    {
                    $('.country_class').removeClass('hidden')
                    }
                }
            });
            $('.selectdiv').find("select[name='country_id']").change();
        }

        if ($(document).find("#Studentnumber").css("display") != 'none') {
            $("#Studentnumber").keyup(function() {
                var text = $("#Studentnumber").val();
                if (text.length >= 1) {
                    document.getElementById("emailadd").style.display = 'none';
                    document.getElementById("EmailAddress").required = false;
                } else {
                    document.getElementById("emailadd").style.display = 'table-row';
                    document.getElementById("EmailAddress").required = false;
                }
            });
        }

        $('input[id="btn_email"]').on('click', function(ev) {
            var email_id = $(document).find('#EmailAddress').val()
            if (!email_id) {
                document.getElementById("EmailAddress").required = true;
                alert('Please enter your email id')
            } else {
                var current = $(this);
                var id = current.attr('data-id');
                ajax.jsonRpc("/check_email", 'call', {
                    'email': email_id
                }).then(
                    function(result) {
                        if (result == true) {
                            document.getElementById("email_msg").innerText = 'Success';
                        } else {
                            $(document).find("[data-id=" + id + "]").each(function() {
                                if ($(this).hasClass('check_set')) {
                                    if ($('#EmailAddress').val()) {
                                        $(this).attr('checked', false);
                                        $('#EmailAddress').val('')
                                        document.getElementById("EmailAddress").disabled = true;
                                        document.getElementById("btn_email").disabled = true;
                                        var value = $(this)[0].value
                                        total_discount_minus = document.getElementById('total_discount_count').innerText;
                                        var discount_count = 0.0;
                                        var chkArray = [];
                                        var discount_id = []
                                        $(".chk:checked").each(function(ev) {
                                            chkArray.push($(this).val());
                                            discount_id.push(parseInt($(this).attr('discount-data-id')))
                                        });
                                        for (var i = 0; i < chkArray.length; i++) {
                                            discount_count += parseFloat(chkArray[i], 10); //don't forget to add the base
                                        }
                                        ajax.jsonRpc("/max_discount_ready", 'call', {
                                            'discount': discount_id
                                        }).then(
                                            function(result) {
                                                if (parseFloat(result['discount']) < discount_count) {
                                                    var aftre_minus = document.getElementById('total_discount_count').innerText = result['discount'];
                                                    var input_discount_val = $('#discount_val').val();
                                                    var input_value = $('#discount_val').val(parseFloat(aftre_minus))
                                                } else {
                                                    var aftre_minus = document.getElementById('total_discount_count').innerText = discount_count;
                                                    var input_discount_val = $('#discount_val').val();
                                                    var input_value = $('#discount_val').val(parseFloat(aftre_minus))
                                                }
                                            });
                                    }
                                }
                            });
                            document.getElementById("email_msg").innerText = 'You DO NOT qualify for the Returning Student Discount';
                        }
                    });
            }

        });


        $('input[id="btn-stdnumbr"]').on('click', function(ev) {
            var std_numbr = $(document).find('#Studentnumber').val()
            if (!std_numbr) {
                document.getElementById("EmailAddress").required = true;
                alert('Please enter student number')
            } else {
                var current = $(this);
                var id = current.attr('data-id');
                ajax.jsonRpc("/check_number", 'call', {
                    'number': std_numbr
                }).then(function(result) {
                    if (result == true) {
                        document.getElementById("number_msg").innerText = 'Success';
                    } else {
                        $(document).find("[data-id=" + id + "]").each(function() {
                            if ($(this).hasClass('check_set')) {
                                if ($('#Studentnumber').val()) {
                                    $(this).attr('checked', false);
                                    $('#Studentnumber').val('')
                                    document.getElementById("Studentnumber").disabled = true;
                                    document.getElementById("btn-stdnumbr").disabled = true;
                                    var value = $(this)[0].value
                                    total_discount_minus = document.getElementById('total_discount_count').innerText;
                                    var discount_count = 0.0;
                                    var chkArray = [];
                                    var discount_id = []
                                    $(".chk:checked").each(function(ev) {
                                        chkArray.push($(this).val());
                                        discount_id.push(parseInt($(this).attr('discount-data-id')))
                                    });
                                    for (var i = 0; i < chkArray.length; i++) {
                                        discount_count += parseFloat(chkArray[i], 10); //don't forget to add the base
                                    }
                                    ajax.jsonRpc("/max_discount_ready", 'call', {
                                        'discount': discount_id
                                    }).then(
                                        function(result) {
                                            if (parseFloat(result['discount']) < discount_count) {
                                                var aftre_minus = document.getElementById('total_discount_count').innerText = result['discount'];
                                                var input_discount_val = $('#discount_val').val();
                                                var input_value = $('#discount_val').val(parseFloat(aftre_minus))
                                            } else {
                                                var aftre_minus = document.getElementById('total_discount_count').innerText = discount_count;
                                                var input_discount_val = $('#discount_val').val();
                                                var input_value = $('#discount_val').val(parseFloat(aftre_minus))
                                            }
                                        });

                                }
                            }
                        });
                        document.getElementById("number_msg").innerText = 'You DO NOT qualify for the Returning Student Discount';
                    }
                });
            }
        });

        $('button[id="reg_and_enrll"]').on('click', function(ev) {
            ajax.jsonRpc("/reg_enroll", 'call').then(
                function(result) {
                    if (result) {
                        window.location.href = '/prof_body_form_render'
                    }
                });
        });

        $('button[id="free_quote_email"]').on('click', function(ev) {
            ajax.jsonRpc("/free_quote", 'call').then(
                function(result) {
                    if (result) {
                        window.location.href = '/prof_body_form_render'
                    }
                });
        });

        $('button[id="btn_get_free_email"]').on('click', function(ev) {
            var grand_tot = $('#grand_tot_val').find('.oe_currency_value').text()
            var product_tot = $('#product_total').find('.oe_currency_value').text()
            $(document).find('#product_total')
            ajax.jsonRpc("/get_free_email", 'call', {
                'grand_tot': grand_tot,
                'product_tot': product_tot
            }).then(
                function(result) {
                    if (result) {
                        window.location.href = '/enrolment_reg'
                    }
                });
        });

        $('button[id="btn_reg_enroll"]').on('click', function(ev) {
            var grand_tot = $('#grand_tot_val').find('.oe_currency_value').text()
            var product_tot = $('#product_total').find('.oe_currency_value').text()
            ajax.jsonRpc("/registration", 'call', {
                'grand_tot': grand_tot,
                'product_tot': product_tot
            }).then(
                function(result) {
                    if (result) {
                        window.location.href = '/registration_form'
                    }
                });
        });

        $('button[id="check_event"]').on('click', function(ev) {
            if ($('.event_course:checked').length == 0) {
                if (confirm("Are You Sure Continue")) {} else {
                    ev.preventDefault()
                    return false
                }
            }
        });

        $('button[id="back_button"]').on('click', function(ev) {
            history.back();
        });

        $(function() {
            $("#datepicker").datepicker({
                dateFormat: 'mm/dd/yy',
                changeMonth: true,
                changeYear: true,
                yearRange: '-100y:c+nn',
                maxDate: '-1d'
            });

            $(document).find('select[id="inputwarehouse"]').change()

            $(document).find('select[name="do_invoice"]').change()


            $('input[type="checkbox"]').on('change', function() {
                $('input[data-id="' + $(this).data('id') + '"]').not(this).prop('checked', false);
            });

            if (window.location.pathname == '/prof_body_form_render') {
                profbody_campus_sem($('#professional_body').val())
            }
            var discount_count = 0.0;
            var chkArray = [];
            var discount_id = []

            $(".chk:checked").each(function(ev) {
                chkArray.push($(this).val());
                discount_id.push(parseInt($(this).attr('discount-data-id')))
            });
            for (var i = 0; i < chkArray.length; i++) {
                discount_count += parseFloat(chkArray[i], 10); //don't forget to add the base
            }
            ajax.jsonRpc("/max_discount_ready", 'call', {
                'discount': discount_id
            }).then(
                function(result) {
                    if (parseFloat(result['discount']) > 0) {
                        if (parseFloat(result['discount']) < parseFloat(discount_count)) {
                            $("#total_discount_count").text("");
                            $("#total_discount_count").text(result['discount']);
                            $('#discount_val').val(result['discount']);
                        } else {
                            $("#total_discount_count").text("");
                            $("#total_discount_count").text(discount_count);
                            $('#discount_val').val(discount_count);
                        }
                    } else {
                        $("#total_discount_count").text("");
                        $("#total_discount_count").text(discount_count);
                        $('#discount_val').val(discount_count);
                    }
                });

            if ($('#mandate_link').val() == "") {
                var input_per = $("#inputPaypercentage").val();
                var total_amount = $(document).find('#totalamount').val();
                var due_amount = (parseFloat(total_amount) * parseFloat(input_per)) / 100;
                $("#inputTotalDue").val(due_amount.toFixed(2));
                var out_standing = (parseFloat(total_amount) - parseFloat(due_amount));
                $("#inputOutstanding").val(out_standing.toFixed(2));
                var payment_month = $("#inputPaymonths").val();
                var interest = $('#inputPaymonths option:selected').attr('data-interest')
                if (interest > 0) {
                    var tax_amount = (parseFloat(out_standing) * parseFloat(interest)) / 100;
                    var payment_with_tax = parseFloat(out_standing) + parseFloat(tax_amount);
                    var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                    $("#inputInterest").val(tax_amount.toFixed(2));
                    $("#inputtotalandInterest").val(payment_with_tax.toFixed(2));
                    $("#inputpaymentpermonth").val(per_mnth_payment.toFixed(2));
                } else {
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    $("#inputInterest").val('0.00');
                    $("#inputtotalandInterest").val(out_standing_amount);
                    var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                    $("#inputpaymentpermonth").val(per_mnth_payment.toFixed(2));
                }
            }

        });

        $('select[id="inputPaydate"]').on('change', function() {
            var date_day = document.getElementById("inputPaydate").value;
            if (date_day < 9) {
                var date_day = '0' + date_day
            }
            var d = new Date();
            var m = d.getMonth();
            var y = d.getFullYear();
            var newmonth = m + 2;
            if (newmonth < 9) {
                var newmonth = '0' + newmonth
            }
            $('#inputnextdodate').val(date_day + '/' + newmonth + '/' + y)
        });

        $('select[id="inputBankName"]').on('change', function() {
            var bank_name = document.getElementById("inputBankName").value;
            var bank_name = document.getElementById("inputBCode").value = bank_name;
        });
//        if($(document).find('select[id="inputwarehouse"]').length != 0){
//        $(document).find('select[id="inputwarehouse"]').change()
//        }

        $('select[id="inputwarehouse"]').on('change', function() {
            var warehouse = $("#inputwarehouse").val();
            var product_id = $(".product_id").val();
            ajax.jsonRpc("/check_product_stock", 'call', {
                'warehouse_id': warehouse,
                'product_id': product_id
            }).then(
                function(result) {
                    if(result.product_stock_qty >= 1){
                        $('.product_out_of_stock').hide()
                        $('.product_in_stock').show()
                        if (result.product_stock_qty <= 5){
                            $(document).find('span[class="product_qty"]').html('').html('Available Quantity: '+ result.product_stock_qty)
                        }
                    }
                    else
                    {
                        $('.product_in_stock').hide()
                        $('.product_out_of_stock').show()
                        $(document).find('span[class="product_qty"]').html('')
                    }
                });
        });


        $('select[id="inputPaypercentage"]').on('change', function() {
            var input_per = $("#inputPaypercentage").val();
            if (parseInt(input_per) == 100) {
                $("select[id='inputPaymonths'] option").hide();
                $('#inputPaymonths').append('<option value="0" selected="selected">0 Month</option>')
                $('#debit_order_section').hide();
                $('#inputRemittancefee').prop("disabled", true);
                $('#totalamount').prop("disabled", false);
                $('#inputTotalDue').prop("disabled", true);
                $('#inputOutstanding').prop("disabled", true);
                $('#inputInterest').prop("disabled", true);
                $('#inputtotalandInterest').prop("disabled", true);
                $('#inputpaymentpermonth').prop("disabled", true);
                $('#inputPaymonths').prop("disabled", true);
                $('#debitrequiredcheckbox').prop("required", false);
                $('#inputAccount').prop("required", false);
                var total_amount = $(document).find('#totalamount').val();
                var due_amount = (parseFloat(total_amount) * parseFloat(input_per)) / 100;
                document.getElementById("inputTotalDue").value = due_amount.toFixed(2);
                var out_standing = (parseFloat(total_amount) - parseFloat(due_amount.toFixed(2)));
                document.getElementById("inputOutstanding").value = out_standing.toFixed(2);
                var payment_month = $("#inputPaymonths").val();
                var interest = $('#inputPaymonths option:selected').attr('data-interest')
                if (interest > 0) {
                    var tax_amount = (parseFloat(out_standing) * parseFloat(interest)) / 100;
                    var payment_with_tax = parseFloat(out_standing) + parseFloat(tax_amount.toFixed(2));
                    var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                    document.getElementById("inputInterest").value = parseFloat(tax_amount.toFixed(2));
                    document.getElementById("inputtotalandInterest").value = parseFloat(payment_with_tax.toFixed(2));
                    document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
                } else {
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    document.getElementById("inputInterest").value = '0.0';
                    document.getElementById("inputtotalandInterest").value = parseFloat(out_standing_amount);
                    var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                    if (per_mnth_payment >= 0) {
                        document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
                    } else {
                        document.getElementById("inputpaymentpermonth").value = 0.0;
                    }
                }
            } else {
            	$('#debitrequiredcheckbox').prop("required", true);
                $('#debit_order_section').show();
                $('#inputRemittancefee').prop("disabled", false);
                $('#totalamount').prop("disabled", false);
                $('#inputTotalDue').prop("disabled", false);
                $('#inputOutstanding').prop("disabled", false);
                $('#inputInterest').prop("disabled", false);
                $('#inputtotalandInterest').prop("disabled", false);
                $('#inputpaymentpermonth').prop("disabled", false);
                $('#inputPaymonths').prop("disabled", false);
                $("select[id='inputPaymonths'] option").show();
                $("#inputPaymonths option[value='0']").remove();
                var total_amount = $(document).find('#totalamount').val();
                var due_amount = (parseFloat(total_amount) * parseFloat(input_per)) / 100;
                document.getElementById("inputTotalDue").value = due_amount.toFixed(2);
                var out_standing = (parseFloat(total_amount) - parseFloat(due_amount.toFixed(2)));
                document.getElementById("inputOutstanding").value = out_standing.toFixed(2);
                var payment_month = $("#inputPaymonths").val();
                var interest = $('#inputPaymonths option:selected').attr('data-interest')
                if (interest > 0) {
                    var tax_amount = (parseFloat(out_standing) * parseFloat(interest)) / 100;
                    var payment_with_tax = parseFloat(out_standing) + parseFloat(tax_amount.toFixed(2));
                    var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                    document.getElementById("inputInterest").value = tax_amount.toFixed(2);
                    document.getElementById("inputtotalandInterest").value = payment_with_tax.toFixed(2);
                    document.getElementById("inputpaymentpermonth").value = per_mnth_payment.toFixed(2);
                } else {
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    document.getElementById("inputInterest").value = '0.0';
                    document.getElementById("inputtotalandInterest").value = parseFloat(out_standing_amount);
                    var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                    document.getElementById("inputpaymentpermonth").value = per_mnth_payment.toFixed(2);
                }
            }
        });

        $('select[id="inputPaymonths"]').on('change', function() {
            var current = $(this);
            var payment_month = $("#inputPaymonths").val();
            var interest = $('#inputPaymonths option:selected').attr('data-interest')
            if (interest > 0) {
                var out_standing_amount = $(document).find('#inputOutstanding').val();
                var tax_amount = (parseFloat(out_standing_amount) * parseFloat(interest)) / 100;
                var payment_with_tax = parseFloat(out_standing_amount) + parseFloat(tax_amount);
                var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                document.getElementById("inputInterest").value = tax_amount.toFixed(2);
                document.getElementById("inputtotalandInterest").value = payment_with_tax.toFixed(2);
                document.getElementById("inputpaymentpermonth").value = per_mnth_payment.toFixed(2);
            } else {
                var out_standing_amount = $(document).find('#inputOutstanding').val();
                document.getElementById("inputInterest").value = '0.0';
                document.getElementById("inputtotalandInterest").value = parseFloat(out_standing_amount);
                var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                document.getElementById("inputpaymentpermonth").value = per_mnth_payment.toFixed(2);
            }
        });
        setTimeout(function(){
        	$(document).find('input[id="inputNoRemittance"]').click();
            $(document).find('input[id="inputNoRemittance"]').click();
        },1000)
        $('input[id="inputNoRemittance"]').on('click', function(ev) {
            $(".remove_fee:not(:checked)").each(function(ev) {
                document.getElementById("inputRemittancefee").value = sessionStorage.getItem('rem_fee')
                var rem_fee = $(document).find("#inputRemittancefee").val()
                var total_amount = $(document).find('#grand_total_amount')[0].innerHTML;
                var add_total_amount = parseFloat(total_amount) + parseFloat(rem_fee)
                document.getElementById("totalamount").value = add_total_amount.toFixed(2)
                var add_total_amount = $(document).find('#totalamount')[0].value;
                var input_per = document.getElementById('inputPaypercentage').value;
                var due_amount = (parseFloat(add_total_amount) * parseFloat(input_per)) / 100;
                var payment_month = $("#inputPaymonths").val();
                document.getElementById("inputTotalDue").value = due_amount.toFixed(2);
                var out_standing = (parseFloat(add_total_amount) - parseFloat(due_amount));
                document.getElementById("inputOutstanding").value = out_standing.toFixed(2);
                var interest = $('#inputPaymonths option:selected').attr('data-interest');

                if (interest > 0) {
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    var tax_amount = (parseFloat(out_standing_amount) * parseFloat(interest)) / 100;
                    var payment_with_tax = parseFloat(out_standing_amount) + parseFloat(tax_amount);
                    var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                    document.getElementById("inputInterest").value = tax_amount.toFixed(2);
                    document.getElementById("inputtotalandInterest").value = payment_with_tax.toFixed(2);
                    document.getElementById("inputpaymentpermonth").value = per_mnth_payment.toFixed(2);
                } else {
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    document.getElementById("inputInterest").value = '0.0';
                    document.getElementById("inputtotalandInterest").value = parseFloat(out_standing_amount);
                    var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                    document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
                }
            });

            $(".remove_fee:checked").each(function(ev) {
                var rem_fee = $(document).find("#inputRemittancefee").val()
                sessionStorage.setItem("rem_fee", rem_fee);
                var total_amount = $(document).find('#grand_total_amount')[0].innerHTML;
                document.getElementById("totalamount").value = total_amount
                document.getElementById("inputRemittancefee").value = '0'
                var add_total_amount = $(document).find('#totalamount')[0].value;
                var input_per = document.getElementById('inputPaypercentage').value;
                var payment_month = $("#inputPaymonths").val();
                var due_amount = (parseFloat(add_total_amount) * parseFloat(input_per)) / 100;
                document.getElementById("inputTotalDue").value = due_amount.toFixed(2);
                var out_standing = (parseFloat(add_total_amount) - parseFloat(due_amount));
                document.getElementById("inputOutstanding").value = out_standing.toFixed(2);
                var interest = $('#inputPaymonths option:selected').attr('data-interest')

                if (interest > 0) {
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    var tax_amount = (parseFloat(out_standing_amount) * parseFloat(interest)) / 100;
                    var payment_with_tax = parseFloat(out_standing_amount) + parseFloat(tax_amount);
                    var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                    document.getElementById("inputInterest").value = tax_amount.toFixed(2);
                    document.getElementById("inputtotalandInterest").value = payment_with_tax.toFixed(2);
                    document.getElementById("inputpaymentpermonth").value = per_mnth_payment.toFixed(2);
                } else {
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    document.getElementById("inputInterest").value = '0.0';
                    document.getElementById("inputtotalandInterest").value = parseFloat(out_standing_amount);
                    var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                    document.getElementById("inputpaymentpermonth").value = per_mnth_payment.toFixed(2);
                }
            });
        });

        //      var $payment = $("#payment_method");
        //
        //      $payment.on("click", 'button[type="submit"],button[name="submit"]', function (ev) {
        //      ev.preventDefault();
        //      ev.stopPropagation();
        //      var $form = $(ev.currentTarget).parents('form');
        //      console.log('')
        //      var acquirer_id = $(ev.currentTarget).parents('div.oe_sale_acquirer_button').first().data('id');
        //      console.log('acquirer_id', acquirer_id)
        //      if (!$('#terms').is(':checked')){
        //        console.log('click')
        //        if ($('p#msg')){
        //        console.log('inside')
        //        $('p#msg').remove()
        //        }
        //        $('div p').append(' <p id="msg" style="color:red">Please accept Terms &amp; Conditions to continue')
        //        return false;
        //        }
        //
        //      if (! acquirer_id) {
        //        return false;
        //      }
        //      ajax.jsonRpc('/shop/payment/transaction/' + acquirer_id, 'call', {}).then(function (data) {
        //        $form.submit();
        //      });
        //   });

        $('input[id="discount_type_id"]').on('click', function(ev) {
            var discount_count = 0.0;
            var chkArray = [];
            var discount_id = []
            $(".chk:not(:checked)").each(function() {
                var current = $(this);
                var id = current.attr('data-id');
                $(document).find("[data-id=" + id + "]").each(function() {
                    if ($(this).hasClass('studentnumberprocess')) {
                        $(this).hide();
                        document.getElementById("EmailAddress").required = false;
                        document.getElementById("Studentnumber").required = false;
                        $('#number_msg').text('')
                        $('#email_msg').text('')
                    }
                });
            });
            $(".chk:checked").each(function(ev) {
                chkArray.push($(this).val());
                discount_id.push(parseInt($(this).attr('discount-data-id')))
                var current = $(this);
                var id = current.attr('data-id');
                $(document).find("[data-id=" + id + "]").each(function() {
                    if ($(this).hasClass('studentnumberprocess')) {
                        $(this).show();
                        $('#number_msg').text('')
                        $('#email_msg').text('')
                        document.getElementById("EmailAddress").required = true;
                        document.getElementById("Studentnumber").required = true;
                        document.getElementById("EmailAddress").disabled = false;
                        document.getElementById("btn_email").disabled = false;
                        document.getElementById("Studentnumber").disabled = false;
                        document.getElementById("btn-stdnumbr").disabled = false;
                    }
                });
            });
            for (var i = 0; i < chkArray.length; i++) {
                discount_count += parseFloat(chkArray[i], 10); //don't forget to add the base
            }
            ajax.jsonRpc("/max_discount", 'call', {
                'discount': discount_id
            }).then(
                function(result) {
                    if (parseFloat(result['discount']) > 0) {
                        if (parseFloat(result['discount']) < parseFloat(discount_count)) {
                            document.getElementById("total_discount_count").innerHTML = '';
                            document.getElementById("total_discount_count").innerHTML = result['discount'];
                            $('#discount_val').val(result['discount']);
                        } else {
                            document.getElementById("total_discount_count").innerHTML = '';
                            document.getElementById("total_discount_count").innerHTML = discount_count;
                            $('#discount_val').val(discount_count);
                        }
                    } else {
                        document.getElementById("total_discount_count").innerHTML = '';
                        document.getElementById("total_discount_count").innerHTML = discount_count;
                        $('#discount_val').val(discount_count);
                    }
                });
        });
    });
});
