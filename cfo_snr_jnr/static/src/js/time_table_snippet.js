odoo.define('cfo_snr_jnr.time_table_snippet',function (require) {
"use strict";

var rpc = require('web.rpc');
var ajax = require('web.ajax');
var core = require('web.core');
var QWeb = core.qweb;
var self = this;
$(document).ready(function(){
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
    });

        $("#level_select").prop('disabled', true);
	    $("#course_code_select").prop('disabled', true);
	    $("#semester_select").prop('disabled', true);
	    $("#option_select").prop('disabled', true);


        $('#campus_select').select2({
			    placeholder: "",
		    });

		$('#level_select').select2({
			    placeholder: ""
		    });

		$('#semester_select').select2({
			    placeholder: ""
		    });

		$('#course_code_select').select2({
			    placeholder: ""
		    });

		$('#option_select').select2({
			    placeholder: ""
		    });
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
//    alert()
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



    $(".fillter_timetable").on('click',function(e){
            var id=$(this).attr('data-id')
            var qua_ids=$('#level_select').val()
            var campus_ids=$('#campus_select').val()
            var semester_ids=$('#semester_select').val()
            var course_code_ids=$('#course_code_select').val()
            var option_ids=$('#option_select').val()
            if(id){
                ajax.jsonRpc('/time_table_snippet', 'call', {
                'level_select': qua_ids,
                'campus_select': campus_ids,
                'semester_select': semester_ids,
                'option_select':option_ids,
                'course_code_select':course_code_ids,
                'id':id
                }).then(function (data) {
                    $("#timetable_body").html(data);
                    var i=0;
                    $('.time_table_snippet_div').each(function(){
                        i++;
                        var newID='sesson'+i;
                        $(this).attr('id',newID);
                        $(this).val(i);
                    });
                    $('#level_select').val('').trigger("change");
                    $('#campus_select').val('').trigger("change");
                    $('#semester_select').val('').trigger("change");
                    $('#course_code_select').val('').trigger("change");
                    $('#option_select').val('').trigger("change");
                    });
            }
    });


});
$(document).ajaxComplete(function(){

    $('.info_time_table_course_snippet').popover({
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

    $('.time_table_snippet_div').popover({
		animation: true,
		html: true,
		trigger : 'hover',
		placement: 'right',
		selector:$('.time_table_snippet_div'),
        content: function() {
			var content = $(this).attr("data-popover-content");
			return content;
        },
	});
	$('body').on('click', function (e) {
		$('.info_time_table_course_snippet').each(function () {
			if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
				$(this).popover('hide');
			}
		});
	});

    var i=0;
    $('.time_table_snippet_div').each(function(){
        i++;
        var newID='sesson'+i;
        $(this).attr('id',newID);
        $(this).val(i);
    });

    $('.color-picker').on("click",function(e){
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

    $('.back_to_lecturers').on('click', function(){
		window.history.back();
	});

});
});