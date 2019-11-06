odoo.define('cfo_snr_jnr.snippets_card_block', function (require) {

    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    ajax.loadXML('/cfo_snr_jnr/static/src/xml/snippet_custom.xml', qweb);
    options.registry.cfo_snr_jnr_material_cards = options.Class.extend({
        start: function (editMode) {
            var self = this;
            this._super();
			self.availableTags = [];
	    	self._rpc({
	    		model: 'res.partner',
	    		method: 'search_read',
	    		domain: [['is_lecturer', '=', true]],
	    		fields: ['id','name', 'image', 'comment', 'function'],
	    	}, {async: false}).then(function(partners){
	    		if(partners.length > 0){
	    			$.each(partners, function (key, val){
	    				self.availableTags.push({'label': val.name, 'value': val.name, 'id':val.id, 'image': val.image, 'comment': val.comment, 'qualification': val.function})
	    			});
	    		}
	    	});
	    	if (!editMode) {
                self.$el.find(".cfo_snr_jnr_add_card").on("click", _.bind(self.cfo_add_card, self));
                self.$el.find(".cfo_snr_jnr_remove_card").on("click", _.bind(self.cfo_remove_card, self));
            }
        },
        onBuilt: function () {
            var self = this;
            this._super();
            if (this.cfo_cards_block_configuration()) {
                this.cfo_cards_block_configuration().fail(function () {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cfo_remove_card: function(type, value){
			var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
				self.$target.find('.material-card.active').remove()
            } else {
                return false;
            }
		},
        cfo_add_card: function(type, value){
			var self = this;
			var $target = self.$target.find('.material-card.active');
            if (type != undefined && type.type == "click" || type == undefined) {
				$(document).find('#cfo_cards_block_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_cards_blocks_cfo"));
                self.$modal.appendTo('body');
                self.$modal.modal();

				var $is_facebook = false,
					$is_twitter = false,
					$is_linkedin = false,
					$is_google = false;

                self.$modal.find('#is_facebook').on('change', function() {
					if($(this).prop("checked") == true){
                		self.$modal.find(".facebook_is").removeClass('hidden');
                		$is_facebook = true;
					}
            		else if($(this).prop("checked") == false){
						self.$modal.find(".facebook_is").addClass('hidden');
						$is_facebook = false;
            		}
				});

				self.$modal.find('#is_twitter').on('change', function() {
					if($(this).prop("checked") == true){
                		self.$modal.find(".twitter_is").removeClass('hidden');
                		$is_twitter = true;
					}
            		else if($(this).prop("checked") == false){
						self.$modal.find(".twitter_is").addClass('hidden');
						$is_twitter = false;
            		}
				});

				self.$modal.find('#is_linkedin').on('change', function() {
					if($(this).prop("checked") == true){
                		self.$modal.find(".linkedin_is").removeClass('hidden');
                		$is_linkedin = true;
					}
            		else if($(this).prop("checked") == false){
						self.$modal.find(".linkedin_is").addClass('hidden');
						$is_linkedin = false;
            		}
				});

				self.$modal.find('#is_google').on('change', function() {
					if($(this).prop("checked") == true){
                		self.$modal.find(".google_is").removeClass('hidden');
                		$is_google = true;
					}
            		else if($(this).prop("checked") == false){
						self.$modal.find(".google_is").addClass('hidden');
						$is_google = false;
            		}
				});

                var $lecturer_id = self.$modal.find("#lecturer_id"),
                	$lec_name = '',
                	$lec_image = '',
                	$lec_id = '',
                	$lec_desc = '',
                	$lec_qualification = '',
                	$card_color = self.$modal.find("#color_card"),
                	$sub_data = self.$modal.find("#cards_block_submit");

				$lecturer_id.autocomplete({
      				source: self.availableTags,
				 	minLength: 0,
				 	select: function (event, ui) {
						$lec_name = ui.item.value;
						$lec_id = ui.item.id;
						$lec_desc = ui.item.comment;
						$lec_image = ui.item.image;
						$lec_qualification = ui.item.qualification;
					},
    			}).blur(function(){
    				$(this).autocomplete('enable');
				}).focus(function () {
    				$(this).autocomplete('search', '');
				});
				$sub_data.on('click', function () {

					var card_color = '';
					var $facebook_url = self.$modal.find('#facebook_href').val(),
					$twitter_url = self.$modal.find('#twitter_href').val(),
					$linkedin_url = self.$modal.find('#linkedin_href').val(),
					$google_url = self.$modal.find('#google_href').val();
                	if ($card_color.val()) {
                        card_color = $card_color.val();
                    } else {
                        card_color = 'Red';
                    }
                    var lec_name=$lec_name.replace(" ","-");
					var html = `
						<div class="col-md-3 col-sm-6 col-xs-12">
							<div class="material-card `+ card_color +`">
								<h2>
									<span class="lecturer-name">` + $lec_name + `</span>
									<strong class="lecturer-qualification">
										` + $lec_qualification + `
									</strong>
								</h2>
								<div class="mc-content">
									<div class="img-container">
										<img class="img-responsive lecturer-image" src="data:image/jpeg;base64,`+ $lec_image +`"/>
									</div>
									<div class="mc-description">
										` + $lec_desc + `
									</div>
								</div>
								<a class="mc-btn-action">
									<i class="fa fa-bars"/>
								</a>
								<div class="mc-footer">
									<h4>
										<button class="details_view_lecturer" data-href="/`+lec_name+`/`+ $lec_id +`">View Profile</button>
									</h4>
									<div class="social_icons">
								`;
								if ($is_facebook){
									html += '<a class="fa fa-fw fa-facebook" href="'+ $facebook_url +'"/>';
								}
								if ($is_twitter){
									html += '<a class="fa fa-fw fa-twitter" href="'+ $twitter_url +'"/>';
								}
								if ($is_linkedin){
									html += '<a class="fa fa-fw fa-linkedin" href="'+ $linkedin_url +'"/>';
								}
								if ($is_google){
									html += '<a class="fa fa-fw fa-google-plus" href="'+ $google_url +'"/>';
								}
								html += `</div></div>
							</div>
						</div>
					`;
					$target.parents('.row.active-with-click').append(html);
                });
            } else {
                return false;
            }
        },

        cfo_cards_block_configuration: function (type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                $(document).find('#cfo_cards_block_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_cards_blocks_cfo"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $is_facebook = false,
					$is_twitter = false,
					$is_linkedin = false,
					$is_google = false;

                self.$modal.find('#is_facebook').on('change', function() {
					if($(this).prop("checked") == true){
                		self.$modal.find(".facebook_is").removeClass('hidden');
                		$is_facebook = true;
					}
            		else if($(this).prop("checked") == false){
						self.$modal.find(".facebook_is").addClass('hidden');
						$is_facebook = false;
            		}
				});

				self.$modal.find('#is_twitter').on('change', function() {
					if($(this).prop("checked") == true){
                		self.$modal.find(".twitter_is").removeClass('hidden');
                		$is_twitter = true;
					}
            		else if($(this).prop("checked") == false){
						self.$modal.find(".twitter_is").addClass('hidden');
						$is_twitter = false;
            		}
				});

				self.$modal.find('#is_linkedin').on('change', function() {
					if($(this).prop("checked") == true){
                		self.$modal.find(".linkedin_is").removeClass('hidden');
                		$is_linkedin = true;
					}
            		else if($(this).prop("checked") == false){
						self.$modal.find(".linkedin_is").addClass('hidden');
						$is_linkedin = false;
            		}
				});

				self.$modal.find('#is_google').on('change', function() {
					if($(this).prop("checked") == true){
                		self.$modal.find(".google_is").removeClass('hidden');
                		$is_google = true;
					}
            		else if($(this).prop("checked") == false){
						self.$modal.find(".google_is").addClass('hidden');
						$is_google = false;
            		}
				});

                var $lecturer_id = self.$modal.find("#lecturer_id"),
                	$lec_name = '',
                	$lec_image = '',
                	$lec_id = '',
                	$lec_desc = '',
                	$lec_qualification = '',
                	$card_color = self.$modal.find("#color_card"),
                	$sub_data = self.$modal.find("#cards_block_submit");

				$lecturer_id.autocomplete({
      				source: self.availableTags,
				 	minLength: 0,
				 	select: function (event, ui) {
						$lec_name = ui.item.value;
						$lec_id = ui.item.id;
						$lec_desc = ui.item.comment;
						$lec_image = ui.item.image;
						$lec_qualification = ui.item.qualification;
					},
    			}).blur(function(){
    				$(this).autocomplete('enable');
				}).focus(function () {
    				$(this).autocomplete('search', '');
				});
                $sub_data.on('click', function () {
                	var card_color = '';
                	var $facebook_url = self.$modal.find('#facebook_href').val(),
					$twitter_url = self.$modal.find('#twitter_href').val(),
					$linkedin_url = self.$modal.find('#linkedin_href').val(),
					$google_url = self.$modal.find('#google_href').val();
                	if ($card_color.val()) {
                        card_color = $card_color.val();
                    } else {
                        card_color = 'Red';
                    }
                    var html = "";
                    if ($is_facebook){
						html += '<a class="fa fa-fw fa-facebook" href="'+ $facebook_url +'"/>';
					}
					if ($is_twitter){
						html += '<a class="fa fa-fw fa-twitter" href="'+ $twitter_url +'"/>';
					}
					if ($is_linkedin){
						html += '<a class="fa fa-fw fa-linkedin" href="'+ $linkedin_url +'"/>';
					}
					if ($is_google){
						html += '<a class="fa fa-fw fa-google-plus" href="'+ $google_url +'"/>';
					}
					self.$target.find('.social_icons').append(html);
                    self.$target.find('.material-card').addClass(card_color);
					self.$target.find('.lecturer-image').attr('src',"data:image/jpeg;base64,"+ $lec_image);
                    self.$target.find('.lecturer-name').html($lec_name);
                    self.$target.find('.mc-description').html($lec_desc);
                    self.$target.find('.lecturer-qualification').html($lec_qualification);
                    self.$target.find('.details_view_lecturer').attr('data-href',"/"+$lec_name.replace(' ','-')+"/"+ $lec_id);
//                    self.$target.find('.info_lecturers_study').attr('data-popover-content',"#info_let_"+ $lec_id);
//                    self.$target.find('.hidden').attr('id',"info_let_"+ $lec_id);
                });
            } else {
                return false;
            }
        },
    });
});