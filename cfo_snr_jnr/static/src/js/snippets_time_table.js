odoo.define('cfo_snr_jnr.snippets_time_table', function (require) {

    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var qweb = core.qweb;
    var _t = core._t;
    ajax.loadXML('/cfo_snr_jnr/static/src/xml/snippet_custom.xml', qweb);
    options.registry.cfo_snr_jnr_timetable = options.Class.extend({
        start: function (editMode) {
//        alert()
            var self = this;
            this._super();
            if (!editMode) {
//                self.$el.find(".cfo_snr_jnr_time_table_part").on("click", _.bind(self.cfo_menu_tabs_configuration, self));
//                self.$el.find(".cfo_snr_jnr_remove_menu_tabs").on("click", _.bind(self.cfo_menu_tabs_remove, self));
            }
        },
        onBuilt: function () {
            var self = this;
            this._super();
            if (this.cfo_timetable_configuration()) {
                this.cfo_timetable_configuration().fail(function () {
                    self.getParent()._removeSnippet();
                });
            }
        },
//        cfo_menu_tabs_remove: function () {
//        	var self = this;
//           	self.$target.find('.nav.nav-tabs li.active').remove();
//			self.$target.find('.tab-content.tabs .tab-pane.active').remove();
//			self.$target.find('.nav.nav-tabs li:first').addClass('active')
//			self.$target.find('.tab-content.tabs .tab-pane:first').addClass('active')
//        },
        cfo_timetable_configuration: function (type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                $(document).find('#cfo_timetable_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_timetable_snippet"));
                self.$modal.appendTo('body');
                $event=self.$modal.find('#event_category');
                $event.html('');
                rpc.query({
                        model: 'event.type',
                        method: 'get_event_category',
                }).then(function(data){
                    var events=[]
                        for(var i=0; i<data .length; i++)
                        {
                            events.push('<option value=' + data[i].id + '>' + data[i].name + '</option>\n')
                        }
                    $event.append(events);
                });
                self.$modal.modal()
                $sub_data = self.$modal.find("#timetable_event_submit");
                $fillter_timetable=self.$modal.find(".fillter_timetable");
                $sub_data.on('click', function (event) {
                    var id=$('#event_category').val();
                    var lecturer_id=$('#lecturer_ids').val();
                    var domain=[('id','=',id)]
                    rpc.query({
                        model: 'event.type',
                        method: 'get_event_data',
                        args: [id],
                    }).then(function(data){
    //                        $(document).find('#course_code_select').html("")
                        self.$target.find('select[name="level_select"]').html("")
                        self.$target.find('select[name="campus_select"]').html("")
                        self.$target.find('select[name="semester_select"]').html("")
                        var level=[]
                        var campus=[]
                        var sem=[]
                        var options=[]
                        for(var i=0; i<data['qua'].length; i++)
                        {
                            level.push('<option value=' + data['qua'][i].id + '>' + data['qua'][i].name + '</option>\n')
                        }
                        for(var i=0; i<data['sem'].length; i++)
                        {
                            sem.push('<option value=' + data['sem'][i].id + '>' + data['sem'][i].name + '</option>\n')
                        }
                        for(var i=0; i<data['campus'].length; i++)
                        {
                            campus.push('<option value=' + data['campus'][i].id + '>' + data['campus'][i].name + '</option>\n')
                        }
                        for(var i=0; i<data['options'].length; i++)
                        {
                            options.push('<option value=' + data['options'][i].id + '>' + data['options'][i].name + '</option>\n')
                        }
                        self.$target.find('select[name="level_select"]').html(level)
                        self.$target.find('select[name="campus_select"]').html(campus)
                        self.$target.find('select[name="semester_select"]').html(sem)
                        self.$target.find('select[name="option_select"]').html(options)
                        self.$target.find(".fillter_timetable").attr('data-id',id);
                        self.$target.find("#campus_select").attr('data-id',id);
                        self.$target.find(".fillter_timetable").attr('data-lecturer-id',lecturer_id);
                    });
                });
            } else {
                return false;
            }
        },
    });
});