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

	if(window.location.pathname == '/time_table'){

		$('.multiple-codes-select').select2({
			placeholder: "Select a Subject"
		});

		var codes_list = [];
		$.each($(document).find("input[name=course_code_select]").val().split(','), function (key, val){
			codes_list.push(parseInt(val));
		});

	//	$('.multiple-codes-select').select2('val', codes_list);

		$('.multiple-levels-select').select2({
			placeholder: "Select a Level"
		});

		var level_list = [];
		$.each($(document).find("input[name=level_select]").val().split(','), function (key, val){
			level_list.push(parseInt(val));
		});

		$('.multiple-levels-select').select2('val', level_list);

		$('.multiple-option-select').select2({
			placeholder: "Select a Study Option"
		});

		var option_list = [];
		$.each($(document).find("input[name=option_select]").val().split(','), function (key, val){
			option_list.push(parseInt(val));
		});

		$('.multiple-option-select').select2('val', option_list);

		$('.multiple-semester-select').select2({
			placeholder: "Select a Semester"
		});

		var semester_list = [];
		$.each($(document).find("input[name=semester_select]").val().split(','), function (key, val){
			semester_list.push(parseInt(val));
		});

		$('.multiple-campus-select').select2('val', semester_list);

		$('.multiple-campus-select').select2({
			placeholder: "Select a Campus"
		});

		var campus_list = [];
		$.each($(document).find("input[name=campus_select]").val().split(','), function (key, val){
			campus_list.push(parseInt(val));
		});

		$('.multiple-campus-select').select2('val', campus_list);

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

});