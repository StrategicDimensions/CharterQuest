odoo.define('cfo_snr_jnr.contentMenu', function (require) {

	var contentMenu = require('website.contentMenu');
	contentMenu.EditMenuDialog.include({
		start: function () {
	        var r = this._super.apply(this, arguments);
	        this.$('.oe_menu_editor').nestedSortable({
	            listType: 'ul',
	            handle: 'div',
	            items: 'li',
	            maxLevels: 15,
	            toleranceElement: '> div',
	            forcePlaceholderSize: true,
	            opacity: 0.6,
	            placeholder: 'oe_menu_placeholder',
	            tolerance: 'pointer',
	            attribute: 'data-menu-id',
	            expression: '()(.+)', // nestedSortable takes the second match of an expression (*sigh*)
	        });
	        return r;
	    },
	});
});