odoo.define('cfo_snr_jnr.snippets_menu_tabs', function (require) {

    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    ajax.loadXML('/cfo_snr_jnr/static/src/xml/snippet_custom.xml', qweb);
    options.registry.cfo_snr_jnr_menu_tabs_snippet_add_menu_option = options.Class.extend({
        start: function (editMode) {
            var self = this;
            this._super();
            if (!editMode) {
                self.$el.find(".cfo_snr_jnr_menu_tabs").on("click", _.bind(self.cfo_menu_tabs_configuration, self));
                self.$el.find(".cfo_snr_jnr_remove_menu_tabs").on("click", _.bind(self.cfo_menu_tabs_remove, self));
            }
        },
        onBuilt: function () {
            var self = this;
            this._super();
            if (this.cfo_menu_tabs_configuration()) {
                this.cfo_menu_tabs_configuration().fail(function () {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cfo_menu_tabs_remove: function () {
        	var self = this;
           	self.$target.find('.nav.nav-tabs li.active').remove();
			self.$target.find('.tab-content.tabs .tab-pane.active').remove();
			self.$target.find('.nav.nav-tabs li:first').addClass('active')
			self.$target.find('.tab-content.tabs .tab-pane:first').addClass('active')
        },
        cfo_menu_tabs_configuration: function (type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                $(document).find('#cfo_add_menu_with_tabs_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_menu_block_with_tabs"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                self.$modal.find('#menu-icon').iconpicker('#menu-icon');
                self.$modal.find('#external-icon').iconpicker('#menu-icon');

                var unique_label =	'xxxxxxxx_'.replace(/[x]/g, function(c) {
						var r = (Math.random() * 16) | 0,
						v = c == 'x' ? r : (r & 0x3) | 0x8;
						return v.toString(16);
					}) + new Date().getTime();

                var $menu_title = self.$modal.find("#menu-title"),
                	$menu_icon = self.$modal.find("#menu-icon"),
                	$menu_url = self.$modal.find("#menu-url"),
                	$external_url = self.$modal.find("#external-url"),
                	$sub_data = self.$modal.find("#menu_sub_data_with_tabs");

                $sub_data.on('click', function () {
                    var menu_title = '';
                    var menu_icon = '';
                    var menu_url = '';
                    var external_url = '';
                    self.$target.attr("data-menu-title", $menu_title.val());
                    self.$target.attr('data-menu-icon', $menu_icon.val());
                    self.$target.attr('data-menu-url', $menu_url.val());
                    self.$target.attr('data-menu-external-url', $external_url.val());
                    if ($menu_title.val()) {
                        menu_title = $menu_title.val();
                    } else {
                        menu_title = _t("#");
                    }
                    if ($menu_icon.val()) {
                        menu_icon = $menu_icon.val();
                    } else {
                        menu_icon = _t("fa-check");
                    }
                    if ($menu_url.val()) {
                        menu_url = $menu_url.val().replace(/\s/g, "_");
                    } else {
                        menu_url = _t("#");
                    }
                    if ($external_url.val()) {
                        external_url = $external_url.val().replace(/\s/g, "_");
                    } else {
                        external_url = _t("#");
                    }
                    self.$target.find('.nav.nav-tabs li').removeClass('active');
                    self.$target.find('.tab-content.tabs .tab-pane').removeClass('active');
                    var tab_html = `
                    	<li role="presentation" class="active">
                            <a class="cfo_menu_with_tabs_a_panel" external-href="`+ external_url +`" href="#`+ menu_url +`" aria-controls="home" role="tab"
                               data-toggle="tab"><i class="fa `+ menu_icon +`"/> &nbsp;&nbsp;` + menu_title + `
                            </a>
                        </li>
                    `;
                    var len=self.$target.find('.nav.nav-tabs').find('a.read-more').length
                    if (len > 0){
                        self.$target.find('.nav.nav-tabs').find('a.read-more').before(tab_html);
                    }
                    else{
					self.$target.find('.nav.nav-tabs').append(tab_html);
					}
                    var content_html = `
                    	<div role="tabpanel" class="tab-pane fade in active" id="`+ menu_url +`">
							<div class="row oe_structure" style="min-height:150px;"/>
                        </div>
                    `;
                    self.$target.find('.tab-content.tabs').append(content_html);
                });
            } else {
                return false;
            }
        },
    });

    $(document).ready(function(){
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
            if($(this).attr("external-href") != '#')
			{
				const hash = $(this).attr("external-href");
				const win=window.open(hash);
				win.focus();
				event.preventDefault();
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
			event.preventDefault();
		});


	});

});