odoo.define('cfo_snr_jnr.snippets_comparision_block', function (require) {

    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    ajax.loadXML('/cfo_snr_jnr/static/src/xml/snippet_custom.xml', qweb);
    options.registry.cfo_snr_jnr_comparision_blocks_opt = options.Class.extend({
        start: function (editMode) {
            var self = this;
            this._super();
            if (!editMode) {
                self.$el.find(".cfo_snr_jnr_add_row_comp").on("click", _.bind(self.cfo_add_row_comp, self));
                self.$el.find(".cfo_snr_jnr_copy_row_comp").on("click", _.bind(self.cfo_copy_row_comp, self));
                self.$el.find(".cfo_snr_jnr_remove_row_comp").on("click", _.bind(self.cfo_remove_row_comp, self));
                self.$el.find(".cfo_snr_jnr_add_column_comp").on("click", _.bind(self.cfo_add_column_comp, self));
                self.$el.find(".cfo_snr_jnr_remove_column_comp").on("click", _.bind(self.cfo_remove_column_comp, self));
            }
        },
        onBuilt: function () {
            var self = this;
            this._super();
            if (this.cfo_comparision_block_configuration()) {
                this.cfo_comparision_block_configuration().fail(function () {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cfo_copy_row_comp:function(type,value){
        	var self = this;
        	self.$target.find('tr.active').after(self.$target.find('tr.active').clone());
        },
        cfo_add_column_comp:function(type,value){
        	var self = this;
        	self.$target.find('tr').each(function (ev){
        		var $tr = $(this);
				if ($($tr[0].lastElementChild).is('th')) {
					$($tr[0].lastElementChild).after("<th class='bg-blue'/>");
				}
				else if ($($tr[0].lastElementChild).is('td')){
					if (!$($tr[0].lastElementChild).hasClass('sep')){
						$($tr[0].lastElementChild).after("<td/>");
					}
				}
        	});
        	self.$target.find('td.sep').each(function(){
        		$(this).attr('colspan',parseInt($(this).attr('colspan')) + 1);
        	});
        },
        cfo_remove_row_comp:function(type,value){
        	var self = this;
        	self.$target.find('tr.active').remove();
        },
        cfo_remove_column_comp:function(type,value){
        	var self = this;
        	var index = $(document).find('.comparision_article tr.active td').index($(document).find('.comparision_article td.active'))
        	self.$target.find('tr').each(function(){
        		if(!$(this).find('td').eq(parseInt(index)).hasClass('sep')){
        			$(this).find('td').eq(parseInt(index)).remove();
				}
        		$(this).find('th').eq(parseInt(index)).remove();
        	});
        	self.$target.find('td.sep').each(function(){
        		$(this).attr('colspan',parseInt($(this).attr('colspan')) - 1);
        	})
        },
		cfo_add_row_comp: function (type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                $(document).find('#cfo_comparision_add_row_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_comparision_add_row_mod"));
                self.$modal.appendTo('body');
                self.$modal.modal();
				var $is_with_without_colspan = self.$modal.find("#is_with_without_colspan"),
					$cols_comparision = self.$modal.find("#cols_comparision"),
					$sub_data = self.$modal.find("#comparision_blocks_apply_add");

				$is_with_without_colspan.on('change', function() {
					if($(this).prop("checked") == true){
                		self.$modal.find(".is_with_without_label").text('').text('With Colspan');
                		self.$modal.find(".cols_comparision_label").text('').text('No. Columns Colspan');
					}
            		else if($(this).prop("checked") == false){
						self.$modal.find(".is_with_without_label").text('').text('Without Colspan');
						self.$modal.find(".cols_comparision_label").text('').text('No. Columns');
            		}
				});

				$sub_data.on('click', function () {
                    var cols_comparision = '';
                    if ($cols_comparision.val()) {
                        cols_comparision = $cols_comparision.val();
                    } else {
                        cols_comparision = 1;
                    }
                    if ($is_with_without_colspan.prop("checked") == true){
						var with_html = "<tr><td colspan='"+ cols_comparision +"' class='sep'></tr>";
                    	self.$target.find('.comparision_article table tbody tr.active').after(with_html);
                    }
                    else if($is_with_without_colspan.prop("checked") == false){
                    	var without_html = "<tr>";
						for (var i = 0; i <= parseInt(cols_comparision); i++) {
                    		without_html += "<td/>";
                    	}
                    	without_html += "<tr/>";
                    	self.$target.find('.comparision_article table tbody tr.active').after(without_html);
                    }
                });
            } else {
                return false;
            }
        },
        cfo_comparision_block_configuration: function (type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                $(document).find('#cfo_comparision_blocks_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_comparision_blocks_mod_new"));
                self.$modal.appendTo('body');
                self.$modal.modal();

                var $cols_comparision_header = self.$modal.find("#cols_comparision_header"),
                	$sub_data = self.$modal.find("#comparision_blocks_apply");

                $sub_data.on('click', function () {
                    var cols_comparision_header = '';
                    if ($cols_comparision_header.val()) {
                        cols_comparision_header = $cols_comparision_header.val();
                    } else {
                        cols_comparision_header = 1;
                    }
                    var ul_html = "";
                    var thead_html = "";
                    var tbody_html = "";
                    var j=0;
                    for (var i = 0; i < parseInt(cols_comparision_header); i++) {
                        j++;
                        var class_id="block"+j;
                    	if (i==0){
							ul_html += "<li class='bg-purple'>";
							thead_html += "<th class='bg-purple comparison_block' id='"+class_id+"'></th>";
                    	}
                    	else{
                    		ul_html += "<li class='bg-blue'>";
                    		thead_html += "<th class='bg-blue comparison_block' id='"+class_id+"'></th>";
                    	}
						ul_html += "<button class='"+class_id+"'></button></li>";
                    }
                    for (var i = 0; i <= parseInt(cols_comparision_header); i++) {
                    	tbody_html += "<td/>"
                    }
                    console.log('\n\n\n\n ul_html',ul_html)
					self.$target.find('.comparision_article ul').append(ul_html);
					self.$target.find('.comparision_article table thead tr').append(thead_html);
					self.$target.find('.comparision_article table tbody tr').append(tbody_html);

                });
            } else {
                return false;
            }
        },
    });
    $(document).ready(function(){
    	$(document).on('click','.comparision_article td , .comparision_article th',function(){
    		$(document).find('.comparision_article tr').removeClass('active');
    		$(document).find('.comparision_article td').removeClass('active');
    		$(document).find('.comparision_article th').removeClass('active');
    		$(this).addClass('active');
    		$(this).parents('tr').addClass('active');
    	});
    	$("body").on('DOMSubtreeModified', ".comparison_block", function() {
    	     var color=$( this ).css( "background-color" );
    	     console.log("\n\n\n\n color",color)
             $('button[class=' + $(this).attr('id') + ']').html($(this).html())
             $('button[class=' + $(this).attr('id') + ']').css("background-color",color)
        });
    });
});