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

	$('.multiple-codes-select').select2({
		placeholder: "Select a Subject"
	});

	$('.multiple-levels-select').select2({
		placeholder: "Select a Level"
	});

	$('.multiple-option-select').select2({
		placeholder: "Select a Study Option"
	});

	$('.multiple-semester-select').select2({
		placeholder: "Select a Semester"
	});

	$('.multiple-campus-select').select2({
		placeholder: "Select a Campus"
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

});