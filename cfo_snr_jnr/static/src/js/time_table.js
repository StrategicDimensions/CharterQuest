odoo.define('cfo_snr_jnr.time_table',function (require) {
"use strict";

var rpc = require('web.rpc');
var ajax = require('web.ajax');
var core = require('web.core');
var session = require('web.session');
var QWeb = core.qweb;
var self = this;
var flag = false;
var localStorage = window.localStorage;
$(document).ready(function(){
	if(window.location.pathname == '/time_table'){

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
            var option_ids=$('#option_select').val()
            var subject=[]
            var study_option=[]
                ajax.jsonRpc('/get_timetable_data', 'call', {
                'qua_ids': qua_ids,
                'campus_ids': campus_ids,
                'semester_ids': semester_ids,
                'option_ids':option_ids
            }).then(function (data) {
                $(document).find('#course_code_select').html("")
                for(var i=0; i<data['subject'].length; i++)
                {
                    subject.push('<option value=' + data['subject'][i].id + '>' + data['subject'][i].name + '</option>\n')
                }
                $(document).find('#course_code_select').html(subject)
//                $(document).find('#option_select').html("")
//                for(var i=0; i<data['study_option'].length; i++)
//                {
//                    study_option.push('<option value=' + data['study_option'][i].id + '>' + data['study_option'][i].name + '</option>\n')
//                }
//                $(document).find('#option_select').html(study_option)
            });
    });


    $('#option_select').on('click',function(){
            var qua_ids=$('#level_select').val()
            var campus_ids=$('#campus_select').val()
            var semester_ids=$('#semester_select').val()
            var option_ids=$('#option_select').val()
            var subject=[]
            var study_option=[]
                ajax.jsonRpc('/get_timetable_data', 'call', {
                'qua_ids': qua_ids,
                'campus_ids': campus_ids,
                'semester_ids': semester_ids,
                'option_ids':option_ids
            }).then(function (data) {
                $(document).find('#course_code_select').html("")
                for(var i=0; i<data['subject'].length; i++)
                {
                    subject.push('<option value=' + data['subject'][i].id + '>' + data['subject'][i].name + '</option>\n')
                }
                $(document).find('#course_code_select').html(subject)
//                $(document).find('#option_select').html("")
//                for(var i=0; i<data['study_option'].length; i++)
//                {
//                    study_option.push('<option value=' + data['study_option'][i].id + '>' + data['study_option'][i].name + '</option>\n')
//                }
//                $(document).find('#option_select').html(study_option)
            });
    });

    $('#campus_select').on('click',function(){
        var qua_ids=$('#level_select').val()
            var campus_ids=$('#campus_select').val()
            var semester_ids=$('#semester_select').val()
            var option_ids=$('#option_select').val()
            var subject=[]
            var study_option=[]
                ajax.jsonRpc('/get_timetable_data', 'call', {
                'qua_ids': qua_ids,
                'campus_ids': campus_ids,
                'semester_ids': semester_ids,
                'option_ids':option_ids
            }).then(function (data) {
                $(document).find('#course_code_select').html("")
                for(var i=0; i<data['subject'].length; i++)
                {
                    subject.push('<option value=' + data['subject'][i].id + '>' + data['subject'][i].name + '</option>\n')
                }
                $(document).find('#course_code_select').html(subject)
//                $(document).find('#option_select').html("")
//                for(var i=0; i<data['study_option'].length; i++)
//                {
//                    study_option.push('<option value=' + data['study_option'][i].id + '>' + data['study_option'][i].name + '</option>\n')
//                }
//                $(document).find('#option_select').html(study_option)
            });
    });

    $('#semester_select').on('click',function(){
        var qua_ids=$('#level_select').val()
            var campus_ids=$('#campus_select').val()
            var semester_ids=$('#semester_select').val()
            var option_ids=$('#option_select').val()
            var subject=[]
            var study_option=[]
                ajax.jsonRpc('/get_timetable_data', 'call', {
                'qua_ids': qua_ids,
                'campus_ids': campus_ids,
                'semester_ids': semester_ids,
                'option_ids':option_ids
            }).then(function (data) {
                $(document).find('#course_code_select').html("")
                for(var i=0; i<data['subject'].length; i++)
                {
                    subject.push('<option value=' + data['subject'][i].id + '>' + data['subject'][i].name + '</option>\n')
                }
                $(document).find('#course_code_select').html(subject)
//                $(document).find('#option_select').html("")
//                for(var i=0; i<data['study_option'].length; i++)
//                {
//                    study_option.push('<option value=' + data['study_option'][i].id + '>' + data['study_option'][i].name + '</option>\n')
//                }
//                $(document).find('#option_select').html(study_option)
            });
    });

    $('.time_table_css').each(function(){
        if($(this).children().find('.session_not_available').length > 0){
            $(this).css('display','none');
        }
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
            $("#option_select").prop('disabled', false);
        }
        else
        {
            $("#option_select").prop('disabled', true);
        }
    });

    $('#option_select').on('change',function(){
        var value=$(this).val();
        if (value){
            $(".multiple-codes-select").prop('disabled', false);
        }
        else
        {
            $(".multiple-codes-select").prop('disabled', true);
        }
    });

    $('.back_to_lecturers').on('click', function(){
		window.history.back();
	});

	}

	var i=0;
    var list_menu=[]
    $('#cfo_menu_with_tabs_div_panel ul.nav.nav-tabs').each(function(){
        i++;
        var newID='ul'+i;
        $(this).attr('id',newID);
        $(this).val(i);
        list_menu.push(newID)
    });

    for(var i=0; i<list_menu.length; i++){
        var id1=list_menu[i];
        var j=0;
        var cnt=$(document).find('#'+id1+' li').length;
        if($(document).find('#'+id1+' a.read-more').length >=1){
            $(document).find('#'+id1+' a.read-more').remove()
        }
        if (cnt > 2){
            $('#'+id1+' li:nth-child('+ 1 +')').addClass('active')
            $('#cfo_menu_with_tabs_div_panel div.tab-content.tabs div:nth-child('+1+')').addClass('active in').siblings().removeClass('active in');
            for(j=2;j<=cnt; j++){
                var $class = $('#'+id1+' li:nth-child('+ j +')');
                $class.removeClass('active')
                if ($class.hasClass('js-read-less')){}else{
                $class.addClass('js-read-less')}
            }
            $('#'+id1+' li:nth-child('+ 1 +')').addClass('active').removeClass('js-read-less')
            $('#'+id1+' li:last-child').removeClass('active')
        }
        if ($(document).find('#'+id1+' button.read-more').length == 0){
            var btnid="btn"+id1
            $('#'+id1).append(`<button type="submit" class='read-more fa fa-arrow-down' id="`+btnid+`"> More</button>`)
        }

    }

    $(document).on('click','button.read-more',function(){
        var id=$(this).attr('id')
        var pid=$(this).parents().attr('id')
        $('#'+pid+' li.js-read-less').addClass('js-read-more').removeClass('js-read-less');
        $(document).find('#'+id).addClass('read-less');
    });

    $(document).on('click','a.cfo_menu_with_tabs_a_panel',function(){
        $(this).parent().siblings().removeClass();
        $(this).parent().siblings().addClass('js-read-less');
        $(this).parent().parent().find('button.js-read-less').addClass('read-more fa fa-arrow-down').removeClass('js-read-less');
    });

    $('a.add_menu_side').on('click',function(){
        if(window.innerWidth <= 460) {
            $(this).parents('.label_link_list').css('display','none');
        }
    })

    $(document).on('click','.material-card',function(){
        $(document).find('.material-card').removeClass('active');
        $(this).addClass('active');
    });
    	$('.material-card > .mc-btn-action').click(function () {
            var card = $(this).parent('.material-card');
            var icon = $(this).children('i');
            icon.addClass('fa-spin-fast');

            if (card.hasClass('mc-active')) {
                card.removeClass('mc-active');

                window.setTimeout(function() {
                    icon
                        .removeClass('fa-arrow-left')
                        .removeClass('fa-spin-fast')
                        .addClass('fa-bars');

                }, 800);
            } else {
                card.addClass('mc-active');

                window.setTimeout(function() {
                    icon
                        .removeClass('fa-bars')
                        .removeClass('fa-spin-fast')
                        .addClass('fa-arrow-left');

                }, 800);
            }
        });
        $('.details_view_lecturer').on('click', function (){
        	window.location.href = $(this).attr('data-href');
        });


        let url = location.href.replace(/\/$/, "");

		if (location.hash) {
			const hash = url.split("#");
			$('#cfo_menu_with_tabs_div_panel a[href="#' + hash[1] + '"]').tab("show");
			url = location.href.replace(/\/#/, "#");
			history.replaceState(null, null, url);
			setTimeout(() => {
				$(window).scrollTop(0);
			}, 400);
		}

		$('.cfo_menu_with_tabs_a_panel').on("click", function(event) {
            if($(this).attr("external-href") != '#')
			{
				const hash = $(this).attr("external-href");
				const win=window.open(hash);
				win.focus();
				event.preventDefault();
			}
			else{
				let newUrl;
				const hash = $(this).attr("href");
				if (hash == "#home") {
					newUrl = url.split("#")[0];
				} else {
					newUrl = url.split("#")[0] + hash;
				}
				newUrl += "/";
				history.replaceState(null, null, newUrl);
			}
			event.preventDefault();
		});

        $('.cfo_snr_jnr_time_table_snippet').each(function(){
            $(this).remove();
        })
});
});