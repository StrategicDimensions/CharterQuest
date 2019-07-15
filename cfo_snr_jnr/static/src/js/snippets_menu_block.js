odoo.define('cfo_snr_jnr.snippets_menu_block', function (require) {

    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    ajax.loadXML('/cfo_snr_jnr/static/src/xml/snippet_custom.xml', qweb);
    options.registry.cfo_snr_jnr_blocks_tabs = options.Class.extend({
        start: function (editMode) {
            var self = this;
            this._super();
            if (!editMode) {
                self.$el.find(".cfo_snr_jnr_edit_block_menu").on("click", _.bind(self.cfo_edit_menu_block_configuration, self));
            }
        },
        onBuilt: function () {
            var self = this;
            this._super();
            if (this.cfo_menu_block_configuration()) {
                this.cfo_menu_block_configuration().fail(function () {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cfo_edit_menu_block_configuration: function (type, value) {
            var self = this;
            var $target = self.$target.find('.inside_block.active');
            if (type != undefined && type.type == "click" || type == undefined) {
                $(document).find('#cfo_add_menu_blocks_tabs_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_menu_blocks_tabs_mod"));
                self.$modal.appendTo('body');
                self.$modal.modal();
				$(self.$modal.find('.color-picker-cfo')).spectrum({
					showAlpha: true,
					hideAfterPaletteSelect: true,
					showInitial: true,
					showPalette: true,
					showSelectionPalette: true,
					showInput: true,
					preferredFormat: "hex",
					palette: [
						["#000", "#444", "#666", "#999", "#ccc", "#eee", "#f3f3f3", "#fff"],
						["#f00", "#f90", "#ff0", "#0f0", "#0ff", "#00f", "#90f", "#f0f"],
						["#f4cccc", "#fce5cd", "#fff2cc", "#d9ead3", "#d0e0e3", "#cfe2f3", "#d9d2e9", "#ead1dc"],
						["#ea9999", "#f9cb9c", "#ffe599", "#b6d7a8", "#a2c4c9", "#9fc5e8", "#b4a7d6", "#d5a6bd"],
						["#e06666", "#f6b26b", "#ffd966", "#93c47d", "#76a5af", "#6fa8dc", "#8e7cc3", "#c27ba0"],
						["#c00", "#e69138", "#f1c232", "#6aa84f", "#45818e", "#3d85c6", "#674ea7", "#a64d79"],
						["#900", "#b45f06", "#bf9000", "#38761d", "#134f5c", "#0b5394", "#351c75", "#741b47"],
						["#600", "#783f04", "#7f6000", "#274e13", "#0c343d", "#073763", "#20124d", "#4c1130"]
					]
				});
                var $menu_upper_bg = self.$modal.find("#menu-upper-bgcolor"),
                	$menu_lower_bg = self.$modal.find("#menu-lower-bgcolor"),
                	$menu_border_bg = self.$modal.find("#middle-border-bgcolor"),
                	$menu_border_width = self.$modal.find("#middle-border-width"),
                	$sub_data = self.$modal.find("#menu_blocks_tabs_apply");

                $sub_data.on('click', function () {
                    var menu_upper_bg = '';
                    var menu_lower_bg = '';
                    var menu_border_bg = '';
                    var menu_border_width = '';
                    if ($menu_upper_bg.val()) {
                        menu_upper_bg = $menu_upper_bg.val();
                    } else {
                        menu_upper_bg = 'white';
                    }
                    if ($menu_lower_bg.val()) {
                        menu_lower_bg = $menu_lower_bg.val();
                    } else {
                        menu_lower_bg = 'white';
                    }
                    if ($menu_border_bg.val()) {
                        menu_border_bg = $menu_border_bg.val();
                    } else {
                        menu_border_bg = 'gainsboro';
                    }
                    if ($menu_border_width.val()) {
                        menu_border_width = $menu_border_width.val();
                    } else {
                        menu_border_width = '5';
                    }
                    $target.find('.upper_block').css({"background-color": menu_upper_bg});
                    $target.find('.low_block').attr('style','background-color: '+menu_lower_bg+'; border-top: '+menu_border_width+'px solid ' + menu_border_bg);
                });
            } else {
                return false;
            }
        },
        cfo_menu_block_configuration: function (type, value) {
            var self = this;

            if (type != undefined && type.type == "click" || type == undefined) {
                $(document).find('#cfo_add_menu_blocks_tabs_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_menu_blocks_tabs_mod"));
                self.$modal.appendTo('body');
                self.$modal.modal();
				$(self.$modal.find('.color-picker-cfo')).spectrum({
					showAlpha: true,
					hideAfterPaletteSelect: true,
					showInitial: true,
					showPalette: true,
					showSelectionPalette: true,
					showInput: true,
					preferredFormat: "hex",
					palette: [
						["#000", "#444", "#666", "#999", "#ccc", "#eee", "#f3f3f3", "#fff"],
						["#f00", "#f90", "#ff0", "#0f0", "#0ff", "#00f", "#90f", "#f0f"],
						["#f4cccc", "#fce5cd", "#fff2cc", "#d9ead3", "#d0e0e3", "#cfe2f3", "#d9d2e9", "#ead1dc"],
						["#ea9999", "#f9cb9c", "#ffe599", "#b6d7a8", "#a2c4c9", "#9fc5e8", "#b4a7d6", "#d5a6bd"],
						["#e06666", "#f6b26b", "#ffd966", "#93c47d", "#76a5af", "#6fa8dc", "#8e7cc3", "#c27ba0"],
						["#c00", "#e69138", "#f1c232", "#6aa84f", "#45818e", "#3d85c6", "#674ea7", "#a64d79"],
						["#900", "#b45f06", "#bf9000", "#38761d", "#134f5c", "#0b5394", "#351c75", "#741b47"],
						["#600", "#783f04", "#7f6000", "#274e13", "#0c343d", "#073763", "#20124d", "#4c1130"]
					]
				});
                var $menu_upper_bg = self.$modal.find("#menu-upper-bgcolor"),
                	$menu_lower_bg = self.$modal.find("#menu-lower-bgcolor"),
                	$menu_border_bg = self.$modal.find("#middle-border-bgcolor"),
                	$menu_border_width = self.$modal.find("#middle-border-width"),
                	$sub_data = self.$modal.find("#menu_blocks_tabs_apply");

                $sub_data.on('click', function () {
                    var menu_upper_bg = '';
                    var menu_lower_bg = '';
                    var menu_border_bg = '';
                    var menu_border_width = '';
                    if ($menu_upper_bg.val()) {
                        menu_upper_bg = $menu_upper_bg.val();
                    } else {
                        menu_upper_bg = 'white';
                    }
                    if ($menu_lower_bg.val()) {
                        menu_lower_bg = $menu_lower_bg.val();
                    } else {
                        menu_lower_bg = 'white';
                    }
                    if ($menu_border_bg.val()) {
                        menu_border_bg = $menu_border_bg.val();
                    } else {
                        menu_border_bg = 'gainsboro';
                    }
                    if ($menu_border_width.val()) {
                        menu_border_width = $menu_border_width.val();
                    } else {
                        menu_border_width = '5';
                    }
                    self.$target.find('.upper_block').css({"background-color": menu_upper_bg});
                    self.$target.find('.low_block').attr('style','background-color: '+menu_lower_bg+'; border-top: '+menu_border_width+'px solid ' + menu_border_bg);
                });
            } else {
                return false;
            }
        },
    });
    $(document).ready(function(){
    	$(document).on('click','.inside_block',function(){
    		$(document).find('.inside_block').removeClass('active');
    		$(this).addClass('active');
    	});
    });

});