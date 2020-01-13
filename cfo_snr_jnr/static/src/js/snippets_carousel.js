odoo.define('cfo_snr_jnr.snippets_carousel', function (require) {

    var options = require('web_editor.snippets.options');

    options.registry.cfo_snr_jnr_carousel_remove = options.Class.extend({
        start: function (editMode) {
            var self = this;
            this._super();
            if (!editMode) {
                self.$el.find(".cfo_snr_jnr_remove_carousel_placeholder_a").on("click", _.bind(self.cfo_remove_placeholder, self));
                self.$el.find(".cfo_snr_jnr_add_carousel_placeholder_a").on("click", _.bind(self.cfo_add_placeholder, self));
            }
        },
        cfo_remove_placeholder: function (type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
				self.$target.find('.item.active .carousel-caption').hide();
            } else {
                return false;
            }
        },
        cfo_add_placeholder: function (type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
				self.$target.find('.item.active .carousel-caption').show();
            } else {
                return false;
            }
        },
    });

});