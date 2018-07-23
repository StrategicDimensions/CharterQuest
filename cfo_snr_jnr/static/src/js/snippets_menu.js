odoo.define('cfo_snr_jnr.snippet_menu', function (require) {
    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    ajax.loadXML('/cfo_snr_jnr/static/src/xml/snippet_custom.xml', qweb);
    options.registry.cfo_snr_jnr_menu_snippet_add_menu_option = options.Class.extend({

        start: function (editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.on('click', '.add_menu_side', function (ev) {
                $(ev.currentTarget).parents('.label_link_list.row').find('.add_menu_side').removeClass('active');
                $(ev.currentTarget).parents('section').find('.col-md-1').removeClass('active');
                $(ev.currentTarget).parents('section').find('.content').addClass('hidden').removeClass('active');
                $(ev.currentTarget).addClass('active');
                $(ev.currentTarget).parents('section').find('.col-md-1.' + $(ev.currentTarget).attr('data-current-menu')).addClass('active');
                $(ev.currentTarget).parents('section').find('.content.' + $(ev.currentTarget).attr('data-current-menu')).removeClass('hidden').addClass('active');
                $(document).find('.breadcrumb').find('li.active').removeClass('active');
                $(document).find('.breadcrumb').find('li.cfo_menu').remove();
                $(document).find('.breadcrumb').append('<li class="active cfo_menu">' + $(ev.currentTarget).text() + '</li>')
            });
            this.$target.on('click', '.menu-icon', function (ev) {
                $(ev.currentTarget).parents('section').find('.add_menu_side').removeClass('active');
                $(ev.currentTarget).parents('section').find('.col-md-1').removeClass('active');
                $(ev.currentTarget).parents('section').find('.content').addClass('hidden').removeClass('active');
                $(ev.currentTarget).addClass('active');
                $(ev.currentTarget).parents('section').find('.add_menu_side.' + $(ev.currentTarget).attr('data-current-menu')).addClass('active');
                $(ev.currentTarget).parents('section').find('.content.' + $(ev.currentTarget).attr('data-current-menu')).removeClass('hidden').addClass('active');
                $(document).find('.breadcrumb').find('li.active').removeClass('active');
                $(document).find('.breadcrumb').find('li.cfo_menu').remove();
                $(document).find('.breadcrumb').append('<li class="active cfo_menu">' + $(ev.currentTarget).find('a').text() + '</li>')
            });
            if (!editMode) {
                self.$el.find(".cfo_snr_jnr_menu").on("click", _.bind(self.cfo_menu_configuration, self));
                self.$el.find(".cfo_snr_jnr_remove_menu").on("click", _.bind(self.cfo_menu_remove, self));
            }
        },
        onBuilt: function () {
            var self = this;
            this._super();
            if (this.cfo_menu_configuration()) {
                this.cfo_menu_configuration().fail(function () {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function () {
            $('.mobicraft_theme_brand_slider .owl-carousel').empty();
        },
        cfo_menu_remove: function () {
            console.log(this.$el.html());
            this.$target.find('.add_menu_side.active').parent().remove();
            this.$target.find('.content.active').remove();
            this.$target.find('.col-md-1.active').remove();
        },
        cfo_menu_configuration: function (type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                $(document).find('#cfo_add_menu_modal').remove();
                self.$modal = $(qweb.render("cfo_snr_jnr.cfo_snr_jnr_menu_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                self.$modal.find('#menu-icon').iconpicker('#menu-icon');
                var $menu_title = self.$modal.find("#menu-title"),
                    $menu_url = self.$modal.find("#menu-url"),
                    $menu_icon = self.$modal.find("#menu-icon"),
                    $sub_data = self.$modal.find("#menu_sub_data");

                $sub_data.on('click', function () {
                    var menu_title = '';
                    var menu_url = '';
                    var menu_icon = '';
                    self.$target.attr("data-menu-title", $menu_title.val());
                    self.$target.attr('data-menu-url', $menu_url.val().replace(' ', '_'));
                    self.$target.attr('data-menu-icon', $menu_icon.val());

                    if ($menu_url.val()) {
                        menu_url = $menu_url.val().replace(/\s/g, "_");
                    } else {
                        menu_url = _t("#");
                    }
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
                    html = '<a href="#' + menu_url + '" class="step-link"><div class="col-md-1 menu-icon ' + menu_url + '" data-current-menu="' + menu_url + '"><ul class="breadcrumb-list-new"><li class="step-done">';
                    if (typeof self.$target.find('.menu-with-icon ul li').html() != 'undefined') {
                        $(".menu-with-icon ul li:last-child div").addClass('add-connector_after');
                        html += '<div class="stop-rounding add-connector">';
                    } else {
                        html += '<div class="stop-rounding">';
                    }
                    html += '<span class="step-number">' +
                        '<i class="fa ' + menu_icon + '" aria-hidden="true"></i>' +
                        '</span>' +
                        '</div>' +
                        '<p>' + menu_title +
                        '</p></li></ul></div></a>';
                    self.$target.find('.label_link_list.row').append('<div class="col-md-3"><a href="#' + menu_url + '" class="honsNav0 add_menu_side ' + menu_url + '" data-current-menu="' + menu_url + '" id="custom">' + menu_title + '</a></div>');
                    self.$target.find('.row.menu-with-icon').append(html);
                    self.$target.find('.row.menu-content').append('<div class="col-md-12 content hidden ' + menu_url + '" style="min-height: 100px;"><div class="oe_structure"/></div>');
                });
            } else {
                return false;
            }
        },
    });

});