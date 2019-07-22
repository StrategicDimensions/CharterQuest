odoo.define('cfo_snr_jnr.snippets_steps_wizard', function (require) {

    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    ajax.loadXML('/cfo_snr_jnr/static/src/xml/snippet_custom.xml', qweb);
    options.registry.cfo_snr_jnr_steps_wizard_option = options.Class.extend({
        start: function (editMode) {
            var self = this;
            this._super();
        },
        onBuilt: function () {
            var self = this;
            this._super();
            if (this.cfo_steps_wizard_configuration()) {
                this.cfo_steps_wizard_configuration().fail(function () {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cfo_steps_wizard_configuration: function (type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                $(document).find('#cfo_steps_wizard_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_steps_wizard_cfo"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                self.$modal.find('#menu-icon').iconpicker('#menu-icon');

                var $menu_icon = self.$modal.find("#menu-icon"),
                	$sub_data = self.$modal.find("#menu_steps_wizard_submit");

                $sub_data.on('click', function () {
                    var menu_icon = '';
                    self.$target.attr('data-menu-icon', $menu_icon.val());
                    if ($menu_icon.val()) {
                        menu_icon = $menu_icon.val();
                    } else {
                        menu_icon = _t("fa-check");
                    }
                    var unique_label =	'xxxxxxxx_'.replace(/[x]/g, function(c) {
						var r = (Math.random() * 16) | 0,
						v = c == 'x' ? r : (r & 0x3) | 0x8;
						return v.toString(16);
					}) + new Date().getTime();
                    var tab_html = `
                    	<li role="presentation" class="active">
                            <a href="#`+ unique_label +`" data-toggle="tab" aria-controls="`+ unique_label +`" role="tab">
                            	<span class="round-tab">
                            		<i class="fa `+ menu_icon +`"/>
								</span>
                            </a>
                        </li>
                    `;
					self.$target.find('.wizard-inner ul').append(tab_html);
                    var content_html = `
                    	<div class="tab-pane fade in active" role="tabpanel" id="`+ unique_label +`">
							<h3>This is test content</h3>
							<p>Test Content</p>
							<ul class="list-inline pull-right">
								<li>
									<button type="button" class="btn btn-default prev-step">Previous
									</button>
								</li>
								<li>
									<button type="button" class="btn btn-primary next-step">Continue
									</button>
								</li>
							</ul>
                        </div>
                    `;
                    self.$target.find('.wizard .tab-content').append(content_html);
                });
            } else {
                return false;
            }
        },
    });

});