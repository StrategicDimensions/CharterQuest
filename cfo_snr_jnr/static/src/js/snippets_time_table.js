odoo.define('cfo_snr_jnr.snippets_time_table', function (require) {

    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var qweb = core.qweb;
    var _t = core._t;
    ajax.loadXML('/cfo_snr_jnr/static/src/xml/snippet_custom.xml', qweb);
    options.registry.cfo_snr_jnr_timetable = options.Class.extend({
        start: function (editMode) {
//        alert()
            var self = this;
            this._super();
            if (!editMode) {
//                self.$el.find(".cfo_snr_jnr_time_table_part").on("click", _.bind(self.cfo_menu_tabs_configuration, self));
//                self.$el.find(".cfo_snr_jnr_remove_menu_tabs").on("click", _.bind(self.cfo_menu_tabs_remove, self));
            }
        },
        onBuilt: function () {
            var self = this;
            this._super();
            if (this.cfo_timetable_configuration()) {
                this.cfo_timetable_configuration().fail(function () {
                    self.getParent()._removeSnippet();
                });
            }
        },
//        cfo_menu_tabs_remove: function () {
//        	var self = this;
//           	self.$target.find('.nav.nav-tabs li.active').remove();
//			self.$target.find('.tab-content.tabs .tab-pane.active').remove();
//			self.$target.find('.nav.nav-tabs li:first').addClass('active')
//			self.$target.find('.tab-content.tabs .tab-pane:first').addClass('active')
//        },
        cfo_timetable_configuration: function (type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                $(document).find('#cfo_timetable_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_timetable_snippet"));
                self.$modal.appendTo('body');
                self.$modal.modal()
                $sub_data = self.$modal.find("#timetable_event_submit");
                $fillter_timetable=self.$modal.find(".fillter_timetable");
                $sub_data.on('click', function (event) {
                    var id=$('#event_category').val();
                    var domain=[('id','=',id)]
                    rpc.query({
                        model: 'event.type',
                        method: 'get_qualification_level',
                        args: [id],
                    }).then(function(data){
//                        $(document).find('#course_code_select').html("")
                        self.$target.find('select[name="level_select"]').html("")
                        var level=[]
                        for(var i=0; i<data.length; i++)
                        {
                            level.push('<option value=' + data[i].id + '>' + data[i].name + '</option>\n')
                        }
                        self.$target.find('select[name="level_select"]').html(level)
                        self.$target.find(".fillter_timetable").attr('data-id',id);
                    });


//                    self.$target.find('.tab-content.tabs').append(content_html);
                });
            } else {
                return false;
            }
        },

//        $fillter_timetable=self.$modal.find(".fillter_timetable");
//        self.$modal.find(".fillter_timetable").on('click',function(){
//            alert()
//        });

    });



    $(document).ready(() => {

		let url = location.href.replace(/\/$/, "");

		if (location.hash) {
			const hash = url.split("#");
			$('#cfo_menu_with_tabs_div_panel a[href="#' + hash[1] + '"]').tab("show");
			url = location.href.replace(/\/#/, "#");
			history.replaceState(null, null, url);
			setTimeout(() => {
				$(window).scrollTop(0);
			}, 400);
		}

		$('.cfo_menu_with_tabs_a_panel').on("click", function(event) {
			if (event.ctrlKey)
			{
				const hash = $(this).attr("external-href");
				window.open(hash);
			}
			else{
				let newUrl;
				const hash = $(this).attr("href");
				if (hash == "#home") {
					newUrl = url.split("#")[0];
				} else {
					newUrl = url.split("#")[0] + hash;
				}
				newUrl += "/";
				history.replaceState(null, null, newUrl);
			}
		});
        var self = this;
        var color_picker=self.$modal.find("#cfo-cnr-jnr-color-picker");
		$("#cfo-cnr-jnr-color-picker").on("click",function(e){
            alert()
            var id="#"+ e.toElement.id;
            var data_id=$(id).attr('data')
                var hexVal=null
            $(id).spectrum();
            $(id).on('move.spectrum', function(e, tinyColor) {
                hexVal = tinyColor.toHexString();
                $(id).css('backgroundColor', '#' + hexVal);
            });
            $('.sp-choose').on("click",  function(){
                  ajax.jsonRpc('/set_color', 'call',{
                        'data_id':data_id,
                        'hex_val':hexVal
                  })

            });
        });



    });


});