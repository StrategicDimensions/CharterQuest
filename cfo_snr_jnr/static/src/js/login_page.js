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
//                location.replace('/user_details');
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
            ajax.jsonRpc("/check_user_team", "call", {'email': email})
                .then(function (result) {
                    if (result) {
                        self.parents('tr').find('.request-join').show();
                    } else {
                        self.parents('tr').find('.request-join').hide();
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
            $(".ac-row-data-list").each(function () {
                var email = $(this).find("input[name='email']").val();
                var user_type = $(this).find(".user_type").val();
                list_of_member.push({'email': email, 'user_type': user_type});
            });
            ajax.jsonRpc("/create_team", 'call', {
                'aspirant_id': aspirant_id,
                'name': name,
                'sys_name': sys_name,
                'list_of_member': list_of_member,
                'aspirant_team': aspirant_team
            })
                .then(function (data) {
                    if(data){
                        window.location.replace("/cfo_senior");
                    }else{
                        alert('Email is not found')
                    }
                });
        });
    });

})
;