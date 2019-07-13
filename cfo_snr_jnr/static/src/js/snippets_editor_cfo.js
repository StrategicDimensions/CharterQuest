odoo.define('cfo_snr_jnr.snippets_editor_cfo', function (require) {
'use strict';

	var SnippetEditor = require('web_editor.snippet.editor');

	SnippetEditor.Editor.include({

		_onCloneClick: function (ev) {
			ev.preventDefault();
			var $clone = this.$target.clone(false);

			this.trigger_up('request_history_undo_record', {$target: this.$target});

			this.$target.after($clone);
			this.trigger_up('call_for_each_child_snippet', {
				$snippet: $clone,
				callback: function (editor, $snippet) {
					for (var i in editor.styles) {
						editor.styles[i].onClone({
							isCurrent: ($snippet.is($clone)),
						});
					}
				},
			});
			$clone.find('.nav.nav-tabs li a').each(function(){
				var old_lable = $(this).attr('href');
				var new_lable =	'xxxxxxxx_'.replace(/[x]/g, function(c) {
							var r = (Math.random() * 16) | 0,
							v = c == 'x' ? r : (r & 0x3) | 0x8;
							return v.toString(16);
						}) + new Date().getTime();
				$clone.find(old_lable).attr('id',new_lable)
				var new_herf='#'+new_lable
				$(this).attr('href',new_herf);
			});
			this.trigger_up('snippet_cloned', {$target: $clone});
		},

	});

});