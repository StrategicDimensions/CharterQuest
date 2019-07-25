$(document).ready(function() {

	$('#calendar_time_table').fullCalendar({
		header: {
			left: 'prev,next today',
			center: 'title',
			right: 'month,agendaWeek,agendaDay'
		},
		defaultDate: moment(),
		defaultView: 'month',
		editable: true,
		events: [
			{
				title: 'All Day Event',
				start: '2019-07-01'
			},
			{
				title: 'Long Event',
				start: '2019-07-07',
				end: '2019-07-10'
			},
			{
				id: 999,
				title: 'Repeating Event',
				start: '2019-07-09T16:00:00'
			},
			{
				id: 999,
				title: 'Repeating Event',
				start: '2019-07-16T16:00:00'
			},
			{
				title: 'Meeting',
				start: '2019-07-16T10:30:00',
				end: '2019-07-16T12:30:00'
			},
			{
				title: 'Lunch',
				start: '2019-07-12T12:00:00'
			},
			{
				title: 'Birthday Party',
				start: '2019-07-13T07:00:00'
			},
			{
				title: 'Click for Google',
				url: 'http://google.com/',
				start: '2019-07-28'
			}
		]
	});

});