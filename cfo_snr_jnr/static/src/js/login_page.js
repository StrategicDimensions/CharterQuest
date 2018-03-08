odoo.define('cfo_snr_jnr.login_page', function (require) {
    document.write("<script src='https://www.google.com/recaptcha/api.js'></script>");
    var ajax = require('web.ajax');
    $(document).ready(function () {
//
//	$(".btn_login_js").click(function() {
//        var username = $('#username').val();
//        var pswd = $('#pswd').val();
//        console.log('username',username);
//        console.log('pswd',pswd);
//        ajax.jsonRpc("/login_check", 'call', {'username': username, 'pswd': pswd}).then(function(data){
//            if(!data){
//                alert('Incorrect username/password.!')
//            }
//            if(data){
//                location.replace('/user_details');hot to know webscription version in odoo
//            }
//        });
//    });
//
//	$('.loginBtn').click(function (){
//		var username = $('#login').val();
//        var pswd = $('#password').val();
//        console.log(username)
//        console.log(pswd)
//		ajax.jsonRpc("/web_login", 'call', {'username': username, 'pswd': pswd}).then(function(data){
//            if(!data){
//                alert('Incorrect username/password.!')
//            }
//            if(data){
//                location.replace('/user_details');
//            }
//        });
//	});
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
            $('.employee_details').css('display', 'none');
            $('.school_details').css('display', 'block');
        } else {
            $('.school_details').css('display', 'none');
            $('.employee_details').css('display', 'block');
        }
        $('input[name="user_type"]').on('change', function () {
            if ($(this).val() == 'student') {
                $('.school_details').css('display', 'block');
                $('.employee_details').css('display', 'none');
            } else {
                $('.school_details').css('display', 'none');
                $('.employee_details').css('display', 'block');
            }
        });
        $('.datepicker').datepicker();

        var $TABLE = $('#table_quick_view');
        $('.table-add').click(function (e) {
            var $clone = $TABLE.find('.custom_tr.hide').clone(true).removeClass('custom_tr').removeClass('hide');
            $TABLE.append($clone).focus();
            e.preventDefault();
        });
        $('.table-remove').click(function () {
            var member_id = $(this).parents('tr').attr('member_id');
            if (member_id) {
                ajax.jsonRpc("/remove_member", "call", {'member_id': member_id})
                    .then(function (result) {
                    });
            }
            $(this).parents('tr').remove();
        });
        $('input[name="name"]').on('change', function () {
            var name = $(this).val();
            var country = $(this).parent().find('input[name="country"]').val();
            var state_name = $(this).parent().find('input[name="state"]').val();
            $(this).parents(".form").find('.sys_name_new').val("Team " + name + " from " + state_name + "," + country)
        });
        $('.team_email').on('change', function () {
            var email = $(this).val();
            var self = $(this);
            var user_type = $(this).parents('tr').find('.user_type').val();
            ajax.jsonRpc("/check_user_team", "call", {'email': email})
                .then(function (result) {
                    if (result.user_id) {
                        self.parents('tr').find('.request-join').show().attr('user_id', result['user_id']);
                    } else {
                        self.parents('tr').find('.request-join').hide();
                        self.parents('tr').find('.create-user').hide()
                    }
                });
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
        $('.request-join').on('click', function () {
            var user_id = $(this).attr('user_id');
            var team_id = $(this).attr('team-id');
            var email = $(this).parents('tr').find('.team_email').val();
            var self = $(this);
            var user_type = $(this).parents('tr').find('.user_type').val();
            ajax.jsonRpc("/request_to_join", "call", {'user_id': user_id, 'team_id': team_id, 'user_type':user_type,})
                .then(function (result) {
                    if (result) {
                        self.parents('tr').find('.request-join').hide().attr('user_id', '');
                    } else {
                        self.parents('tr').find('.request-join').show().attr('user_id', result['user_id']);
                    }
                });
        });
        $('.create_member').on('click', function () {
            var email = $(this).parents('tr').find('.team_email').val();
            var name = $(this).parents('tr').find('.team_member_name').val();
            var user_type = $(this).parents('tr').find('.user_type').val();
            var year = $(this).parents('tr').find('.competition_year').val();
            var self = $(this);
            ajax.jsonRpc("/create_new_member", "call", {'email': email, 'name': name,'user_type':user_type,'year':year})
                .then(function (result) {
                    if (result) {
                        alert("Email already exist...")
                    } else {
                        self.parents('tr').find('.create_member').hide();
                        self.parents('tr').find('.team_member_name').hide()
                    }
                });
        });
        $('.create_team').on('click', function () {
            var self = $(this).parents('.form');
            var name = self.find('input[name="name"]').val();
            var sys_name = self.find('input[name="sys_name"]').val();
            var aspirant_id = self.find('input[name="snr_aspirants"]').val();
            var aspirant_team = self.find('input[name="aspirant_team"]').val();
            var list_of_member = [];
            if(self.find('input[name="name"]').val().length < 1){
                alert("Team name must be required !!!!.");
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
            ajax.jsonRpc("/create_team", 'call', {
                'aspirant_id': aspirant_id,
                'name': name,
                'sys_name': sys_name,
                'list_of_member': list_of_member,
                'aspirant_team': aspirant_team
            })
                .then(function (data) {
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
                        alert('Email not found');
                    }
                });
        });
        $('.create_acadamic_team').on('click', function () {
            var self = $(this).parents('.form');
            var name = self.find('input[name="name"]').val();
            var sys_name = self.find('input[name="sys_name"]').val();
            var acadamic_id = self.find('input[name="snr_academic_institution"]').val();
            var acadamic_team = self.find('input[name="acadamic_ids"]').val();
            var list_of_member = [];
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
                'acadamic_team': acadamic_team
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
                    alert('Email not found');
                }
            });
        });
    });

})
;