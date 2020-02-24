odoo.define('cfo_snr_jnr.pc_exam', function(require){
    var ajax = require('web.ajax');

    $(document).ready(function() {

//        $('button[id="pc_exam_booking"]').on('click', function(ev) {
//            window.location.href = '/registerPB'
//        });

        var dateToday = new Date();
        console.log("\n\n\n\n============date=======",dateToday)
        $("#datepicker").datepicker({
                dateFormat: 'mm/dd/yy',
                changeMonth: true,
                changeYear: true,
                yearRange: '-100y:c+nn',
                minDate: 0
        });

//        $('#datepicker').datepicker({
//            onSelect: function(dateText, inst) {
//                //Get today's date at midnight
//                var today = new Date();
//                today = Date.parse(today.getMonth()+1+'/'+today.getDate()+'/'+today.getFullYear());
//                //Get the selected date (also at midnight)
//                var selDate = Date.parse(dateText);
//
//                if(selDate < today) {
//                    //If the selected date was before today, continue to show the datepicker
//                    $('#datepicker').val('');
//                    $(inst).datepicker('show');
//                }
//            }
//        });

        $(".exam_date_validation").on('click', function (event) {
            var date_exam = $(document).find('#datepicker').val();
            if (!date_exam) {
                event.preventDefault()
                alert('Date OF Exam Must Be Required');
            }

        });
        $('.exam_search').on('click', function (e) {
            e.preventDefault();
            console.log("\n\n\n\n==============call============");
            $('#select_pc_exam_level').attr('required', true);
            $('#select_pc_exam_subject').attr('required', true);
            $("#datepicker").attr('required',true)
            var level_value = $(document).find('#select_pc_exam_level').val();
            var subject_value = $(document).find('#select_pc_exam_subject').val();
            var date_exam = $(document).find('#datepicker').val();
            if (level_value && subject_value && date_exam){
                $('.available_exam').css("display", "block");
                $('.selected_exam').css("display", "block");
                $('.term_condition').css("display", "block");
            }
            else{
                $('#select_pc_exam_level').attr('required', true);
                $('#select_pc_exam_subject').attr('required', true);
            }

        });

    });


});

