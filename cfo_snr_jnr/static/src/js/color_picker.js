odoo.define('web_theme_color.main', function (require) {
"use strict";

	var BasicFields = require('web.basic_fields');

	BasicFields.FieldChar.include({
		_renderEdit: function() {
			var def = this._super.apply(this, arguments);
			if (this.field.size && this.field.size > 0) {
				this.$el.attr('maxlength', this.field.size);
			}
			this.$el = this.$el.add(this._renderTranslateButton());
			var self = this;
			setTimeout(function(e) {
				if (self.$el.hasClass('color-picker-cfo')) {
					$(self.$el).spectrum({
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
				}
				if (self.$el.hasClass('color-picker')) {
					$(self.$el).spectrum({
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
				}
			}, 0)
			return def;
		},
	})


});

