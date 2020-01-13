$(document).ready( function () {
    $('#myTable').DataTable();
} );
$( 'table' ).DataTable( {
	  order: [ [ 0, "asc" ] ],
		responsive: {
	        details: {
	            type: 'column',
	            target: 'tr'
	        }
	    },
	    columnDefs: [ {
	        className: 'control',
	        orderable: false,
	        targets: -1
	    } ]
	} );