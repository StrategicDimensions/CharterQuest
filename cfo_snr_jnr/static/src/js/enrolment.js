odoo.define('cfo_snr_jnr.enrolment', function (require) {
    var ajax = require('web.ajax');
    $(document).ready(function () {

        function profbody_campus_sem(data){
            ajax.jsonRpc("/get_event_data", 'call',
            {'professional_body': data}).then(
            function (result) {
                var select = document.getElementById("select_campus");
                select.options.length = 0;
                var select = document.getElementById("select_semester");
                select.options.length = 0;
                var locationoptions = "";
                for(var i = 0; i < result['location'].length; i++) {
                    locationoptions += "<option id='"+  result['location'][i]['id'] + "' value='" +  result['location'][i]['id'] + "'>" +  result['location'][i]['name'] + "</option>";
                }
                $( 'select[id="select_campus"]' ).append( locationoptions );

                var semesteroptions = "";
                for(var i = 0; i < result['semester'].length; i++) {
                    semesteroptions += "<option id='"+ result['semester'][i]['id'] + "' value='" + result['semester'][i]['id'] + "'>" + result['semester'][i]['name'] + "</option>";
                }
                $('select[id="select_semester"]').append(semesteroptions);
            });
        }

        $('select[id="professional_body"]').on('change', function () {
            profbody_campus_sem($(this).val())
        });

        if ($(document).find("#EmailAddress").css("display") != 'none'){
            $("#EmailAddress").keyup(function(){
                var text = $("#EmailAddress").val();
                if (text.length >= 1){
                    document.getElementById("stdnumbr").style.display = 'none';
                    document.getElementById("Studentnumber").required = false;
                }
                else{
                    document.getElementById("stdnumbr").style.display = 'table-row';
                    document.getElementById("Studentnumber").required = true;
                }
            });
         }


        if ($(document).find("#Studentnumber").css("display") != 'none'){
            $("#Studentnumber").keyup(function(){
                var text = $("#Studentnumber").val();
                if (text.length >= 1){
                     document.getElementById("emailadd").style.display = 'none';
                     document.getElementById("EmailAddress").required = false;
                }
                else{
                    document.getElementById("emailadd").style.display = 'table-row';
                    document.getElementById("EmailAddress").required = false;
                }
            });
        }

        $('input[id="btn_email"]').on('click', function (ev) {
            var email_id = $(document).find('#EmailAddress').val()
            if (! email_id){
              document.getElementById("EmailAddress").required = true;
              alert('Please enter your email id')
            }
            else{
                var current = $(this);
		    var id =current.attr('data-id');
            ajax.jsonRpc("/check_email", 'call',
                {'email': email_id}).then(
                function (result) {
                    if (result == true){
                        document.getElementById ("email_msg").innerText = 'Success';
                    }
                    else{
                        $(document).find("[data-id="+id+"]").each(function (){
                            if ($(this).hasClass('check_set')){
                                if ($('#EmailAddress').val()){
                                    $(this).attr('checked',false);
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
                                    for( var i = 0; i < chkArray.length; i++ ){
                                       discount_count  += parseFloat( chkArray[i], 10); //don't forget to add the base
                                    }
                                    ajax.jsonRpc("/max_discount_ready", 'call',{'discount': discount_id}).then(
                                    function (result) {
                                        if(parseFloat(result['discount']) < discount_count){
                                            var aftre_minus = document.getElementById('total_discount_count').innerText = result['discount'];
                                            var input_discount_val = $('#discount_val').val();
                                            var input_value = $('#discount_val').val(parseFloat(aftre_minus))
                                        }
                                        else{
                                            var aftre_minus = document.getElementById('total_discount_count').innerText = discount_count;
                                            var input_discount_val = $('#discount_val').val();
                                            var input_value = $('#discount_val').val(parseFloat(aftre_minus))
                                        }
                                    });
                                }
                            }
		                });
                        document.getElementById ("email_msg").innerText = 'You DO NOT qualify for the Returning Student Discount';
                    }
                });
            }

        });


        $('input[id="btn-stdnumbr"]').on('click', function (ev) {
            var std_numbr = $(document).find('#Studentnumber').val()
            if (! std_numbr){
                document.getElementById("EmailAddress").required = true;
                alert('Please enter student number')
            }
            else{
                var current = $(this);
                var id =current.attr('data-id');
                ajax.jsonRpc("/check_number", 'call',{'number': std_numbr}).then(function (result) {
                    if (result == true){
                        document.getElementById("number_msg").innerText = 'Success';
                    }
                    else{
                        $(document).find("[data-id="+id+"]").each(function (){
                            if ($(this).hasClass('check_set')){
                                if ($('#Studentnumber').val()){
                                    $(this).attr('checked',false);
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
                                    for( var i = 0; i < chkArray.length; i++ ){
                                       discount_count  += parseFloat( chkArray[i], 10); //don't forget to add the base
                                    }
                                    ajax.jsonRpc("/max_discount_ready", 'call',{'discount': discount_id}).then(
                                    function (result) {
                                        if(parseFloat(result['discount']) < discount_count){
                                            var aftre_minus = document.getElementById('total_discount_count').innerText = result['discount'];
                                            var input_discount_val = $('#discount_val').val();
                                            var input_value = $('#discount_val').val(parseFloat(aftre_minus))
                                        }
                                        else{
                                            var aftre_minus = document.getElementById('total_discount_count').innerText = discount_count;
                                            var input_discount_val = $('#discount_val').val();
                                            var input_value = $('#discount_val').val(parseFloat(aftre_minus))
                                        }
                                    });

                                }
                            }
                        });
                        document.getElementById ("number_msg").innerText = 'You DO NOT qualify for the Returning Student Discount';
                    }
                });
            }
        });

        $('button[id="btn_get_free_email"]').on('click', function (ev) {
            var grand_tot = $('#grand_tot_val').find('.oe_currency_value').text()
            var product_tot = $('#product_total').find('.oe_currency_value').text()
            $(document).find('#product_total')
            ajax.jsonRpc("/get_free_email", 'call', {'grand_tot': grand_tot, 'product_tot':product_tot}).then(
                function (result) {
                if (result){
                        window.location.href = '/enrolment_reg'
                    }
                });
        });

        $('button[id="btn_reg_enroll"]').on('click', function (ev) {
            var grand_tot = $('#grand_tot_val').find('.oe_currency_value').text()
            var product_tot = $('#product_total').find('.oe_currency_value').text()
            ajax.jsonRpc("/registration", 'call', {'grand_tot': grand_tot, 'product_tot':product_tot}).then(
                function (result) {
                    if (result){
                        window.location.href = '/registration_form'
                    }
                });
        });

        $('button[id="check_event"]').on('click', function (ev) {
            if($('.event_course:checked').length == 0){
                if (confirm("Are You Sure Continue")) {
                } else {
                    ev.preventDefault()
                    return false
                }
            }
        });

        $('button[id="back_button"]').on('click', function (ev) {
            history.back();
        });

        $(function() {
            $( "#datepicker" ).datepicker({
                dateFormat : 'mm/dd/yy',
                changeMonth : true,
                changeYear : true,
                yearRange: '-100y:c+nn',
                maxDate: '-1d'
            });

            $('input[type="checkbox"]').on('change', function() {
                $('input[data-id="' + $(this).data('id') + '"]').not(this).prop('checked', false);
            });

            if(window.location.pathname == '/prof_body_form_render'){
                profbody_campus_sem($('#professional_body').val())
            }
            var discount_count = 0.0;
            var chkArray = [];
            var discount_id = []

            $(".chk:checked").each(function(ev) {
		        chkArray.push($(this).val());
		        discount_id.push(parseInt($(this).attr('discount-data-id')))
	        });
	        for( var i = 0; i < chkArray.length; i++ ){
               discount_count  += parseFloat( chkArray[i], 10); //don't forget to add the base
            }
            ajax.jsonRpc("/max_discount_ready", 'call',{'discount': discount_id}).then(
            function (result) {
                if(parseFloat(result['discount']) > 0){
                    if(parseFloat(result['discount']) < parseFloat(discount_count)){
                        $("#total_discount_count").text("");
                        $("#total_discount_count").text(result['discount']);
                        $('#discount_val').val(result['discount']);
                    }
                    else{
                        $("#total_discount_count").text("");
                        $("#total_discount_count").text(discount_count);
                        $('#discount_val').val(discount_count);
                    }
                }
                else{
                        $("#total_discount_count").text("");
                        $("#total_discount_count").text(discount_count);
                        $('#discount_val').val(discount_count);
                    }
            });

            var input_per = $("#inputPaypercentage").val();
            var total_amount = $(document).find('#totalamount').val();
            var due_amount = (parseFloat(total_amount) * parseFloat(input_per)) /100;
            $("#inputTotalDue").val(parseFloat(due_amount.toFixed(2)));
            var out_standing = (parseFloat(total_amount) - parseFloat(due_amount));
            $("#inputOutstanding").val(parseFloat(out_standing.toFixed(2)));
            var payment_month = $("#inputPaymonths").val();
            var interest = $('#inputPaymonths option:selected').attr('data-interest')
            if (interest > 0){
                var tax_amount = (parseFloat(out_standing) * parseFloat(interest)) /100;
                var payment_with_tax = parseFloat(out_standing) + parseFloat(tax_amount);
                var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                $("#inputInterest").val(parseFloat(tax_amount.toFixed(2)));
                $("#inputtotalandInterest").val(parseFloat(payment_with_tax.toFixed(2)));
                $("#inputpaymentpermonth").val(parseFloat(per_mnth_payment.toFixed(2)));
            }
            else{
                var out_standing_amount = $(document).find('#inputOutstanding').val();
                $("#inputInterest").val('0.0');
                $("#inputtotalandInterest").val(parseFloat(out_standing_amount));
                var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                $("#inputpaymentpermonth").val(parseFloat(per_mnth_payment.toFixed(2)));
            }
        });

        $('select[id="inputPaydate"]').on('change', function(){
            var date_day = document.getElementById("inputPaydate").value;
            if (date_day < 9){
                var date_day = '0'+date_day
            }
            var d = new Date();
            var m = d.getMonth();
            var y = d.getFullYear();
            var newmonth = m + 2;
            if (newmonth < 9){
                var newmonth = '0'+newmonth
            }
            $('#inputnextdodate').val(date_day+'/'+newmonth + '/'+y)
        });

        $('select[id="inputBankName"]').on('change', function(){
            var bank_name = document.getElementById("inputBankName").value;
            var bank_name = document.getElementById("inputBCode").value = bank_name;
        });

        $('select[id="inputPaypercentage"]').on('change', function(){
            var input_per = $("#inputPaypercentage").val();
            if (parseInt(input_per) == 100){
                $("select[id='inputPaymonths'] option").hide();
                $('#inputPaymonths').append('<option value="0" selected="selected">0 Month</option>')
                $('#debit_order_section').hide();
                $('#inputRemittancefee').prop("disabled", true);
                $('#totalamount').prop("disabled", true);
                $('#inputTotalDue').prop("disabled", true);
                $('#inputOutstanding').prop("disabled", true);
                $('#inputInterest').prop("disabled", true);
                $('#inputtotalandInterest').prop("disabled", true);
                $('#inputpaymentpermonth').prop("disabled", true);
                $('#inputPaymonths').prop("disabled", true);
                var total_amount = $(document).find('#totalamount').val();
                var due_amount = (parseFloat(total_amount) * parseFloat(input_per)) /100;
                document.getElementById("inputTotalDue").value = parseFloat(due_amount.toFixed(2));
                var out_standing = (parseFloat(total_amount) - parseFloat(due_amount.toFixed(2)));
                document.getElementById("inputOutstanding").value = parseFloat(out_standing.toFixed(2));
                var payment_month = $("#inputPaymonths").val();
                var interest = $('#inputPaymonths option:selected').attr('data-interest')
                if (interest > 0){
                    var tax_amount = (parseFloat(out_standing) * parseFloat(interest)) /100;
                    var payment_with_tax = parseFloat(out_standing) + parseFloat(tax_amount.toFixed(2));
                    var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                    document.getElementById("inputInterest").value = parseFloat(tax_amount.toFixed(2));
                    document.getElementById("inputtotalandInterest").value = parseFloat(payment_with_tax.toFixed(2));
                    document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
                }
                else{
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    document.getElementById("inputInterest").value = '0.0';
                    document.getElementById("inputtotalandInterest").value = parseFloat(out_standing_amount);
                    var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                    if (per_mnth_payment >= 0){
                        document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
                    }
                    else{
                    document.getElementById("inputpaymentpermonth").value = 0.0;
                    }
                }
            }
            else{
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
                var due_amount = (parseFloat(total_amount) * parseFloat(input_per)) /100;
                document.getElementById("inputTotalDue").value = parseFloat(due_amount.toFixed(2));
                var out_standing = (parseFloat(total_amount) - parseFloat(due_amount.toFixed(2)));
                document.getElementById("inputOutstanding").value = parseFloat(out_standing.toFixed(2));
                var payment_month = $("#inputPaymonths").val();
                var interest = $('#inputPaymonths option:selected').attr('data-interest')
                if (interest > 0){
                    var tax_amount = (parseFloat(out_standing) * parseFloat(interest)) /100;
                    var payment_with_tax = parseFloat(out_standing) + parseFloat(tax_amount.toFixed(2));
                    var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                    document.getElementById("inputInterest").value = parseFloat(tax_amount.toFixed(2));
                    document.getElementById("inputtotalandInterest").value = parseFloat(payment_with_tax.toFixed(2));
                    document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
                }
                else{
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    document.getElementById("inputInterest").value = '0.0';
                    document.getElementById("inputtotalandInterest").value = parseFloat(out_standing_amount);
                    var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                    document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
                }
            }
        });

        $('select[id="inputPaymonths"]').on('change', function(){
            var current = $(this);
            var payment_month = $("#inputPaymonths").val();
            var interest = $('#inputPaymonths option:selected').attr('data-interest')
            if (interest > 0){
                var out_standing_amount = $(document).find('#inputOutstanding').val();
                var tax_amount = (parseFloat(out_standing_amount ) * parseFloat(interest)) /100;
                var payment_with_tax = parseFloat(out_standing_amount) + parseFloat(tax_amount);
                var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                document.getElementById("inputInterest").value = parseFloat(tax_amount.toFixed(2));
                document.getElementById("inputtotalandInterest").value = parseFloat(payment_with_tax.toFixed(2));
                document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
            }
            else{
                var out_standing_amount = $(document).find('#inputOutstanding').val();
                document.getElementById("inputInterest").value = '0.0';
                document.getElementById("inputtotalandInterest").value = parseFloat(out_standing_amount);
                var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
            }
        });

        $('input[id="inputNoRemittance"]').on('click', function (ev) {
            $(".remove_fee:not(:checked)").each(function(ev) {
		        document.getElementById("inputRemittancefee").value = sessionStorage.getItem('rem_fee')
		        var rem_fee = $(document).find("#inputRemittancefee").val()
		        var total_amount = $(document).find('#grand_total_amount')[0].innerHTML;
		        document.getElementById("totalamount").value = parseFloat(total_amount) + parseFloat(rem_fee)
		        var add_total_amount = $(document).find('#totalamount')[0].value;
                var input_per = document.getElementById('inputPaypercentage').value;
                var due_amount = (parseFloat(add_total_amount) * parseFloat(input_per)) /100;
                var payment_month = $("#inputPaymonths").val();
                document.getElementById("inputTotalDue").value = parseFloat(due_amount.toFixed(2));
                var out_standing = (parseFloat(add_total_amount) - parseFloat(due_amount));
                document.getElementById("inputOutstanding").value = parseFloat(out_standing.toFixed(2));
                var interest = $('#inputPaymonths option:selected').attr('data-interest');

                if (interest > 0){
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    var tax_amount = (parseFloat(out_standing_amount ) * parseFloat(interest)) /100;
                    var payment_with_tax = parseFloat(out_standing_amount) + parseFloat(tax_amount);
                    var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                    document.getElementById("inputInterest").value = parseFloat(tax_amount.toFixed(2));
                    document.getElementById("inputtotalandInterest").value = parseFloat(payment_with_tax.toFixed(2));
                    document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
                    }
                else{
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
		        var due_amount = (parseFloat(add_total_amount) * parseFloat(input_per)) /100;
                document.getElementById("inputTotalDue").value = parseFloat(due_amount.toFixed(2));
                var out_standing = (parseFloat(add_total_amount) - parseFloat(due_amount));
                document.getElementById("inputOutstanding").value = parseFloat(out_standing.toFixed(2));
                var interest = $('#inputPaymonths option:selected').attr('data-interest')

                if (interest > 0){
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    var tax_amount = (parseFloat(out_standing_amount ) * parseFloat(interest)) /100;
                    var payment_with_tax = parseFloat(out_standing_amount) + parseFloat(tax_amount);
                    var per_mnth_payment = parseFloat(payment_with_tax) / parseFloat(payment_month);
                    document.getElementById("inputInterest").value = parseFloat(tax_amount.toFixed(2));
                    document.getElementById("inputtotalandInterest").value = parseFloat(payment_with_tax.toFixed(2));
                    document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
                    }
                else{
                    var out_standing_amount = $(document).find('#inputOutstanding').val();
                    document.getElementById("inputInterest").value = '0.0';
                    document.getElementById("inputtotalandInterest").value = parseFloat(out_standing_amount);
                    var per_mnth_payment = parseFloat(out_standing_amount) / parseFloat(payment_month)
                    document.getElementById("inputpaymentpermonth").value = parseFloat(per_mnth_payment.toFixed(2));
                }
	        });
        });

        $('input[id="discount_type_id"]').on('click', function (ev) {
            var discount_count = 0.0;
            var chkArray = [];
            var discount_id = []
            $(".chk:not(:checked)").each(function() {
                var current = $(this);
		        var id =current.attr('data-id');
		        $(document).find("[data-id="+id+"]").each(function (){
                    if ($(this).hasClass('studentnumberprocess')){
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
		        var id =current.attr('data-id');
		        $(document).find("[data-id="+id+"]").each(function (){
                    if ($(this).hasClass('studentnumberprocess')){
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
	        for( var i = 0; i < chkArray.length; i++ ){
               discount_count  += parseFloat( chkArray[i], 10); //don't forget to add the base
            }
            ajax.jsonRpc("/max_discount", 'call',{'discount': discount_id}).then(
            function (result) {
                if(parseFloat(result['discount']) > 0){
                    if(parseFloat(result['discount']) < parseFloat(discount_count)){
                        document.getElementById("total_discount_count").innerHTML = '';
                        document.getElementById("total_discount_count").innerHTML = result['discount'];
                        $('#discount_val').val(result['discount']);
                    }
                    else{
                        document.getElementById("total_discount_count").innerHTML = '';
                        document.getElementById("total_discount_count").innerHTML = discount_count;
                        $('#discount_val').val(discount_count);
                    }
                }
                else{
                        document.getElementById("total_discount_count").innerHTML = '';
                        document.getElementById("total_discount_count").innerHTML = discount_count;
                        $('#discount_val').val(discount_count);
                    }
            });
        });
    });
});