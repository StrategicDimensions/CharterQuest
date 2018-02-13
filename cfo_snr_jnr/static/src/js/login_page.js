odoo.define('cfo_snr_jnr.login_page', function (require) {
	document.write("<script src='https://www.google.com/recaptcha/api.js'></script>");
	var ajax = require('web.ajax');
	$(document).ready(function() {
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
		$('.oe_signup_form').on('submit',function(e){
			var response = grecaptcha.getResponse();
			if(response.length == 0){
				$('.g-recaptcha').css('border','1px solid red');
				e.preventDefault();
				$('button[type="submit"]').removeAttr('disabled');
			}
		});
		$("#cfo_source").change(function() {
	    	if (this.value != 'Other')
			{
	    		$('#other_source').hide();
			}
	    	else
			{
	    		$('#other_source').show();
			}

	    	if (this.value != 'Social Media')
			{
	    		$('#socialmedia_source').hide();
			}
	    	else
			{
	    		$('#socialmedia_source').show();
			}
	    });
		$('#cfo_competition').val('');
		$('#cfo_competition').change(function(){
			ajax.jsonRpc("/get_member_types","call",{'val':$(this).val()}).then(function(result){
				if (result){
					var html = '';
					 for(var i=0;i<result.length;i++){
                         html += "<option>"+result[i]+"</option>";
                     }
                     $('#cfo_membertype').html(html);
                   }
			});
		});
	});
});