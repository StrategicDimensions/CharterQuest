odoo.define('cfo_snr_jnr.login_page', function (require) {
    document.write("<script src='https://www.google.com/recaptcha/api.js'></script>");
    var ajax = require('web.ajax');
    $(document).ready(function () {
        if ($('.user_type_leader').val() == 'Leader') {
            $(this).attr('count', '1')
            $('.leader-add').css('display', 'none');
        } else {
            $('.leader-add').show();
        }
        if (window.location.href.indexOf("/cfo_senior") != -1) {
            var deadline_date = $(document).find('input[name="cfo_report_deadline_date_time"]').val();
            var countDownDate = new Date(deadline_date).getTime();

            var x = setInterval(function () {
                var now = new Date().getTime();
                var distance = countDownDate - now;
                var days = Math.floor(distance / (1000 * 60 * 60 * 24));
                var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((distance % (1000 * 60)) / 1000);

                if (deadline_date) {
                    html = ''
                    html += days + "Days " + hours + ":" + minutes + ":" + seconds + "";
                    $('#remaining_time_time').html(html);
                    if (distance < 0) {
                        clearInterval(x);
                        document.getElementById("remaining_time_time").innerHTML = "EXPIRED";
                    }
                }
            }, 1000);
        }

        if ($('.user_type_leader_acadamic').val() == 'Leader') {
            $(this).attr('count', '1')
            $('.leader-add-acadamic').css('display', 'none');
        } else {
            $('.leader-add-acadamic').show();
        }
        var count = $(document).find('.member-add').attr('data-count');
        if (count >= 3) {
            $(document).find('.member-add').hide();
        }
        else {
            $(document).find('.member-add').show();
        }

        var count_member = $(document).find('.member-add-school').attr('data-count');
        if (count_member >= 2) {
            $(document).find('.member-add-school').hide();
        }
        else {
            $(document).find('.member-add-school').show();
        }

        $(function () {
            $('.datepicker1').datepicker({
                autoclose: true,
                format: 'dd/mm/yyyy',

            });
        });
        $(function () {
            $('.datepicker2').datepicker({
                autoclose: true,
                format: 'dd/mm/yyyy',
                startDate: "0d"
            });
        });
        $(function () {
            $('.datepicker4').datepicker({
                autoclose: true,
                format: 'dd/mm/yyyy',
                endDate: "0d"

            });
        });
        $(function () {
            $('.datepicker5').datepicker({
                autoclose: true,
                todayHighlight: true,
                format: 'dd/mm/yyyy',
                endDate: "0d"
            });
        });
        $(".datepicker5").on('change', function () {
            var dt = new Date();
            var select_date = $(this).datepicker('getDate');
            dt.setFullYear(new Date().getFullYear() - 25);
            var date_one = new Date(select_date)
            var date_two = new Date(dt)
            if (date_one < date_two) {
                $(document).find('#check_birthdate_age').modal('show');
                $('#date_of_birth').val('');
            }

        });
        $(".check_date_validation").on('click', function (event) {
            var date_birth = $(document).find('#date_of_birth').val();
            if (!date_birth) {
                event.preventDefault()
                alert('Date OF Birth  Must Be Required');
            }

        });
        $('.submit_cfo_report').on('click', function (e) {
            $(document).find('.loader_report').css("display", "block");
            var report_value = $(document).find('#update_bio_check').val();
            var member_id = $(document).find('#member_id').val();
            var aspirant_id = $(document).find('input[name="aspirant_id"]').val();
            var team_id = $(document).find('input[name="team_id"]').val();
            ajax.jsonRpc("/submit_cfo_report_data", 'call',
                {'aspirant_id': aspirant_id, 'team_id': team_id}).then(
                function (result) {
                    html = ''
                    if (result.bio_not_upadate) {
                        for (key in result.list_without_bio_member) {
                            if (result.list_without_bio_member.hasOwnProperty(key)) {
                                html += "<tr><td>" + result.list_without_bio_member[key]['member_name'] + "</td>";
                                html += "<td>" + result.list_without_bio_member[key]['member_type'] + "</td></tr>";
                            }
                        }
                        $('#member_bio_list').html(html);
                        $(document).find('#cfo_memeber_bio_not_updated').modal('show');
                        $(document).find('.loader_report').css("display", "none");
                    }
                    else {
                        window.location.replace("/cfo_snr_report?aspirant_id=" + aspirant_id + "&team_id=" + team_id);
                        $(document).find('.loader_report').css("display", "none");
                    }
                });
        });
        $('.submit_cfo_jnr_report').on('click', function (e) {
            $(document).find('.loader_report_jnr_school').css("display", "block");
            var report_value = $(document).find('#update_bio_check').val();
            var member_id = $(document).find('#member_id').val();
            var aspirant_id = $(document).find('input[name="aspirant_id"]').val();
            var team_id = $(document).find('input[name="team_id"]').val();
            ajax.jsonRpc("/submit_cfo_jnr_report_data", 'call',
                {'aspirant_id': aspirant_id, 'team_id': team_id}).then(
                function (result) {
                    html = ''
                    if (result.bio_not_upadate) {
                        for (key in result.list_without_bio_member) {
                            if (result.list_without_bio_member.hasOwnProperty(key)) {
                                html += "<tr><td>" + result.list_without_bio_member[key]['member_name'] + "</td>";
                                html += "<td>" + result.list_without_bio_member[key]['member_type'] + "</td></tr>";
                            }
                        }
                        $('#member_bio_list').html(html);
                        $(document).find('#cfo_memeber_jnr_bio_not_updated').modal('show');
                        $(document).find('.loader_report_jnr_school').css("display", "none");
                    }
                    else {
                        window.location.replace("/cfo_jnr_report?aspirant_id=" + aspirant_id + "&team_id=" + team_id);
                        $(document).find('.loader_report_jnr_school').css("display", "none");
                    }
                });
        });
        $('.send_report_reminder').on('click', function (e) {
            e.preventDefault();
            var team_id = $(this).attr('id');
            $(document).find('.loader_report_reminder_send').css("display", "block");
            ajax.jsonRpc("/send_reminder_mail", "call", {'team_id': team_id}).then(
                function (result) {
                    if (result) {
                        $(document).find('#cfo_memeber_upload_report_reminder').modal('show');
                        $(document).find('.loader_report_reminder_send').css("display", "none");
                    }
                })
        })

        $('.oe_signup_form').on('submit', function (e) {
            var response = grecaptcha.getResponse();
            if (response.length == 0) {
                $('.g-recaptcha').css('border', '1px solid red');
                e.preventDefault();
                $('button[type="submit"]').removeAttr('disabled');
            }
        });
        $("#cfo_source").change(function () {
            if (this.value != 'Other') {
                $('#other_source').hide();
            }
            else {
                $('#other_source').show();
            }

            if (this.value != 'Social Media') {
                $('#socialmedia_source').hide();
            }
            else {
                $('#socialmedia_source').show();
            }
        });
        $('#cfo_competition').val('');
        $('#cfo_competition').change(function () {
            ajax.jsonRpc("/get_member_types", "call", {'val': $(this).val()}).then(function (result) {
                if (result) {
                    var html = '';
                    for (var i = 0; i < result.length; i++) {
                        html += "<option>" + result[i] + "</option>";
                    }
                    $('#cfo_membertype').html(html);
                }
            });
        });
        if ($('input[name="user_type"]:checked').val() == 'student') {
            $('#programme_name').attr('required', true);
            $('#school_name').attr('required', true);
            $('.employee_details').css('display', 'none');
            $('.school_details').css('display', 'block');
            $('.tertiry_studyfields').css('display', 'block');

        } else if ($('input[name="user_type"]:checked').val() == 'employee') {
            $('#programme_name').removeAttr('required', true);
            $('#legal_name_employer').attr('required', true);
            $('.school_details').css('display', 'none');
            $('.employee_details').css('display', 'block');
            $('.tertiry_studyfields').css('display', 'block');
            $('#sector').attr('required', true);
        }
        else {
            $('#programme_name').removeAttr('required', true);
            $('.school_details').css('display', 'none');
            $('.employee_details').css('display', 'none');
        }
        $('input[name="user_type"]').on('change', function () {
            if ($(this).val() == 'student') {
                $('#programme_name').attr('required', true);
                $('#school_name').attr('required', true);
                $('#legal_name_employer').attr('required', false);
                $('.school_details').css('display', 'block');
                $('.employee_details').css('display', 'none');
                $('#sector').attr('required', false);
                $('.tertiry_studyfields').css('display', 'block');
            } else {
                $('#programme_name').removeAttr('required', true);
                $('#school_name').attr('required', false);
                $('.tertiry_studyfields').css('display', 'block');
                $('.school_details').css('display', 'none');
                $('.employee_details').css('display', 'block');
                $('#legal_name_employer').attr('required', true);
                $('#sector').attr('required', true);


            }
        });
        $('.datepicker').datepicker();

        var $TABLE = $('#table_quick_view');
        $('.table-add').click(function (e) {
            var $clone = $TABLE.find('.custom_tr.hide').clone(true).removeClass('custom_tr').removeClass('hide');
            $TABLE.append($clone).focus();
            e.preventDefault();
        });

        var $TABLE_LEADER = $('#table_quick_view_leader');
        $('.leader-add').click(function (e) {
            var $clone = $TABLE_LEADER.find('.custom_tr_leader.hide').clone(true).removeClass('custom_tr_leader').removeClass('hide');
            $TABLE_LEADER.append($clone).focus();
            $(this).hide();
            $(document).find('.admin_leader_true').hide();
            $(document).find('.admin_leader_false').show();
            e.preventDefault();
        });
        var $TABLE_LEADER_ACADAMIC = $('#table_quick_view_leader_acadamic');
        $('.leader-add-acadamic').click(function (e) {
            var $clone = $TABLE_LEADER_ACADAMIC.find('.custom_tr_leader_acadamic.hide').clone(true).removeClass('custom_tr_leader_acadamic').removeClass('hide');
            $TABLE_LEADER_ACADAMIC.append($clone).focus();
            $(this).hide();
            $(document).find('.admin_leader_true').hide();
            $(document).find('.admin_leader_false').show();
            e.preventDefault();
        });
        var $TABLE_MEMBER = $('#table_quick_view_member');
        $('.member-add').click(function (e) {
            var is_blank_email = $TABLE_MEMBER.find('.ac-row-data-list').val();
            var count = $('.member-add').attr('data-count')
            $(this).attr('data-count', parseInt(count) + 1);
            var $clone = $TABLE_MEMBER.find('.custom_tr_member.hide').clone(true).removeClass('custom_tr_member').removeClass('hide');
            var member_type = $(document).find('.user_type').val();

            $TABLE_MEMBER.append($clone).focus();
            $(document).find('.memeber_clock_true').hide();
            $(document).find('.memeber_clock_false').show();
            e.preventDefault();
            var count = $(this).attr('data-count')
            if (count > 2) {
                $(document).find('.member-add').hide();
            }
        });
        var $TABLE_MEMBER_SCHOOL = $('#table_quick_view_member_school');
        $('.member-add-school').click(function (e) {
            var count = $('.member-add-school').attr('data-count')
            $(this).attr('data-count', parseInt(count) + 1);
            var $clone = $TABLE_MEMBER_SCHOOL.find('.custom_tr_member_school.hide').clone(true).removeClass('custom_tr_member_school').removeClass('hide');
            var member_type = $(document).find('.user_type').val();

            $TABLE_MEMBER_SCHOOL.append($clone).focus();
            $(document).find('.memeber_clock_true').hide();
            $(document).find('.memeber_clock_false').show();
            e.preventDefault();
            var count = $(this).attr('data-count')
            if (count >= 2) {
                $(document).find('.member-add-school').hide();
            }
        });


        var $TABLE_MENTOR = $('#table_quick_view_mentor');
        $('.mentor-add').click(function (e) {
            var $clone = $TABLE_MENTOR.find('.custom_tr_mentor.hide').clone(true).removeClass('custom_tr_mentor').removeClass('hide');
            $TABLE_MENTOR.append($clone).focus();
            $(this).hide();
            $(document).find('.admin_leader_true').hide();
            $(document).find('.admin_leader_false').show();
            e.preventDefault();
        });
        var $TABLE_AMB = $('#table_quick_view_ambassador');
        $('.amb-add').click(function (e) {
            var $clone = $TABLE_AMB.find('.custom_tr_ambassador.hide').clone(true).removeClass('custom_tr_ambassador').removeClass('hide');
            $TABLE_AMB.append($clone).focus();
            $(this).hide();
            $(document).find('.admin_leader_true').hide();
            $(document).find('.admin_leader_false').show();
            e.preventDefault();
        });

        var $TABLE_report = $('#report_table');
        $('.table-add_new').click(function (e) {
            $('.confirm_member').css('display', 'none');
            var $clone = $TABLE_report.find('.custom_tr.hide').clone(true).removeClass('custom_tr').removeClass('hide');
            $TABLE_report.append($clone).focus();
            e.preventDefault();
        });
        $('.table-remove-report').click(function () {
            var confirm_res = confirm("are you sure?")
            var aspirant_team = $(this).parents('tr').find('input[name="team_id"]').val();
            var member_type = $(this).parents('tr').find('select[name="user_type"]').val();
            if (confirm_res) {
                $(this).parents('tr').remove();
                ajax.jsonRpc("/remove_member_from_team",
                    "call", {
                        'aspirant_team': aspirant_team,
                        'member_type': member_type
                    }).then(function (result) {
                });
            }
        });
        $('.remove_document').click(function (e) {
            var document_id = $(this).attr('id');
            $(".modal-body #attachment_id").val(document_id);
            $(document).find('#remove_document_modal').modal('show');
            e.preventDefault();
        });
        $('.remove_attachment').click(function (e) {
            var attachment_id = $(document).find('input[name="attachment_id"]').val();
            window.location.reload();
            ajax.jsonRpc("/remove_attachment_from_team", "call", {
                'attachment_id': attachment_id,

            }).then(function (result) {

                window.location.reload();
            });
        });
        $('.table-remove').click(function () {

            var member_id = $(this).parents('tr').find('input[name="member_id"]').val();
            var user_type = $(this).parents('tr').find('.user_type').val();
            var count = $(document).find('.member-add').attr('data-count');
            var team_id = $(document).find('input[name="aspirant_team"]').val();

            if (user_type == 'Member') {
                $(document).find('.member-add').attr('data-count', parseInt(count) - 1);
            }
            var count = $(document).find('.member-add').attr('data-count');
            if (count < 3) {
                $(document).find('.member-add').show();
            }
            if (user_type == "Leader") {
                $(this).parents('.team-leader').find('.leader-add').show();
            }
            if (user_type == "Mentor") {
                $(this).parents('.team-leader').find('.mentor-add').show();
            }
            if (user_type == "Brand Ambassador") {
                $(this).parents('.team-leader').find('.amb-add').show();
            }
            if (member_id) {
                ajax.jsonRpc("/remove_member", "call", {
                    'member_id': member_id,
                    'team_id': team_id,
                    'member_type': user_type
                })
                    .then(function (result) {
                        if (result) {
                            $(this).parents('tr').find('.amb-add').css('display', 'block');
                            $(this).parents('tr').find('.mentor-add').css('display', 'block');
                        }
                    });
            }
            $(this).parents('tr').remove();
        });
        $('.table-remove-acadamic').click(function () {
            var member_id = $(document).find('input[name="member_id"]').val();
            var user_type = $(this).parents('tr').find('.user_type').val();
            var count = $(document).find('.member-add').attr('data-count');
            var count_school_member = $(document).find('.member-add-school').attr('data-count');
            var team_id = $(document).find('input[name="acadamic_team"]').val();
            if (user_type == 'Member') {
                $(document).find('.member-add').attr('data-count', parseInt(count) - 1);
                $(document).find('.member-add-school').attr('data-count', parseInt(count_school_member) - 1);
            }

            var count = $(document).find('.member-add').attr('data-count');
            if (count < 3 && user_type == 'Member') {
                $(document).find('.member-add').show();
            }

            var count_school_member = $(document).find('.member-add-school').attr('data-count');
            if (count_school_member < 2 && user_type == 'Member') {
                $(document).find('.member-add-school').show();
            }
            if (user_type == "Leader") {
                $(this).parents('.team-leader-acadamic').find('.leader-add-acadamic').show();
            }
            if (user_type == "Mentor") {
                $(this).parents('.team-leader-acadamic').find('.mentor-add').show();
            }
            if (user_type == "Brand Ambassador") {
                $(this).parents('.team-leader-acadamic').find('.amb-add').show();
            }
            if (member_id) {
                ajax.jsonRpc("/remove_member_acadamic", "call", {
                    'member_id': member_id,
                    'team_id': team_id,
                    'member_type': user_type
                })
                    .then(function (result) {
                        if (result) {
                            $(this).parents('tr').find('.amb-add').css('display', 'block');
                            $(this).parents('tr').find('.mentor-add').css('display', 'block');
                        }
                    });
            }
            $(this).parents('tr').remove();
        });

        $('.table-remove-school').click(function () {
            var member_id = $(document).find('input[name="member_id"]').val();
            var user_type = $(this).parents('tr').find('.user_type').val();
            var count_school_member = $(document).find('.member-add-school').attr('data-count');
            var team_id = $(document).find('input[name="high_school_team"]').val();
            if (user_type == 'Member') {
                $(document).find('.member-add-school').attr('data-count', parseInt(count_school_member) - 1);
            }

            var count_school_member = $(document).find('.member-add-school').attr('data-count');
            if (count_school_member < 2 && user_type == 'Member') {
                $(document).find('.member-add-school').show();
            }
            if (user_type == "Leader") {
                $(this).parents('.team-leader-acadamic').find('.leader-add-acadamic').show();
            }
            if (user_type == "Mentor") {
                $(this).parents('.team-leader-acadamic').find('.mentor-add').show();
            }
            if (user_type == "Brand Ambassador") {
                $(this).parents('.team-leader-acadamic').find('.amb-add').show();
            }
            if (member_id) {
                ajax.jsonRpc("/remove_member_school", "call", {
                    'member_id': member_id,
                    'team_id': team_id,
                    'member_type': user_type
                })
                    .then(function (result) {
                        if (result) {
                            $(this).parents('tr').find('.amb-add').css('display', 'block');
                            $(this).parents('tr').find('.mentor-add').css('display', 'block');
                        }
                    });
            }
            $(this).parents('tr').remove();
        });


        if (parseInt($('.amb-add').attr('count')) == 1) {
            $('.amb-add').css('display', 'none');
        } else {
            $('.amb-add').css('display', 'block');
        }
        if (parseInt($('.mentor-add').attr('count')) == 1) {
            $('.mentor-add').css('display', 'none');
        } else {
            $('.mentor-add').css('display', 'block');
        }
//        if(parseInt($('.leader-add').attr('count')) == 1){
//        	$('.leader-add').css('display','none');
//        }else{
//        	$('.leader-add').css('display','block');
//        }

        $('input[name="name"]').on('change', function () {
            var name = $(this).val();
            var country = $(this).parent().find('input[name="country"]').val();
            var school_name = $(document).find('input[name="school_name"]').val();
            ajax.jsonRpc("/check_team_name", 'call', {'team_name': name}).then(function (result) {
                if (result) {
                    $(document).find('#diffrent_team_name_modal').modal('show');
                }
                else {
                    $(document).find('.sys_name_new').val("Team," + name + " from " + school_name + " and " + country)
                }
            });
        });

        $('.team_email').on('change', function () {
            var email = $(this).val();
            var self = $(this);
            var user_type = $(this).parents('tr').find('.user_type').val();
            var acadamic = $(document).find("input[name='snr_academic_institution']").val();
            var jnr_highschool = $(document).find("input[name='jnr_high_school']").val();
            var admin_email = $(document).find('.admin_email').val();
            if ((acadamic && admin_email === email) && (user_type == 'Leader' || user_type == 'Member')) {
                $(document).find('#acadamic_leader_member_diffrent').modal('show');
                $(this).val('');

            }
            else if (admin_email == email) {
                self.parents('tr').find('.admin_leader_true').show();
                self.parents('tr').find('.admin_leader_false').hide();
            }
            if ((jnr_highschool && admin_email === email) && (user_type == 'Leader' || user_type == 'Member')) {
                $(document).find('#acadamic_leader_member_diffrent').modal('show');
                $(this).val('');

            }
            else if (admin_email == email) {
                self.parents('tr').find('.admin_leader_true').show();
                self.parents('tr').find('.admin_leader_false').hide();
            }
            else {
                ajax.jsonRpc("/check_user_team", "call", {'email': email})
                    .then(function (result) {
                        if (result.user_id) {
                            self.parents('tr').find('.request-join').show().attr('user_id', result['user_id']);
                        }
                        else {
                            self.parents('tr').find('.request-join').hide();
                            self.parents('tr').find('.create-user').hide();
                            self.parents('tr').find('.create_member').show();
                            self.parents('tr').find('.team_member_name').show();
                            self.parents('td').find('.admin_leader_true').hide();
                        }
                    });
            }
        });

        $('.user_type').on('change', function () {
            var user_type = $(this).val();
            var email = $(this).parents('tr').find('.team_email').val();
            var self = $(this);
            ajax.jsonRpc("/check_user_team", "call", {'email': email, 'user_type': user_type})
                .then(function (result) {
                    if (result) {
                        self.parents('tr').find('.create_member').show();
                        self.parents('tr').find('.team_member_name').show();
                    } else {
                        self.parents('tr').find('.create_member').hide();
                        self.parents('tr').find('.team_member_name').hide()
                    }
                });
        });

        var request_list = []
        $('.request-join').on('click', function () {
            var user_id = $(this).attr('user_id');
            var team_id = $(this).attr('team-id');
            var email = $(this).parents('tr').find('.team_email').val();
            var self = $(this);
            var user_type = $(this).parents('tr').find('.user_type').val();
            request_list.push({'email': email, 'user_type': user_type, 'user_id': user_id})
            self.parents('tr').find('.request-join').hide().attr('user_id', '');
            self.parents('tr').find('.create_member').hide();

//            $(".ac-row-data-list").each(function () {
//                var email = $(this).find("input[name='email']").val();
//                var user_type = $(this).find(".user_type").val();
//                if (email && user_type) {
//                    list_of_member.push({'email': email, 'user_type': user_type});
//                }
//            });
//            
//            
//            ajax.jsonRpc("/request_to_join", "call", {'user_id': user_id, 'team_id': team_id, 'user_type':user_type,})
//                .then(function (result) {
//                    if (result) {
//                        self.parents('tr').find('.request-join').hide().attr('user_id', '');
//                        self.parents('tr').find('.create_member').hide();
//                    } else {
//                        self.parents('tr').find('.request-join').show().attr('user_id', result['user_id']);
//                        self.parents('tr').find('.confirm_member').show();
//                        self.parents('tr').find('.create_member').hide();
//                    }
//                });
        });
        $('.create_member').on('click', function () {
            var email = $(this).parents('tr').find('.team_email').val();
            var name = $(this).parents('tr').find('.team_member_name').val();
            var team_id = $(this).attr('team-id')
            var user_type = $(this).parents('tr').find('.user_type').val();
            var year = $(this).parents('tr').find('.competition_year').val();
            var from_acadamic = $(this).parents('tr').find('.from_acadamic').val();
            var from_aspirant = $(this).parents('tr').find('.from_aspirant').val();
            var from_employer = $(this).parents('tr').find('.from_employer').val();
            var from_jnr_school = $(this).parents('tr').find('.from_jnr_school').val();
            var self = $(this);
            ajax.jsonRpc("/create_new_member", "call", {
                'email': email,
                'name': name,
                'user_type': user_type,
                'year': year,
                'team_id': team_id,
                'from_acadamic': from_acadamic,
                'from_aspirant': from_aspirant,
                'from_employer': from_employer,
                'from_jnr_school': from_jnr_school,
            })
                .then(function (result) {
                    if (result) {
                        self.parents('tr').find('.create_member').hide();
                        alert("Email already exist...")
                    } else {
                        $('.confirm_member').css('display', 'block');
                        self.parents('tr').find('.create_member').hide();
                        self.parents('tr').find('.team_member_name').hide()
                    }
                });
        });

        $('.confirm_mentor').on('click', function (e) {
            e.preventDefault();
            var pdf_uploaded = $(document).find('.file_uploaded').val();
            var doc_uploaded = $(document).find('.file_uploaded_doc').val();
            var popup_id = $(document).find('#upload_file_popup').val();
            var aknowledgement = $(document).find('.confirm_report').val();
            var submit_form = $(document).find('.confirm_report').val();

            if (pdf_uploaded && doc_uploaded) {
                if ($('#confirm_member_mentor1').is(':visible')) {
                    $(document).find('#confirm_member_mentor').hide();
                }
                else {
                    $(document).find('#confirm_member_mentor').hide();
                    $(document).find('.acknowledge').css("display", "block");
//        				$(document).find('.confirm_report').css("display", "block");
                }
            }
            else {
                $(document).find('#upload_file_popup').modal('show');
            }
        });

        $('.confirm_member').on('click', function (e) {
            e.preventDefault();
            var self = $(this).parents('.form');
            var pdf_uploaded = $(document).find('.file_uploaded').val();
            var doc_uploaded = $(document).find('.file_uploaded_doc').val();
            var popup_id = $(document).find('#upload_file_popup').val();
            var aknowledgement = $(document).find('.acknowledge').val();
            var submit_form = $(document).find('.confirm_report').val();
            var email = $(this).parents('tr').find('input[name="email"]').val();
            var aspirant_id = $(this).parents('tr').find('input[name="snr_aspirants"]').val();
            var aspirant_team = $(this).parents('tr').find('input[name="team_id"]').val();
            var member_type = $(this).parents('tr').find('select[name="user_type"]').val();
            var list_of_member = [];

            if (pdf_uploaded && doc_uploaded) {
                if ($('#confirm_member_mentor').is(':visible')) {
                    $(document).find('#confirm_member_mentor1').hide()
                }
                else {
                    $(document).find('#confirm_member_mentor1').hide();
                    $(document).find('.acknowledge').css("display", "block");
//    				$(document).find('.confirm_report').css("display", "block");
                }
            }
            else {
                $(document).find('#upload_file_popup').modal('show');

            }
            $(".ac-row-data-list").each(function () {
                var email = $(this).find("input[name='email']").val();
                var user_type = $(this).find(".user_type").val();
                if (email && user_type) {
                    list_of_member.push({'email': email, 'user_type': user_type});
                }
            });

            ajax.jsonRpc("/update_team_from_report", 'call', {
                'aspirant_id': aspirant_id,
                'email': email,
                'aspirant_team': aspirant_team,
                'member_type': member_type,
                'list_of_member': list_of_member,
            }).then(function (data) {
                if (data) {
                    alert('Record Updated Succesfully...')
                }
            });
        });
        $("#report_form").submit(function (event) {
            $(document).find('.loader_report_final').css("display", "block");
//    	 
        });

//       $('#confirm_report').on('click',function(e){
//    	   e.preventDefault();
//    	   alert();
//    	   var team_id = $(document).find('input[name="team_id"]').val();
//    	   $(document).find('.loader_report_final').css("display","block");
//    	   setTimeout(function(){
//    		   return true
//    	   },1000)
////    	 
////    	   $(document).find('.loader_report_final').css("display","none");
//       	});
        $('#state_id').on('change', function () {
            var state_id = $(this).val();
            ajax.jsonRpc("/get_country", 'Call', {
                'state_id': state_id,
            }).then(function (result) {
                if (result) {
                    $('#country_id option').each(function () {
                        if ($(this).val() == result.id) {
                            $(this).attr('selected', 'selected');
                        }
                    });
                }
            });
        });
        $('.create_team').on('click', function () {
            var self = $(this).parents('.form');
            var name = $(document).find('input[name="name"]').val();
            var sys_name = $(document).find('input[name="sys_name"]').val();
            var aspirant_id = $(document).find('input[name="snr_aspirants"]').val();
            var aspirant_team = $(document).find('input[name="aspirant_team"]').val();
            var new_list_member = request_list;
            var list_of_member = [];

            if ($(document).find('input[name="name"]').val().length < 1) {
                alert("Please Fill in Team Name.");
                $(this).focus();
                return false;
            }
            $(".ac-row-data-list").each(function () {
                var email = $(this).find("input[name='email']").val();
                var user_type = $(this).find(".user_type").val();
                var member_status = $(this).find("input[name='member_status']").val();

                if (email && user_type) {
                    list_of_member.push({'email': email, 'user_type': user_type, 'member_status': member_status});
                }
            });
            ajax.jsonRpc("/create_team", 'call', {
                'aspirant_id': aspirant_id,
                'name': name,
                'sys_name': sys_name,
                'list_of_member': list_of_member,
                'aspirant_team': aspirant_team,
                'member_request_list': new_list_member,
            }).then(function (data) {
                if (data['success']) {
                    window.location.replace("/cfo_senior");
                } else if (data['member_limit_error']) {
                    alert('You can not add more than 3 members');
                } else if (data['leader_limit_error']) {
                    alert('You can not add more than 1 Leader');
                } else if (data['brand_limit_error']) {
                    alert('You can not add more than 1 Brand Ambassador');
                } else if (data['team_error']) {
                    alert('You can not create more than 1 team');
                } else {
                    alert('One or More Emails you have added have not been created, Please Click "Create New User" Button on all added Emails or Click "Remove" Button');
                }
            });
        });

        $('.create_acadamic_team').on('click', function () {
            var self = $(this).parents('.form');
            var name = $(document).find('input[name="name"]').val();
            var sys_name = $(document).find('input[name="sys_name"]').val();
            var acadamic_id = $(document).find('input[name="snr_academic_institution"]').val();
            var acadamic_team = $(document).find('input[name="acadamic_ids"]').val();
            var new_list_member = request_list;

            var list_of_member = [];

            if ($(document).find('input[name="name"]').val().length < 1) {
                alert("Please Fill in Team Name.");
                $(this).focus();
                return false;
            }

            $(".ac-row-data-list").each(function () {
                var email = $(this).find("input[name='email']").val();
                var user_type = $(this).find(".user_type").val();
                if (email && user_type) {
                    list_of_member.push({'email': email, 'user_type': user_type});
                }
            });
            ajax.jsonRpc("/create_acadamic_team", 'call', {
                'snr_academic_institution': acadamic_id,
                'name': name,
                'sys_name': sys_name,
                'list_of_member': list_of_member,
                'acadamic_team': acadamic_team,
                'acadamic_member_list': new_list_member,
            }).then(function (data) {
                if (data['success']) {
                    window.location.replace("/cfo_senior");
                } else if (data['member_limit_error']) {
                    alert('You can not add more than 3 members');
                } else if (data['leader_limit_error']) {
                    alert('You can not add more than 1 Leader');
                } else if (data['brand_limit_error']) {
                    alert('You can not add more than 1 Brand Ambassador');
                } else if (data['team_error']) {
                    alert('You can not create more than 1 team');
                } else {
                    alert('One or More Emails you have added have not been created, Please Click "Create New User" Button on all added Emails or Click "Remove" Button');
                }
            });
        });

        $('.create_employer_team').on('click', function () {
            var self = $(this).parents('.form');
            var name = $(document).find('input[name="name"]').val();
            var sys_name = $(document).find('input[name="sys_name"]').val();
            var snr_employers_id = $(document).find('input[name="snr_employers"]').val();
            var employers_team = $(document).find('input[name="employers_team"]').val();
            var new_list_member = request_list;

            var list_of_member = [];
            if ($(document).find('input[name="name"]').val().length < 1) {
                alert("Please Fill in Team Name.");
                $(this).focus();
                return false;
            }

            $(".ac-row-data-list").each(function () {
                var email = $(this).find("input[name='email']").val();
                var user_type = $(this).find(".user_type").val();
                if (email && user_type) {
                    list_of_member.push({'email': email, 'user_type': user_type});
                }
            });
            ajax.jsonRpc("/create_employers_team", 'call', {
                'snr_employers': snr_employers_id,
                'name': name,
                'sys_name': sys_name,
                'list_of_member': list_of_member,
                'employer_team': employers_team,
                'employer_member_list': new_list_member,
            }).then(function (data) {
                if (data['success']) {
                    window.location.replace("/cfo_senior");
                } else if (data['member_limit_error']) {
                    alert('You can not add more than 3 members');
                } else if (data['leader_limit_error']) {
                    alert('You can not add more than 1 Leader');
                } else if (data['brand_limit_error']) {
                    alert('You can not add more than 1 Brand Ambassador');
                } else if (data['team_error']) {
                    alert('You can not create more than 1 team');
                } else {
                    alert('One or More Emails you have added have not been created, Please Click "Create New User" Button on all added Emails or Click "Remove" Button');
                }
            });
        });

        $('.create_team_junior').on('click', function () {
            var self = $(this).parents('.form');
            var name = $(document).find('input[name="name"]').val();
            var sys_name = $(document).find('input[name="sys_name"]').val();
            var aspirant_id = $(document).find('input[name="jnr_aspirants"]').val();
            var aspirant_team = $(document).find('input[name="aspirant_team"]').val();
            var new_list_member = request_list;
            var list_of_member = [];


            if ($(document).find('input[name="name"]').val().length < 1) {
                alert("Please Fill in Team Name.");
                $(this).focus();
                return false;
            }
            $(".ac-row-data-list").each(function () {
                var email = $(this).find("input[name='email']").val();
                var user_type = $(this).find(".user_type").val();
                var member_status = $(this).find("input[name='member_status']").val();

                if (email && user_type) {
                    list_of_member.push({'email': email, 'user_type': user_type, 'member_status': member_status});
                }
            });
            ajax.jsonRpc("/create_team_junior", 'call', {
                'aspirant_id': aspirant_id,
                'name': name,
                'sys_name': sys_name,
                'list_of_member': list_of_member,
                'aspirant_team': aspirant_team,
                'member_request_list': new_list_member,
            }).then(function (data) {
                if (data['success']) {
                    window.location.replace("/cfo_senior");
                } else if (data['member_limit_error']) {
                    alert('You can not add more than 3 members');
                } else if (data['leader_limit_error']) {
                    alert('You can not add more than 1 Leader');
                } else if (data['brand_limit_error']) {
                    alert('You can not add more than 1 Brand Ambassador');
                } else if (data['team_error']) {
                    alert('You can not create more than 1 team');
                } else {
                    alert('One or More Emails you have added have not been created, Please Click "Create New User" Button on all added Emails or Click "Remove" Button');
                }
            });
        });

        $('.create_high_school_team').on('click', function () {
            var self = $(this).parents('.form');
            var name = $(document).find('input[name="name"]').val();
            var sys_name = $(document).find('input[name="sys_name"]').val();
            var jnr_high_school = $(document).find('input[name="jnr_high_school"]').val();
            var high_school_team = $(document).find('input[name="high_school_team"]').val();
            var new_list_member = request_list;

            var list_of_member = [];

            if ($(document).find('input[name="name"]').val().length < 1) {
                alert("Please Fill in Team Name.");
                $(this).focus();
                return false;
            }

            $(".ac-row-data-list").each(function () {
                var email = $(this).find("input[name='email']").val();
                var user_type = $(this).find(".user_type").val();
                if (email && user_type) {
                    list_of_member.push({'email': email, 'user_type': user_type});
                }
            });
            ajax.jsonRpc("/create_high_school_team", 'call', {
                'jnr_high_school': jnr_high_school,
                'name': name,
                'sys_name': sys_name,
                'list_of_member': list_of_member,
                'high_school_team': high_school_team,
                'highschool_member_list': new_list_member,
            }).then(function (data) {
                if (data['success']) {
                    window.location.replace("/cfo_junior");
                } else if (data['member_limit_error']) {
                    alert('You can not add more than 3 members');
                } else if (data['leader_limit_error']) {
                    alert('You can not add more than 1 Leader');
                } else if (data['brand_limit_error']) {
                    alert('You can not add more than 1 Brand Ambassador');
                } else if (data['team_error']) {
                    alert('You can not create more than 1 team');
                } else {
                    alert('One or More Emails you have added have not been created, Please Click "Create New User" Button on all added Emails or Click "Remove" Button');
                }
            });
        });
    });
});
$(document).on('ready', function () {
    var menu = (window.location.hash).split('#');
    $('.add_menu_side').on('click', function (ev) {
        $(ev.currentTarget).parents('.label_link_list.row').find('.add_menu_side').removeClass('active');
        $(ev.currentTarget).parents('section').find('.col-md-1').removeClass('active');
        $(ev.currentTarget).parents('section').find('.content').addClass('hidden').removeClass('active');
        $(ev.currentTarget).addClass('active');
        $(ev.currentTarget).parents('section').find('.col-md-1.' + $(ev.currentTarget).attr('data-current-menu')).addClass('active');
        $(ev.currentTarget).parents('section').find('.content.' + $(ev.currentTarget).attr('data-current-menu')).removeClass('hidden').addClass('active');
        $(document).find('.breadcrumb').find('li.active').removeClass('active');
        $(document).find('.breadcrumb').find('li.cfo_menu').remove();
        $(document).find('.breadcrumb').append('<li class="active cfo_menu">' + $(ev.currentTarget).text() + '</li>')
    });
    $(document).on('click', '.menu-icon', function (ev) {
        $(ev.currentTarget).parents('section').find('.add_menu_side').removeClass('active');
        $(ev.currentTarget).parents('section').find('.col-md-1').removeClass('active');
        $(ev.currentTarget).parents('section').find('.content').addClass('hidden').removeClass('active');
        $(ev.currentTarget).addClass('active');
        $(ev.currentTarget).parents('section').find('.add_menu_side.' + $(ev.currentTarget).attr('data-current-menu')).addClass('active');
        $(ev.currentTarget).parents('section').find('.content.' + $(ev.currentTarget).attr('data-current-menu')).removeClass('hidden').addClass('active');
        $(document).find('.breadcrumb').find('li.active').removeClass('active');
        $(document).find('.breadcrumb').find('li.cfo_menu').remove();
        $(document).find('.breadcrumb').append('<li class="active cfo_menu">' + $(ev.currentTarget).find('a').text() + '</li>');
    });

    if (typeof $(document).find('.add_menu_side').html() != 'undefined') {
        if (menu[1]) {
            $(document).find('.add_menu_side.' + menu[1]).trigger('click');
        } else {
            $(document).find('.add_menu_side:first').trigger('click');
        }
    }
    $(document).find('.label_link_list.row').removeAttr('style');
    $(document).on('click', '.onlymobilebtn', function () {
        $(".label_link_list").slideToggle("medium", function () {
        });
    });
});
