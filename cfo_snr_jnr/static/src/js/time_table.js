odoo.define('cfo_snr_jnr.time_table',function (require) {
"use strict";

var rpc = require('web.rpc');
var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;
var self = this;
var flag = false;
var localStorage = window.localStorage;
$(document).ready(function(){
//    alert()

	if(window.location.pathname == '/time_table'){

//	    $("#level_select").prop('disabled', true);
//	    $("#course_code_select").prop('disabled', true);
//	    $("#semester_select").prop('disabled', true);
//	    $("#option_select").prop('disabled', true);


//        $('#campus_select').select2({
//			    placeholder: "",
//
//		    });
//
//		$('#level_select').select2({
//			    placeholder: ""
//		    });
//
//		$('#semester_select').select2({
//			    placeholder: ""
//		    });
//
//		$('#course_code_select').select2({
//			    placeholder: ""
//		    });
//
//		$('#option_select').select2({
//			    placeholder: ""
//		    });
		$(document).on("click", ".details_view_lecturer", function(event){
			window.location.href = $(this).attr('data-href');
		});

		$(document).on('change','#course_code_select',function(){
			$(document).find('input[name="course_code_select"]').val($('.multiple-codes-select').select2('val'));
		});

		$(document).on('change','#level_select',function(){
			$(document).find('input[name="level_select"]').val($('.multiple-levels-select').select2('val'));
		});

		$(document).on('change','#option_select',function(){
			$(document).find('input[name="option_select"]').val($('.multiple-option-select').select2('val'));
		});

		$(document).on('change','#semester_select',function(){
			$(document).find('input[name="semester_select"]').val($('.multiple-semester-select').select2('val'));
		});

		$(document).on('change','#campus_select',function(){
                $(document).find('input[name="campus_select"]').val($('.multiple-campus-select').select2('val'));
		});

		$('#level_select').on('click',function(){
        var qua_ids=$('#level_select').val()
        var campus_ids=$('#campus_select').val()
        var semester_ids=$('#semester_select').val()
        var subject=[]
        var study_option=[]
        ajax.jsonRpc('/get_timetable_data', 'call', {
            'qua_ids': qua_ids,
            'campus_ids': campus_ids,
            'semester_ids': semester_ids
        }).then(function (data) {
            $(document).find('#course_code_select').html("")
            for(var i=0; i<data['subject'].length; i++)
            {
                subject.push('<option value=' + data['subject'][i].id + '>' + data['subject'][i].name + '</option>\n')
            }
            $(document).find('#course_code_select').html(subject)
            $(document).find('#option_select').html("")
            for(var i=0; i<data['study_option'].length; i++)
            {
                study_option.push('<option value=' + data['study_option'][i].id + '>' + data['study_option'][i].name + '</option>\n')
            }
            $(document).find('#option_select').html(study_option)
            });
    });

    $('#campus_select').on('click',function(){
        var qua_ids=$('#level_select').val()
        var campus_ids=$('#campus_select').val()
        var semester_ids=$('#semester_select').val()
        var subject=[]
        var study_option=[]
        ajax.jsonRpc('/get_timetable_data', 'call', {
            'qua_ids': qua_ids,
            'campus_ids': campus_ids,
            'semester_ids': semester_ids
        }).then(function (data) {
            $(document).find('#course_code_select').html("")
            for(var i=0; i<data['subject'].length; i++)
            {
                subject.push('<option value=' + data['subject'][i].id + '>' + data['subject'][i].name + '</option>\n')
            }
            $(document).find('#course_code_select').html(subject)
            $(document).find('#option_select').html("")
            for(var i=0; i<data['study_option'].length; i++)
            {
                study_option.push('<option value=' + data['study_option'][i].id + '>' + data['study_option'][i].name + '</option>\n')
            }
            $(document).find('#option_select').html(study_option)
            });
    });

    $('#semester_select').on('click',function(){
        var qua_ids=$('#level_select').val()
        var campus_ids=$('#campus_select').val()
        var semester_ids=$('#semester_select').val()
        var subject=[]
        var study_option=[]
        ajax.jsonRpc('/get_timetable_data', 'call', {
            'qua_ids': qua_ids,
            'campus_ids': campus_ids,
            'semester_ids': semester_ids
        }).then(function (data) {
        console.log("\n\n\n data...",data)
            $(document).find('#course_code_select').html("")
            for(var i=0; i<data['subject'].length; i++)
            {
                subject.push('<option value=' + data['subject'][i].id + '>' + data['subject'][i].name + '</option>\n')
            }
            $(document).find('#course_code_select').html(subject)
            $(document).find('#option_select').html("")
            for(var i=0; i<data['study_option'].length; i++)
            {
                study_option.push('<option value=' + data['study_option'][i].id + '>' + data['study_option'][i].name + '</option>\n')
            }
            $(document).find('#option_select').html(study_option)
            });
    });

    var i=0;
    $('.time_table_div').each(function(){
        i++;
        var newID='sesson'+i;
        $(this).attr('id',newID);
        $(this).val(i);
    });

    $(".cfo-cnr-jnr-color-picker").on("click",function(e){
        alert()
        var id="#"+ e.toElement.id;
        var data_id=$(id).attr('data')
            var hexVal=null
        $(id).spectrum();
        $(id).on('move.spectrum', function(e, tinyColor) {
            hexVal = tinyColor.toHexString();
            $(id).css('backgroundColor', '#' + hexVal);
        });
        $('.sp-choose').on("click",  function(){
              ajax.jsonRpc('/set_color', 'call',{
                    'data_id':data_id,
                    'hex_val':hexVal
              })

        });
    });
    $('.info_time_table_course').popover({
		animation: true,
		html: true,
		placement: 'right',
        content: function() {
			var content = $(this).attr("data-popover-content");
			return $(content).children(".popover-body").html();
        },
        title: function() {
			var title = $(this).attr("data-popover-content");
			return $(title).children(".popover-heading").html();
        }
	});

    $('.time_table_div').popover({
		animation: true,
		html: true,
		trigger : 'hover',
        content: function() {
			var content = $(this).attr("data-popover-content");
			return content;
        },
	});
	$('body').on('click', function (e) {
		$('.info_time_table_course').each(function () {
			if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
				$(this).popover('hide');
			}
		});
	});


	$('.multiple-campus-select').on('change',function(){
        var value=$(this).val();
        if (value){
            $('#campus_select').find('option').not(':selected').remove();
            $("#semester_select").prop('disabled', false);
        }
        else
        {
            ajax.jsonRpc('/get_campus', 'call',{

            }).then(function (data) {
                var campus=[]
                for(var i=0; i<data['campus'].length; i++)
                {
                    campus.push('<option value=' + data['campus'][i].id + '>' + data['campus'][i].name + '</option>\n')
                }
                $(document).find('#campus_select').html(campus)
                });
            $("#semester_select").prop('disabled', true);
        }
            localStorage.setItem("campus",value);
    });

    $('.multiple-semester-select').on('change',function(){
        var value=$(this).val();
        if (value){
            $("#level_select").prop('disabled', false);
        }
        else
        {
            $("#level_select").prop('disabled', true);
        }
        localStorage.setItem("semester",value);
    });

    $('.multiple-levels-select').on('change',function(){
       var value=$(this).val();
        if (value){
            $("#course_code_select").prop('disabled', false);
        }
        else
        {
            $("#course_code_select").prop('disabled', true);
        }
        localStorage.setItem("levels",value);
    });

    $('.multiple-codes-select').on('change',function(){
        var value=$(this).val();
        if (value){
            $("#option_select").prop('disabled', false);
        }
        else
        {
            $("#option_select").prop('disabled', true);
        }
            localStorage.setItem("campus",value);
    });

    $('.back_to_lecturers').on('click', function(){
		window.history.back();
	});

	}
});
});