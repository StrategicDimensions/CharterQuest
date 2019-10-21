odoo.define('cfo_snr_jnr.rte_font', function (require) {
'use strict';

	var rte = require('web_editor.rte');
	var rpc = require('web.rpc');
	rte.Class.include({
		_getDefaultConfig: function ($editable) {
			var fontSize = ['Default', '8', '9', '10', '11', '12', '14', '18', '24', '36', '48', '62'];
			try {
				rpc.query({
					model: 'ir.config_parameter',
					method: 'get_param',
					args: ['cfo_snr_jnr.font_size_summernote']
				}, {async: false}).then(function (res) {
    					if (res){
						fontSize = JSON.parse(res);
						fontSize.splice(0, 1, "Default", fontSize[0]);
					}
				});
			}
			catch(err) {
				var fontSize = ['Default', '8', '9', '10', '11', '12', '14', '18', '24', '36', '48', '62'];
			}
			return {
				'airMode' : true,
				'focus': false,
				'fontSizes': fontSize,
				'airPopover': [
					['style', ['style']],
					['font', ['bold', 'italic', 'underline', 'clear']],
					['fontsize', ['fontsize']],
					['color', ['color']],
					['para', ['ul', 'ol', 'paragraph']],
					['table', ['table']],
					['insert', ['link', 'picture']],
					['history', ['undo', 'redo']],
				],
				'styleWithSpan': false,
				'inlinemedia' : ['p'],
				'lang': 'odoo',
				'onChange': function (html, $editable) {
					$editable.trigger('content_changed');
				}
			};
		},
	});

});