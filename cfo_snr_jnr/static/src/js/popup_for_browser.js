//odoo.define('cfo_snr_jnr.popup_for_browser', function (require) {
//
//    if( navigator.userAgent.indexOf("Chrome") != -1){
//        $(window).ready(function(){
////                alert("Hello, world");
//            setTimeout(function () {
//                console.log('All assets are loaded')
//
//            }, 5000);
//        });
//    }
//
//});
/* © 2015 Antiun Ingeniería, S.L.
 * © 2015 Lorenzo Battistini - Agile Business Group
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

odoo.define('cfo_snr_jnr.cookie_notice', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var base = require('web_editor.base');

    base.ready().done(function () {
    if( (navigator.userAgent.indexOf("Chrome") != -1) || (navigator.userAgent.indexOf("Firefox") != -1)){
         $(document).find('#website_cookie_notice').css("display","none");
       }
     $(".cc-cookies .btn-primary").click(function (e) {
            e.preventDefault();
            ajax.jsonRpc('/cfo_snr_jnr/ok', 'call')
                .then(function (data) {
                    if (data.result === 'ok') {
                        $(e.target).closest(".cc-cookies").hide();
                    }
                });
        });
    });

}
);