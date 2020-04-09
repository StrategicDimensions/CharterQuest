odoo.define('cfo_snr_jnr.pc_exam', function(require){
    var ajax = require('web.ajax');



    $(document).ready(function() {

        var availableDates = [];

        var sale_order = $(document).find('#sale_order_id').val();
        var event = $(document).find('#event_id').val();
        if (sale_order && event){
            var level = $(document).find('#select_pc_exam_level').val();
            var campus = $(document).find('#campus').val();
            var exam_type = $(document).find('#select_exam_type').val();
            var e = document.getElementById("select_pc_exam_subject");
            var sub = e.options[e.selectedIndex].text;
            console.log("\n\n\n\n==============call=====e====sub===",e,sub);
            var subject = sub;
            console.log("\n\n\n\n\n=========valu subjet,campus=============",level,subject,campus,exam_type)
            ajax.jsonRpc("/pc_exam_date_search", 'call', {
                'level': level,
                'subject':subject,
                'campus':campus,
                'exam_type':exam_type,
                'sale_order':sale_order,
                'event_id':event,
            }).then(
                function(result) {
                    console.log("\n\n\n\n\n=========daate result==============",result)
                    if (result) {
                         availableDates = [];
                         for(var i=0;i<result.length;i++)
                         {
                             availableDates.push(result[i]);
                         }
                         console.log("\n\n\n\n\n=========availableDates result==============",availableDates)
                         $('#exam_datepicker').val("");
                    }
                });
           $('.exam_search').attr("disabled", false);
        }
        $('#select_pc_exam_subject').change(function(){
            var level_value = $(document).find('#select_pc_exam_level').val();
            var subject_value = $(document).find('#select_pc_exam_subject').val();

            var campus_value = $(document).find('#campus').val();
            var exam_type_value = $(document).find('#select_exam_type').val();
//            document.getElementById("load1").style.display = "block";
            console.log("\n\n\n\n\n=========valu subjet,campus=============",level_value,subject_value,campus_value,exam_type_value)
            ajax.jsonRpc("/pc_exam_date_search", 'call', {
                'level': level_value,
                'subject':subject_value,
                'campus':campus_value,
                'exam_type':exam_type_value,
            }).then(
                function(result) {
                    console.log("\n\n\n\n\n=========daate result==============",result)
                    if (result) {
                         availableDates = [];
                         for(var i=0;i<result.length;i++)
                         {
                             availableDates.push(result[i]);
                         }
                         console.log("\n\n\n\n\n=========availableDates result==============",availableDates)
                         $('#exam_datepicker').val("");
                    }
                });

           $('.exam_search').attr("disabled", false);

        });

        var exam_date = new Date();
        exam_date.setDate(exam_date.getDate()+7);



//        var availableDates = ["9-5-2020","14-5-2020","15-5-2020"];

        function available(date) {
          dmy = date.getDate() + "-" + (date.getMonth()+1) + "-" + date.getFullYear();
          if ($.inArray(dmy, availableDates) != -1) {
            return true;
          } else {
            return false;
          }
        }

        $('button[id="pc_exam_booking"]').on('click', function(ev) {
            window.location.href = '/registerPB'
        });
        var select_exam_price = 0.0;
        var voucher_list = [];
        var event_ids = [];

        $('#exam_datepicker').datepicker({
            startDate: exam_date,
//            daysOfWeekDisabled: [0,6],
            beforeShowDay: available
        });

        $('#select_pc_exam_level').change(function(){

            var level_value = $(document).find('#select_pc_exam_level').val();
            var campus_value = $(document).find('#campus').val();
            var exam_type_value = $(document).find('#select_exam_type').val();
//            document.getElementById("load").style.display = "block";
            ajax.jsonRpc("/pc_exam_subject_search", 'call', {
                'level': level_value,
                'campus':campus_value,
                'exam_type':exam_type_value,
            }).then(
                function(result) {
                    if (result['subjects']) {
                         var select = document.getElementById("select_pc_exam_subject");
                         var subject = [];
                         select.options.length = 0;
                         for(var i=0;i<=result['subjects'].length;i++)
                         {
                            subject.push(result['subjects'][i]);
                            select.options[select.options.length] = new Option(subject[i-1], result['subjects'][i-1]);
                         }
                    }
                    if (result['dates'])
                    {
                        availableDates = [];
                        for(var i=0;i<result['dates'].length;i++)
                         {
                             availableDates.push(result['dates'][i]);
                         }
                         $('#exam_datepicker').val("");
                         console.log("\n\n\n\n\n=========availableDates result['dates']==============",availableDates)
                    }
                });

            $('.exam_search').attr("disabled", false);
        });

        $('#exam_datepicker').click(function ()
        {
            $('.exam_search').attr("disabled", false);
        });

        var dob_date = new Date();
        dob_date.setDate(dob_date.getDate());
        $('input[name="DOB"]').datepicker({
        endDate: dob_date
        });

        $(".exam_date_validation").on('click', function (event) {
            var date_exam = $(document).find('#exam_datepicker').val();
            if (!date_exam) {
                event.preventDefault()
                alert('Date OF Exam Must Be Required');
            }

        });

        if ($('.selectdiv').length) {
            var state_options = $("select[name='inputexamState']:enabled option");

            $('.selectdiv').on('change', "select[name='exam_country_id']", function() {
                var select = $("select[name='inputexamState']");
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
            $('.selectdiv').find("select[name='exam_country_id']").change();
        }

        $(document).on("click", "#exam_price_table > tbody > tr.exam_price_row > td > .btn_voucher", function() {
                console.log("\n\n\n\n======this exam_price_table=====",$(this).parents('tr').clone(true))
                var event_id = $(this).closest('.exam_price_row').find('input.event_id').val();
                console.log("\n\n\n\n==============event_id============",event_id);
                $(".modal-body #event_id").val(event_id);
                var modal = $(document).find('#pc_exam_voucher').modal('show');
                $( "#pc_exam_voucher" ).on('shown', function(){ alert("I want this to appear after the modal has opened!"); });
                document.getElementById("voucher_form").reset();
                document.getElementById("errormessage").innerHTML = " ";
//                console.log("\n\n\n\n======button=====",$(this).closest('.exam_price_row').find('button.btn_voucher').attr("disabled", true))
//                $(this).closest('.exam_price_row').find('button.btn_voucher').attr("disabled", true)
         });

        $('.voucher_search').on('click', function (e) {
//            document.getElementById("errormessage").innerHTML = "";
            $('#voucher_code').attr('required', true);
            var voucher_value = $(document).find('#voucher_code').val();
            var event = $(document).find('#event_id').val();
            console.log("\n\n\n\n==============voucher_value============",voucher_value,event);
            if(!voucher_value){
                $('#voucher_code').attr('required', true);
            }
            else{
                ajax.jsonRpc("/check_voucher", 'call', {
                    'voucher_value': voucher_value,
                    'event_id':event,
                }).then(
                    function(result) {
                        if (result['voucher_id']) {
                            console.log("\n\n\n\n\n\n=========$().closest('.exam_price_table')==",$(document).find('#exam_price_table'))
                            var voucher_id = $(document).find("#voucher_"+event).val(parseFloat((result['voucher_price']).toFixed(2)));
                            console.log("\n\n\n\n=====voucher_id====",voucher_id,result['voucher_price'])
                            var event_price = parseFloat($(document).find("#event_price_"+event).val());
                            console.log("\n\n\n\n\n=======event_price===========",event_price)
                            var total_price = event_price - parseFloat((result['voucher_price']).toFixed(2));

                            var total_exam_price = $(document).find('#total_exam_price').val();
                            var total_voucher_price = parseFloat($(document).find("#total_voucher_price").val());
                            var total = $(document).find("#final_total_price").val();
                            console.log("\n\n\n\n\n========total_exam_price===========",total_exam_price,typeof(total_voucher_price),total_price)

                            var total_voucher_price = parseFloat((total_voucher_price).toFixed(2)) + parseFloat((result['voucher_price']).toFixed(2));
                            console.log("\n\n\n\n\n========total_voucher_price===========",total_voucher_price)
                            if (total_price <= 0){
                                $(document).find("#total_exam_price_"+event).val(0.0);
                                var final_total = total -  parseFloat((event_price).toFixed(2));
                                $(document).find("#total_voucher_price").val(parseFloat((total_voucher_price).toFixed(2)));
                                console.log("\n\n\n\n\n=======final_total------",final_total)
                                if (final_total <= 0){
                                    $(document).find("#final_total_price").val(0.0);
                                    $(document).find("#price_total").val(0);
                                }
                                else{
                                    $(document).find("#final_total_price").val(parseFloat((final_total).toFixed(2)));
                                    $(document).find("#price_total").val(parseFloat((final_total).toFixed(2)));
                                }
//                                $(document).find("#final_total_price").val(parseFloat((final_total).toFixed(2)));
//                                $(document).find("#price_total").val(parseFloat((final_total).toFixed(2)));
                            }
                            else{
                                $(document).find("#total_exam_price_"+event).val(parseFloat((total_price).toFixed(2)));
                                var final_total = total -  parseFloat((result['voucher_price']).toFixed(2));
                                $(document).find("#total_voucher_price").val(parseFloat((total_voucher_price).toFixed(2)));
                                $(document).find("#final_total_price").val(parseFloat((final_total).toFixed(2)));
                                $(document).find("#price_total").val(parseFloat((final_total).toFixed(2)));
                            }

//                            var total = total_exam_price -  parseFloat((event_price).toFixed(2));
//                            $(document).find("#total_voucher_price").val(parseFloat((total_voucher_price).toFixed(2)));
//                            $(document).find("#final_total_price").val(parseFloat((total).toFixed(2)));
//                            $(document).find("#price_total").val(parseFloat((total).toFixed(2)));
//                            console.log("\n\n\n\n\n==type===",typeof(parseFloat((total).toFixed(2))))
                            voucher_list.push(result['voucher_id']);
                            $(document).find("#voucher_id").val(voucher_list);
                            $(document).find('#pc_exam_voucher').modal('hide');
                            if ($(document).find("#final_total_price").val() == 0){
                                $(document).find('#btn_pay_via_eft').css('display', 'none');
                                $(document).find('#btn_pay_via_credit_card').css('display', 'none');
                                $(document).find('#btn_confirm_booking').css('display', 'block');
                            }
                        }
                        else if (result['error'] == 'status'){
                            console.log("\n\n\n==result status========",result)
                            document.getElementById("errormessage").innerHTML = "This Voucher cannot be applied because it has a status of "+result['status']+". Contact the CharterQuest office if you believe this is in error.";
//                            $(document).find('.errormessage').val('This Voucher cannot be applied because it has a status of'+result[status]+'. Contact the CharterQuest office if you believe this is in error.')
                        }
                        else if (result['error'] == 'qualification'){
                            console.log("\n\n\n\n=======qul error======")
                            document.getElementById("errormessage").innerHTML = "The voucher you are attempting to apply does not match.The Qualification level of your exam.Please review your voucher and contact Charterquest office if you belive this in error.";
//                            $(document).find('.errormessage').val('The voucher you are attempting to apply does not match.The Qualification level of your exam.Please review your voucher and contact Charterquest office if you belive this in error.');
                        }
                        else if (result['error'] == 'error'){
                            console.log("\n\n\n\n=======error error======")
                            document.getElementById("errormessage").innerHTML = "Voucher Number is not valid";
//                            $(document).find('.errormessage').val('Voucher Number is not valid')
                        }
                    });

            }
//            document.getElementById("voucher_form").reset();
//            document.getElementById("errormessage").innerHTML = " ";
        });

//        $("#examtablebody").on("click", ".exam_search", function() {
//            console.log("\n\n\n\n\n=====tr value=========",$(this).closest("tr"))
////          $(this).closest("tr").remove();
//        });

        $('.exam_search').on('click', function (e) {
            e.preventDefault();
            console.log("\n\n\n\n==============call============");

            $('#select_pc_exam_level').attr('required', true);
            $('#select_pc_exam_subject').attr('required', true);
            $("#exam_datepicker").attr('required',true)
            var level_value = $(document).find('#select_pc_exam_level').val();
            var subject_value = $(document).find('#select_pc_exam_subject').val();
            if (subject_value == '') {
                $('#select_pc_exam_subject').attr('required', true);
            }
            var campus_value = $(document).find('#campus').val();
            var exam_type_value = $(document).find('#select_exam_type').val();
            var date_exam = $(document).find('#exam_datepicker').val();
            var sale_order_id = $(document).find('#sale_order_id').val();
            if (sale_order_id){
                var e = document.getElementById("select_pc_exam_subject");
	            var sub = e.options[e.selectedIndex].text;
	            console.log("\n\n\n\n==============call=====e====sub===",e,sub);
	            subject_value = sub;
            }
            if ((!level_value) || (!subject_value)){
                    $('#select_pc_exam_level').attr('required', true);
                    $('#select_pc_exam_subject').attr('required', true);
            }
            else{
               ajax.jsonRpc("/pc_exam_search", 'call', {
                'level': level_value,
                'subject':subject_value,
                'campus':campus_value,
                'exam_type':exam_type_value,
                'date':date_exam,
                'sale_order_id':sale_order_id,
            }).then(
                function(result) {
                    $("#examtablebody").html('');
                    console.log("\n\n\n\n==================result==level_value=",result,level_value,subject_value,date_exam)
                    if (level_value && subject_value && date_exam && result){
                        $('.available_exam').css("display", "block");
                        $('.selected_exam').css("display", "block");
                        $('.term_condition').css("display", "block");

                        console.log("\n\n\n\n==================result===",result)
                        for(var i=0;i<result.length;i++)
                        {
                            console.log("\n\n\n\n=====i========",i,result[i]['subject_name'])
                            var st_date=(result[i]['start_time']).split(" ");
                            console.log("\n\n\n\n=====startDate========",typeof(st_date[1]))
                            var st_date_list = (st_date[1]).split(":");
                            var startdate=st_date_list[0]+":"+st_date_list[1];

                            var end_date=(result[i]['end_time']).split(" ");
                            var end_date_list = (end_date[1]).split(":");
                            var enddate=end_date_list[0]+":"+end_date_list[1];
                            console.log("\n\n\n\n=====price========",typeof(result[i]['price']))
    //                        var sub_name =(result[i]['subject_name']).toString();
                            $('#examtablebody').append("<tr class='exam_row'><td style='color:black;'>"+ result[i]['subject_name'] +"</td><td style='color:black;'><input id='exam_time' style='width: 100px !important; height: 30px; background: white; border: white;' class='exam_time' type='text' disabled='true' value=" + startdate+"-"+enddate + " ></td><td style='color:black;'><input id='exam_date' style='width: 100px !important; height: 30px; background: white; border: white;' class='exam_date' type='text' disabled='true' value=" + st_date[0] + " ></td><td class='aval_seats' style='color:black;'>" + result[i]['seats_available'] + "</td><td class='price' style='color:black;'><input id='exam_price' style='width: 80px !important; height: 30px; background: white; border: white;' class='exam_price' type='number' disabled='true' value=" + result[i]['price'] + " ></input></td><td><button id='select_button' style='margin-bottom: 0px !important;margin-top: 0px !important;'class='btn btn-primary selectbtn' value='Select' type='button'>Select</button></td><td style='display:none;'><input type='hidden' class='exam_id' id='exam_id' value=" + result[i]['exam_id'] + "></input></td></tr>");
                        }
                    }
                    else{
                        alert('Please Select other Date')
                        $('.exam_search').attr("disabled", false);
                    }

                });
            }
            if (level_value && subject_value && date_exam)
            {
                $('.exam_search').attr("disabled", true);
            }
        })

        $(document).on("click", "#examTable tbody > tr > td > .selectbtn", function() {
            console.log("\n\n\n\n======this=====",$(this).parents('tr').clone(true))
            var row = $(this).parents('tr').clone(true);

            console.log("\n\n\n\n======row=====",row.find('button.select_button')['context']);
            $('#select_exam_body').append(row);

            var avl_seats = $(this).closest('.exam_row').find('td.aval_seats').val();
            var price = $(this).closest('.exam_row').find('input.exam_price').val();
            var date = $(this).closest('.exam_row').find('input.exam_date').val();
            var time = $(this).closest('.exam_row').find('input.exam_time').val();
            var srow = $("#examselectTable tbody > tr > td > .selectbtn");
            var select_exam_id = $(this).closest('.exam_row').find('input.exam_id').val();
            srow.html('Remove');
            console.log("\n\n\n\n======srow=====",price,srow,srow.val(),exam_id,avl_seats,date,time);
            select_exam_price = select_exam_price + parseFloat(price);
            console.log("\n\n\n\n======select_exam_price =====",select_exam_price,select_exam_id)
            $('#total_price').val(select_exam_price);

            event_ids.push(select_exam_id);
            $('#event_ids').val(event_ids);
            console.log("\n\n\n\n\n\n=============event_ids==========event======",event_ids)
//            ajax.jsonRpc("/set_available_seats", 'call', {
//                    'select_exam_id': select_exam_id,
//                    'type':'Select',
//                }).then(
//                    function(result) {
//                        console.log("\n\n\n\n=====list====",result,typeof(result))
//                        $('#event_ids').val(result);
//                    });
        });

        $(document).on("click", "#examselectTable tbody > tr > td > .selectbtn", function() {
            var row = $(this).parents('tr').clone(true);
            var re_price = $(this).closest('.exam_row').find('input.exam_price').val();
            var remove_exam_id = $(this).closest('.exam_row').find('input.exam_id').val();
            console.log("\n\n\n\n======row id =====",remove_exam_id);
            console.log("\n\n\n\n======re_price =====",re_price)
            select_exam_price = select_exam_price - re_price;
            console.log("\n\n\n\n======remove_exam_price =====",select_exam_price)
            $('#total_price').val(parseFloat((select_exam_price).toFixed(2)));
            $(this).closest('.exam_row').remove();

            event_ids.pop(remove_exam_id);
            $('#event_ids').val(event_ids);
//            ajax.jsonRpc("/set_available_seats", 'call', {
//                    'remove_exam_id': remove_exam_id,
//                    'type':'Remove',
//                }).then(
//                    function(result) {
//                        console.log("\n\n\n\n=====list====",result,typeof(result))
//                        $('#event_ids').val(result);
//                    });
        });





    });


});

