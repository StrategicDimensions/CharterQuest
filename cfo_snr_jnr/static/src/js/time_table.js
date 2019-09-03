odoo.define('cfo_snr_jnr.time_table',function (require) {
"use strict";

var rpc = require('web.rpc');
var self = this;
var flag = false;
var localStorage = window.localStorage;
$(document).ready(function(){

	$('.info_time_table_course').popover({
		animation: true,
		html: true,
        content: function() {
			var content = $(this).attr("data-popover-content");
			return $(content).children(".popover-body").html();
        },
        title: function() {
			var title = $(this).attr("data-popover-content");
			return $(title).children(".popover-heading").html();
        }
	});

	$('body').on('click', function (e) {
		$('.info_time_table_course').each(function () {
			if (!$(this).is(e.target) && $(this).has(e.target).length === 0 && $('.popover').has(e.target).length === 0) {
				$(this).popover('hide');
			}
		});
	});

	$('.o_fillter_click').on('click',function(){
	    console.log("\n\n\n calll>>",flag)
	    flag = true;
	    console.log("\n\n\n calll111>>",flag)
	});

	$('.multiple-campus-select').on('change',function(){
//    alert()
        var value=$(this).val();
        localStorage.setItem("campus",value);
    });

    $('.multiple-levels-select').on('change',function(){
//    alert()
        var value=$(this).val();
        localStorage.setItem("levels",value);
    });

    $('.multiple-codes-select').on('change',function(){
//    alert()
        var value=$(this).val();
        localStorage.setItem("codes",value);
    });

    $('.multiple-semester-select').on('change',function(){
//    alert()
        var value=$(this).val();
        localStorage.setItem("semester",value);
    });

    $('.multiple-option-select').on('change',function(){
//    alert()
        var value=$(this).val();
        localStorage.setItem("option",value);
    });


	if(window.location.pathname == '/time_table'){

        $('#campus_select').select2().select2({
			    placeholder: "Select a Campus"
		    });

		$('#level_select').select2({
			    placeholder: "Select a level"
		    });

		$('#course_code_select').select2({
			    placeholder: "Select a Subject"
		    });

		$('#semester_select').select2({
			    placeholder: "Select a Semester"
		    });

		$('#option_select').select2({
			    placeholder: "Select a Study Option"
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
	}

	$('.back_to_lecturers').on('click', function(){
		window.history.back();
	});

    $('#level_select').on('click',function(){
        var qua_ids=$('#level_select').val()
        var campus_ids=$('#campus_select').val()
        var subject=[]
        var semester=[]
        var study_option=[]
        rpc.query({
                model:'cfo.time.table',
                method:'get_data',
                args:[qua_ids,campus_ids]
        }).then(function (data){
            for(var i=0; i<data[0].length; i++)
            {
                subject.push('<option value="' + data[0][i].id + '">' + data[0][i].name + '</option>\n')
            }
            $(document).find('#course_code_select').html(subject)
            for(var i=0; i<data[1].length; i++)
            {
                semester.push('<option value="' + data[1][i].id + '">' + data[1][i].name + '</option>\n')
            }
            $(document).find('#semester_select').html(semester)
            for(var i=0; i<data[2].length; i++)
            {
                study_option.push('<option value="' + data[2][i].id + '">' + data[2][i].name + '</option>\n')
            }
            $(document).find('#option_select').html(study_option)
        })
    });
    $('#campus_select').on('click',function(){
        var qua_ids=$('#level_select').val()
        var campus_ids=$('#campus_select').val()
        var subject=[]
        var semester=[]
        var study_option=[]
        rpc.query({
                model:'cfo.time.table',
                method:'get_data',
                args:[qua_ids,campus_ids]
        }).then(function (data){
            for(var i=0; i<data[0].length; i++)
            {
                subject.push('<option value=' + data[0][i].id + '>' + data[0][i].name + '</option>\n')
            }
            $(document).find('#course_code_select').html(subject)
            for(var i=0; i<data[1].length; i++)
            {
                semester.push('<option value=' + data[1][i].id + '>' + data[1][i].name + '</option>\n')
            }
            $(document).find('#semester_select').html(semester)
            for(var i=0; i<data[2].length; i++)
            {
                study_option.push('<option value=' + data[2][i].id + '>' + data[2][i].name + '</option>\n')
            }
            $(document).find('#option_select').html(study_option)
        })
    });

    $(window).on("load",function(){

//        rpc.query({
//            model:'cfo.time.table.weeks',
//            method:'remove_color',
//            args:[]
//        });
    
        var campus = localStorage.getItem("campus")
        if (campus){
            $('#campus_select').select2().select2('val',campus.split(","));
        }
        else
        {
           $('#campus_select').select2({
			    placeholder: "Select a Campus"
		    });
        }

        var levels = localStorage.getItem("levels")
        console.log("\n\n\n levels",levels)
        if (levels){
            $('#level_select').select2().select2('val',levels.split(","));
        }
        else
        {
           $('#level_select').select2({
			    placeholder: "Select a level"
		    });
        }

        var codes = localStorage.getItem("codes")
        console.log("\n\n\n codes",codes)
        if (codes){
            $('#course_code_select').select2().select2('val',codes.split(","));
        }
        else
        {
           $('#course_code_select').select2({
			    placeholder: "Select a Subject"
		    });
        }

        var semester = localStorage.getItem("semester")
        console.log("\n\n\n semester",semester)
        if (semester){
            $('#semester_select').select2().select2('val',semester.split(","));
        }
        else
        {
           $('#semester_select').select2({
			    placeholder: "Select a Semester"
		    });
        }

        var option = localStorage.getItem("option")
        console.log("\n\n\n option",option)
        if (option){
        $('#option_select').select2().select2('val',option.split(","));
        }
        else
        {
           $('#option_select').select2({
			    placeholder: "Select a Study Option"
		    });
        }

        localStorage.clear();


    });
    var i=0;
    $('.time_table_div').each(function(){
        i++;
        var newID='sesson'+i;
        $(this).attr('id',newID);
        $(this).val(i);
    });

    $(".cfo-cnr-jnr-color-picker").on("click",function(e){
        var id="#"+ e.toElement.id;
        var data_id=$(id).attr('data')
        console.log("\n\n\n data_id",data_id)
        var hexVal=null
        $(id).spectrum();
        $(id).on('move.spectrum', function(e, tinyColor) {
            hexVal = tinyColor.toHexString();
            console.log("\n\n\n val>>>",hexVal)
            $(id).css('backgroundColor', '#' + hexVal);
        });
        $('.sp-choose').on("click",  function(){
             rpc.query({
                model:'cfo.time.table.weeks',
                method:'add_color',
                args:[data_id,hexVal]
            });
        });
    });


});
});