# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2012 - Present Acespritech Solutions Pvt. Ltd. All Rights Reserved
#    Author: <info@acespritech.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################
import werkzeug

from odoo import http, fields, _
from odoo.http import request
import logging
import json
import itertools
import pytz
import babel.dates
from collections import OrderedDict
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.web.controllers import main as web
from odoo.addons.auth_signup.controllers import main as auth_signup
import odoo
from odoo.exceptions import UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.website.controllers.main import QueryURL
import datetime
from datetime import timedelta
import base64
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class WebsiteBlog(http.Controller):
    _blog_post_per_page = 20
    _post_comment_per_page = 10

    def nav_list(self, blog=None):
        dom = blog and [('blog_id', '=', blog.id)] or []
        if not request.env.user.has_group('website.group_website_designer'):
            dom += [('post_date', '<=', fields.Datetime.now())]
        groups = request.env['blog.post']._read_group_raw(
            dom,
            ['name', 'post_date'],
            groupby=["post_date"], orderby="post_date desc")
        for group in groups:
            (r, label) = group['post_date']
            start, end = r.split('/')
            group['post_date'] = label
            group['date_begin'] = start
            group['date_end'] = end

            locale = request.context.get('lang') or 'en_US'
            start = pytz.UTC.localize(fields.Datetime.from_string(start))
            tzinfo = pytz.timezone(request.context.get('tz', 'utc') or 'utc')

            group['month'] = babel.dates.format_datetime(start, format='MMMM', tzinfo=tzinfo, locale=locale)
            group['year'] = babel.dates.format_datetime(start, format='YYYY', tzinfo=tzinfo, locale=locale)

        return OrderedDict((year, [m for m in months]) for year, months in itertools.groupby(groups, lambda g: g['year']))

    @http.route([
        '''/blog/<model("blog.blog"):blog>/post/<model("blog.post", "[('blog_id','=',blog[0])]"):blog_post>''',],
        type='http', auth="public", website=True)
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        """ Prepare all values to display the blog.

        :return dict values: values for the templates, containing

         - 'blog_post': browse of the current post
         - 'blog': browse of the current blog
         - 'blogs': list of browse records of blogs
         - 'tag': current tag, if tag_id in parameters
         - 'tags': all tags, for tag-based navigation
         - 'pager': a pager on the comments
         - 'nav_list': a dict [year][month] for archives navigation
         - 'next_post': next blog post, to direct the user towards the next interesting post
        """
        BlogPost = request.env['blog.post']
        date_begin, date_end = post.get('date_begin'), post.get('date_end')

        pager_url = "/blogpost/%s" % blog_post.id

        pager = request.website.pager(
            url=pager_url,
            total=len(blog_post.website_message_ids),
            page=page,
            step=self._post_comment_per_page,
            scope=7
        )
        pager_begin = (page - 1) * self._post_comment_per_page
        pager_end = page * self._post_comment_per_page
        comments = blog_post.website_message_ids[pager_begin:pager_end]

        tag = None
        if tag_id:
            tag = request.env['blog.tag'].browse(int(tag_id))
        blog_url = QueryURL('', ['blog', 'tag'], blog=blog_post.blog_id, tag=tag, date_begin=date_begin,
                            date_end=date_end)

        if not blog_post.blog_id.id == blog.id:
            return request.redirect("/blog/%s/post/%s" % (slug(blog_post.blog_id), slug(blog_post)))

        tags = request.env['blog.tag'].search([])

        # Find next Post
        all_post = BlogPost.search([('blog_id', '=', blog.id)])
        if not request.env.user.has_group('website.group_website_designer'):
            all_post = all_post.filtered(lambda r: r.post_date <= fields.Datetime.now())

        if blog_post not in all_post:
            return request.redirect("/blog/%s" % (slug(blog_post.blog_id)))

        # should always return at least the current post
        all_post_ids = all_post.ids
        current_blog_post_index = all_post_ids.index(blog_post.id)
        nb_posts = len(all_post_ids)
        next_post_id = all_post_ids[(current_blog_post_index + 1) % nb_posts] if nb_posts > 1 else None
        next_post = next_post_id and BlogPost.browse(next_post_id) or False

        values = {
            'tags': tags,
            'tag': tag,
            'blog': blog,
            'blog_post': blog_post,
            'blog_post_cover_properties': json.loads(blog_post.cover_properties),
            'main_object': blog_post,
            'nav_list': self.nav_list(blog),
            'enable_editor': enable_editor,
            'next_post': next_post,
            'next_post_cover_properties': json.loads(next_post.cover_properties) if next_post else {},
            'date': date_begin,
            'blog_url': blog_url,
            'pager': pager,
            'comments': comments,
        }
        response = request.render("cfo_snr_jnr.blog_detail", values)

        request.session[request.session.sid] = request.session.get(request.session.sid, [])
        if not (blog_post.id in request.session[request.session.sid]):
            request.session[request.session.sid].append(blog_post.id)
            # Increase counter
            blog_post.sudo().write({
                'visits': blog_post.visits + 1,
            })
        return response

class CfoHomeJnr(web.Home):
    
    @http.route(['/cfo_junior'], type='http', auth="public", website=True)
    def cfo_junior(self, **post):
        partner = request.env.user.partner_id
        login = request.env.user.login
        today = datetime.datetime.today()
        args = [('email_1', '=', login)]
        # if today.month in [4, 5, 6, 7, 8, 9, 10, 11, 12]:
        #     args.append(('cfo_competition_year', '=', str(today.year + 1)))
        # else:
        #     args.append(('cfo_competition_year', '=', str(today.year)))
        jnr_aspirants = request.env['cfo.jnr.aspirants'].sudo().search(args)
        jnr_high_school = request.env['academic.institution.jnr'].sudo().search(args)
        jnr_brand_ambassador = request.env['brand.ambassador.jnr'].sudo().search(args)
        jnr_mentors = request.env['mentors.jnr'].sudo().search(args)
        is_from_new_member = request.session.get('is_from_new_member')
        
        values = {}
        if jnr_aspirants:
            values.update({'jnr_aspirants': jnr_aspirants})
        if jnr_high_school:
            values.update({'jnr_high_school': jnr_high_school})
        if jnr_brand_ambassador:
            values.update({'jnr_brand_ambassador': jnr_brand_ambassador})
            values.update({'brand_ambassador': True})
        if jnr_mentors:
            values.update({'jnr_mentors': jnr_mentors})
            values.update({'mentor': True})
            
        if values:
            values.update({'junior': True})
            
        values['country_list'] = request.env['res.country'].sudo().search([])
        values['state_list'] = request.env['res.country.state'].sudo().search([])
            
        if post.get('jnr_aspirants') or post.get('jnr_high_school') or post.get('jnr_mentors') or post.get('jnr_brand_ambassador'):
            values['update_bio'] = True
            values['update_bio_info'] = True

        values['date_of_report_submit'] = False
        if jnr_aspirants.aspirant_id and jnr_aspirants.aspirant_id.cfo_report_deadline_date:
            tz = pytz.timezone(request.env.user.tz) if request.env.user.tz else pytz.utc
            life_date = datetime.datetime.strptime(jnr_aspirants.aspirant_id.cfo_report_deadline_date,
                                                   DEFAULT_SERVER_DATETIME_FORMAT)
            life_date = (life_date + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
            values['date_of_report_submit'] = life_date
        
        if is_from_new_member:
            values['is_from_new_member'] = True

        if jnr_aspirants:
            values.update({'jnr_aspirants': jnr_aspirants})
            if jnr_aspirants.date_of_birth:
                values.update({'date_of_birth':datetime.datetime.strptime(jnr_aspirants.date_of_birth, "%Y-%m-%d").strftime('%d/%m/%Y')})
            if jnr_aspirants.start_date:
                values.update({'start_date':datetime.datetime.strptime(jnr_aspirants.start_date, "%Y-%m-%d").strftime('%d/%m/%Y')})
            if jnr_aspirants.expected_completion_date:
                values.update({'expected_completion_date':datetime.datetime.strptime(jnr_aspirants.expected_completion_date, "%Y-%m-%d").strftime('%d/%m/%Y')})
            values.update({'junior': True})
        
        if post.get('cfo_team'):
            list = []
            values['cfo_team'] = True
            values['update_bio'] = False
            values['update_bio_info'] = False

            if jnr_aspirants.aspirant_id:
                values['aspirant_team'] = jnr_aspirants.aspirant_id
            if jnr_high_school.cfo_team_ids:
                for data in jnr_high_school.cfo_team_ids:
                    for team in data:
                        list.append(team)
                values['high_school_team'] = list
               
        
        if request.httprequest.method == 'GET' or request.httprequest.method == 'POST':
             if post.get('jnr_aspirants') and not post.get('cfo_team'):
                if post.get('update_bio_info'):
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    birth_date = datetime.datetime.strptime(post.get('date_of_birth'), "%d/%m/%Y").strftime('%m/%d/%Y')
                    jnr_aspirants.sudo().write({
                        'name': post.get('name'),
                        'surname': post.get('surname'),
                        'other_names': post.get('other_names'),
                        'date_of_birth': birth_date,
                        'nationality': post.get('nationality'),
                        'jnr_high_school_name':post.get('jnr_high_school_name'),
                        'country_of_birth': post.get('country_of_birth')
                    })
                if post.get('contact_info'):
                    values['eligibility_status'] = True
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['update_bio_info'] = False
                    jnr_aspirants.sudo().write({
                        'mobile': post.get('mobile'),
                        'phone': post.get('phone'),
                        'home_phone': post.get('home_phone'),
                        'email_1': post.get('email_1'),
                        'email_2': post.get('email_2'),
                        'street': post.get('street'),
                        'street2': post.get('street2'),
                        'city': post.get('city'),
                        'state_id': post.get('state_id'),
                        'zip': post.get('zip'),
                        'country_id': post.get('country_id')
                    })
                if post.get('eligibility_status'):
                    values['eligibility_status'] = False
                    values['update_bio_info'] = False
                    values['competition_rule'] = True
                    values['update_bio'] = True
                    if post.get('start_date'):
                        start_date = datetime.datetime.strptime(post.get('start_date'), "%d/%m/%Y").strftime('%m/%d/%Y')
                    if post.get('expected_completion_date'):
                        expected_completion_date = datetime.datetime.strptime(post.get('expected_completion_date'), "%d/%m/%Y").strftime('%m/%d/%Y')
                    jnr_aspirants.sudo().write({
                        'entry_as_student': True if post.get('user_type') == 'student' else False,
                        'entry_as_employee': True if post.get('user_type') == 'employee' else False,
                        'school_name': post.get('school_name'),
                        'department': post.get('department'),
                        'website': post.get('website'),
                        'stu_street': post.get('stu_street'),
                        'stu_street2': post.get('stu_street2'),
                        'stu_city': post.get('stu_city'),
                        'stu_state_id': post.get('stu_state_id'),
                        'stu_zip': post.get('stu_zip'),
                        'stu_country_id': post.get('stu_country_id'),
                        'programme_name': post.get('programme_name'),
                        'start_date': start_date if post.get('start_date') else False,
                        'expected_completion_date': expected_completion_date if post.get(
                            'expected_completion_date') else False,
                        'mode_of_studies': post.get('mode_of_studies'),
                        'formal_work_exp': post.get('formal_work_exp'),
                        'legal_name_employer': post.get('legal_name_employer'),
                        'sector': post.get('sector'),
                        'if_company': post.get('if_company'),
                        'emp_department': post.get('emp_department'),
                        'emp_website': post.get('emp_website'),
                        'emp_start_date': post.get('emp_start_date') or False,
                        'emp_status': post.get('emp_status'),
                        'emp_experience': post.get('emp_experience'),
                        'emp_street': post.get('emp_street'),
                        'emp_street2': post.get('emp_street2'),
                        'emp_city': post.get('emp_city'),
                        'emp_state_id': post.get('emp_state_id'),
                        'emp_zip': post.get('emp_zip'),
                        'emp_country_id': post.get('emp_country_id'),
                        'tertiary_qualification': post.get('tertiary_qualification'),
                        'field_of_studies': post.get('field_of_studies'),
                        'pre_tertiary_qualification': post.get('pre_tertiary_qualification'),
                        'aspirant_age': post.get('aspirant_age')
                    }) 
                if post.get('competition_rule'):
                    values['update_bio'] = False
                    values['competition_rule'] = False
                    jnr_aspirants.sudo().write({
                        'updated_cfo_bio': True})
                if post.get('back_home') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                if post.get('back_contact') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = True
                    values['eligibility_status'] = False
                if post.get('back_eligibility') == '<<Back':
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    values['eligibility_status'] = False
                    values['competition_rule'] = False
                if post.get('back_rule') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    values['eligibility_status'] = True
                    values['competition_rule'] = False
                
                if post.get('cfo_team_edit') and post.get('jnr_aspirants'):
                    values['cfo_team_edit'] = True
                    values['cfo_team'] = True
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                    if jnr_aspirants.aspirant_id:
                        values['aspirant_team'] = jnr_aspirants.aspirant_id
                        
             if post.get('jnr_high_school') and not post.get('cfo_team'):
                if post.get('update_bio_info'):
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    jnr_high_school.sudo().write({
                        'name': post.get('name'),
                        'surname': post.get('surname'),
                        'other_names': post.get('other_names'),
                    })
                if post.get('contact_info'):
                    values['institution_details'] = True
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['update_bio_info'] = False
                    jnr_high_school.sudo().write({
                        'mobile': post.get('mobile'),
                        'phone': post.get('phone'),
                        'home_phone': post.get('home_phone'),
                        'email_1': post.get('email_1'),
                        'email_2': post.get('email_2'),
                        'street': post.get('street'),
                        'street2': post.get('street2'),
                        'city': post.get('city'),
                        'state_id': post.get('state_id'),
                        'zip': post.get('zip'),
                        'country_id': post.get('country_id')
                    })
                if post.get('institution_details'):
                    values['competition_rule'] = True
                    values['update_bio'] = True
                    values['institution_details'] = False
                    values['update_bio_info'] = False
                    jnr_high_school.sudo().write({
                        'school_name': post.get('school_name'),
                        'department': post.get('department'),
                        'website': post.get('website'),
                        'stu_street': post.get('stu_street'),
                        'stu_street2': post.get('stu_street2'),
                        'stu_city': post.get('stu_city'),
                        'stu_state_id': post.get('stu_state_id'),
                        'stu_zip': post.get('stu_zip'),
                        'stu_country_id': post.get('stu_country_id'),
                    })
                if post.get('competition_rule'):
                    values['update_bio'] = False
                    values['competition_rule'] = False
                    values['institution_details'] = False
                    jnr_high_school.sudo().write({
                        'updated_academic_bio': True
                    })
                if post.get('back_home') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                if post.get('back_contact') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = True
                    values['institution_details'] = False
                if post.get('back_institution') == '<<Back':
                    values['contact_info'] = True
                    values['institution_details'] = False
                    values['competition_rule'] = False
                if post.get('back_competition') == '<<Back':
                    values['update_bio_info'] = False
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['institution_details'] = True
                    values['competition_rule'] = False
            
             if post.get('cfo_team_edit') and post.get('new_form'):
                    list = []
                    values['cfo_team_edit'] = True
                    values['cfo_team'] = True
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                    if jnr_high_school.cfo_team_ids:
                            values['high_school_team'] = ''
            
             if post.get('cfo_team_edit') and post.get('jnr_high_school'):
                list = []
                values['cfo_team_edit'] = True
                values['cfo_team'] = True
                values['update_bio'] = False
                values['update_bio_info'] = False
                if jnr_high_school.cfo_team_ids:
                        values['high_school_team'] = jnr_high_school.cfo_team_ids
                if post.get('high_school_team'):
                    team_id = request.env['cfo.team.jnr'].sudo().search([('id', '=', post.get('high_school_team'))])
                    values['high_school_team'] = team_id
               
             if post.get('jnr_mentors'):
                if post.get('update_bio_info'):
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    jnr_mentors.sudo().write({
                        'name': post.get('name'),
                        'surname': post.get('surname'),
                        'other_names': post.get('other_names'),
                    })
                if post.get('contact_info'):
                    values['competition_rule'] = True
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['update_bio_info'] = False
                    jnr_mentors.sudo().write({
                        'mobile': post.get('mobile'),
                        'email_1': post.get('email_1'),
                        'email_2': post.get('email_2'),
                        'street': post.get('street'),
                        'street2': post.get('street2'),
                        'city': post.get('city'),
                        'state_id': post.get('state_id'),
                        'zip': post.get('zip'),
                        'country_id': post.get('country_id'),
                    })
                if post.get('competition_rule'):
                    values['update_bio'] = False
                    values['competition_rule'] = False
                    values['contact_info'] = False
                    jnr_mentors.sudo().write({
                        'updated_mentors_bio': True
                    })
                if post.get('back_home') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                if post.get('back_contact') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = True
                    values['competition_rule'] = False
                if post.get('back_competition') == '<<Back':
                    values['update_bio_info'] = False
                    values['update_bio'] = True
                    values['contact_info'] = True
                    values['competition_rule'] = False
                    
             if post.get('jnr_brand_ambassador'):
                if post.get('update_bio_info'):
                    values['contact_info'] = True
                    values['update_bio'] = True
                    values['update_bio_info'] = False
                    jnr_brand_ambassador.sudo().write({
                        'name': post.get('name'),
                        'surname': post.get('surname'),
                        'other_names': post.get('other_names'),
                    })
                if post.get('contact_info'):
                    values['competition_rule'] = True
                    values['update_bio'] = True
                    values['contact_info'] = False
                    values['update_bio_info'] = False
                    jnr_brand_ambassador.sudo().write({
                        'mobile': post.get('mobile'),
                        'email_1': post.get('email_1'),
                        'email_2': post.get('email_2'),
                    })
                if post.get('competition_rule'):
                    values['update_bio'] = False
                    values['competition_rule'] = False
                    values['contact_info'] = False
                    jnr_brand_ambassador.sudo().write({
                        'updated_brand_amb_bio': True
                    })
                if post.get('back_home') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = False
                    values['update_bio_info'] = False
                if post.get('back_contact') == '<<Back':
                    values['contact_info'] = False
                    values['update_bio'] = True
                    values['update_bio_info'] = True
                    values['competition_rule'] = False
                if post.get('back_competition') == '<<Back':
                    values['update_bio_info'] = False
                    values['update_bio'] = True
                    values['contact_info'] = True
                    values['competition_rule'] = False
        print("\n\n\n\n\n=====values========",values)
        return request.render('cfo_snr_jnr.cfo_junior', values)
    
    
    @http.route('/create_team_junior', type='json', auth="public", website=True)
    def create_team_junior(self, **post):
        if post.get('aspirant_id') and not post.get('aspirant_team'):
            aspirant_id = request.env['cfo.jnr.aspirants'].sudo().search([('id', '=', int(post.get('aspirant_id')))],
                                                                         limit=1)
            if not aspirant_id.aspirant_id:
                team_id = request.env['cfo.team.jnr'].sudo().create({
                    'name': post.get('name'),
                    'ref_name': post.get('sys_name'),
                    'team_type': 'CFO Aspirant',
                    'cfo_competition_year': aspirant_id.cfo_competition_year,
                    'aspirant_admin_id': aspirant_id.id,
                    'cfo_comp': 'CFO JNR'
                })
                if post.get('member_request_list'):
                    '''
                    Send email for Join Our Team.
                    '''
                    # for each_request in post.get('member_request_list'):
                    #     res = request.env['cfo.jnr.aspirants'].sudo().search([('user_id', '=', int(each_request.get('user_id')))])
                    #     aspirant_team_member_id = request.env['jnr.aspirant.team.member'].sudo().search([('related_user_id', '=', res.id), ('member_status', '=', 'Accept')])
                    #     res.sudo().write({
                    #             'is_request': True,
                    #             'new_team_id': team_id.id
                    #         })
                    #     template = request.env.ref('cfo_snr_jnr.email_template_request_for_join',
                    #                                raise_if_not_found=False)
                    #     if template:
                    #         template.sudo().with_context(
                    #             user_type=each_request.get('user_type'),
                    #             team_id=team_id.id,
                    #             team_name=team_id.name,
                    #             email_to=each_request.get('email')
                    #         ).send_mail(res.id, force_send=True)
                    #     aspirant_team_member_id.write({'aspirant_member_requested':True})

                    for each_request in post.get('member_request_list'):
                        if each_request.get('user_type') == 'Mentor' or each_request.get('user_type') == 'Brand Ambassador':
                            mentor_id = request.env['mentors.jnr'].sudo().search(
                                [('user_id', '=', int(each_request.get('user_id')))])
                            amb_id = request.env['brand.ambassador.jnr'].sudo().search(
                                [('user_id', '=', int(each_request.get('user_id')))])
                            if mentor_id:
                                template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor',
                                                                  raise_if_not_found=False)
                                if template_mentor:
                                    template_mentor.sudo().with_context(
                                        user_type=each_request.get('user_type'),
                                        team_id=team_id.id,
                                        team_name=team_id.ref_name,
                                        # email_to=each_request.get('email'),
                                        email_cc='thecfo@charterquest.co.za',
                                    ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(mentor_id.id, force_send=True)
                            if amb_id:
                                template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb',
                                                               raise_if_not_found=False)
                                if template_amb:
                                    template_amb.sudo().with_context(
                                        user_type=each_request.get('user_type'),
                                        team_id=team_id.id,
                                        team_name=team_id.ref_name,
                                        # email_to=each_request.get('email'),
                                        email_cc='thecfo@charterquest.co.za',
                                    ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(amb_id.id, force_send=True)

                        if each_request.get('user_type') in ['Leader', 'Member']:
                            res = request.env['cfo.jnr.aspirants'].sudo().search(
                                [('user_id', '=', int(each_request.get('user_id')))])
                            aspirant_team_member_id = request.env['jnr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', res.id), ('member_status', '=', 'Accept')])

                            res.sudo().write({
                                'is_request': True,
                                'new_team_id': team_id.id
                            })
                            template = request.env.ref('cfo_snr_jnr.email_template_request_for_join',
                                                       raise_if_not_found=False)
                            if template:
                                template.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id, is_request=True, cfo_login=True).send_mail(res.id,
                                                                                                           force_send=True)

                            aspirant_team_member_id.write({'aspirant_member_requested': True})
                team_id._compute_remaining_time_deadline()
                for each in post.get('list_of_member'):
                    member_ids = request.env['jnr.aspirant.team.member'].sudo().search(
                        [('team_id', '=', team_id.id), ('user_type', '=', 'Member')])
                    user = request.env['cfo.jnr.aspirants'].sudo().search(
                        [('email_1', '=', str(each['email']))], limit=1)
                    mentor = request.env['mentors.jnr'].sudo().search(
                        [('email_1', '=', str(each['email']))], limit=1)
                    brand_ambassador = request.env['brand.ambassador.jnr'].sudo().search(
                        [('email_1', '=', str(each['email']))], limit=1)
                    
                    if not user and not mentor and not brand_ambassador and not member_ids:
                        return {'error': 'error'}
                    else:
                        if len(member_ids) <= 3:
                            if each['user_type'] == 'Member':
                                if not request.env['jnr.aspirant.team.member'].sudo().search(
                                        [('related_user_id', '=', user.id), ('user_type', '=', 'Member')]):
                                    request.env['jnr.aspirant.team.member'].sudo().create({
                                        'team_id': team_id.id,
                                        'related_user_id': user.id,
                                        'user_type': each['user_type'],
                                        'member_status': 'Accept'
                                    })
                                    user.sudo().write({
                                        'team_status': 'Accept',
                                        'team_member' : True,
                                        'aspirant_id' : team_id.id,
                                        'new_team_id': team_id.id
                                    })
                                elif request.env['jnr.aspirant.team.member'].sudo().search(
                                        [('related_user_id', '=', user.id), ('user_type', '=', 'Member'), ('aspirant_member_requested', '=', True)]):
                                     request.env['jnr.aspirant.team.member'].sudo().create({
                                        'team_id': team_id.id,
                                        'related_user_id': user.id,
                                        'user_type': each['user_type'],
                                        'member_status': 'Pending'
                                     })
                        else:
                            return {'member_limit_error': True}
                        if each['user_type'] == 'Admin':
                            team_id.aspirant_admin_id = user.id
                            
                            if not request.env['jnr.aspirant.team.member'].sudo().search(
                                    [('related_user_id', '=', user.id), ('user_type', '=', 'Admin')]):
                                
                                mem_id = request.env['jnr.aspirant.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_id': user.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Accept'
                                })
                                user.sudo().write({
                                    'team_status': 'Accept',
                                    'team_admin' : True,
                                    'aspirant_id' : team_id.id,
                                    'new_team_id': team_id.id
                                })
                        if each['user_type'] == 'Leader':
                            team_id.team_leader_id = user.id
                            if not request.env['jnr.aspirant.team.member'].sudo().search(
                                    [('related_user_id', '=', user.id), ('user_type', '=', 'Leader')]):
                                request.env['jnr.aspirant.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_id': user.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Accept'
                                })
                                user.sudo().write({
                                    'team_status': 'Accept',
                                    'team_leader' : True,
                                    'aspirant_id' : team_id.id,
                                    'new_team_id': team_id.id
                                })
                                leader_admin = request.env['jnr.aspirant.team.member'].sudo().search([('related_user_id', '=', user.id)])
                                if len(leader_admin) > 1:
                                        for leader_admin in leader_admin:
                                           leader_admin.related_user_id.write({
                                                                                'team_leader' : True,
                                                                                'team_admin' : True,
                                                                                   })
                        elif request.env['jnr.aspirant.team.member'].sudo().search(
                                    [('related_user_id', '=', user.id), ('user_type', '=', 'Leader'), ('aspirant_member_requested', '=', True)]):
                                 request.env['jnr.aspirant.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_id': user.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                                
                        if each['user_type'] == 'Mentor':
                            team_id.mentor_id = mentor.id
                            mentor.sudo().write({
                                'team_ids':[(4, team_id.id)],
                                'team_status': 'Pending',
                                'new_team_id': team_id.id,
                            })
                        if each['user_type'] == 'Brand Ambassador':
                            team_id.brand_amb_id = brand_ambassador.id
                            brand_ambassador.sudo().write({
                                'team_status': 'Pending',
                                'new_team_id': team_id.id,
                                'team_ids':[(4, team_id.id)],
                            })
                            
                aspirant_id.write({
                    'aspirant_id': team_id.id
                })
            else:
                return {'team_error': True}
            
        if post.get('aspirant_team'):
            aspirant_id = request.env['cfo.jnr.aspirants'].sudo().search([('id', '=', int(post.get('aspirant_id')))])
            team_id = request.env['cfo.team.jnr'].sudo().search([('id', '=', int(post.get('aspirant_team')))], limit=1)
            member = request.env['jnr.aspirant.team.member'].sudo().search([('team_id', '=', team_id.id)])
#             team_id_mentor = request.env['cfo.team.jnr'].sudo().search([('id', '=', int(post.get('')))], limit=1)
            for each in member:
                each.unlink()
            team_id.sudo().write({
                'name': post.get('name'),
                'ref_name': post.get('sys_name'),
                'team_type': 'CFO Aspirant',
                'aspirant_admin_id': aspirant_id.id,
                'cfo_competition_year': aspirant_id.cfo_competition_year,
                'cfo_comp': 'CFO JNR'
            })
            if post.get('member_request_list'):
                '''
                Send email for Join Our Team.
                '''
                # for each_request in post.get('member_request_list'):
                #     res = request.env['cfo.jnr.aspirants'].sudo().search([('user_id', '=', int(each_request.get('user_id')))])
                #     aspirant_team_member_id = request.env['jnr.aspirant.team.member'].sudo().search([('related_user_id', '=', res.id), ('member_status', '=', 'Accept')])
                #     res.sudo().write({
                #             'is_request': True,
                #             'new_team_id': team_id.id
                #         })
                #     print("\n\n\n\n=======99999999999")
                #     template = request.env.ref('cfo_snr_jnr.email_template_request_for_join',
                #                                raise_if_not_found=False)
                #     if template:
                #         template.sudo().with_context(
                #             user_type=each_request.get('user_type'),
                #             team_id=team_id.id,
                #             team_name=team_id.name,
                #             email_to=each_request.get('email')
                #         ).send_mail(res.id, force_send=True)
                # aspirant_team_member_id.write({'aspirant_member_requested':True})
                for each_request in post.get('member_request_list'):
                    if each_request.get('user_type') == 'Mentor' or each_request.get('user_type') == 'Brand Ambassador':
                        mentor_id = request.env['mentors.jnr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        amb_id = request.env['brand.ambassador.jnr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        if mentor_id:
                            template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor',
                                                              raise_if_not_found=False)
                            if template_mentor:
                                template_mentor.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(mentor_id.id, force_send=True)
                        if amb_id:
                            template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb',
                                                           raise_if_not_found=False)

                            if template_amb:
                                template_amb.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(amb_id.id, force_send=True)

                    if each_request.get('user_type') in ['Leader', 'Member']:
                        res = request.env['cfo.jnr.aspirants'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        aspirant_team_member_id = request.env['jnr.aspirant.team.member'].sudo().search(
                            [('related_user_id', '=', res.id), ('member_status', '=', 'Accept')])
                        res.sudo().write({
                            'is_request': True,
                            'new_team_id': team_id.id
                        })

                        template = request.env.ref('cfo_snr_jnr.email_template_request_for_join',
                                                   raise_if_not_found=False)
                        if template:
                            template.sudo().with_context(
                                user_type=each_request.get('user_type'),
                                team_id=team_id.id,
                                team_name=team_id.ref_name,
                                # email_to=each_request.get('email'),
                                email_cc='thecfo@charterquest.co.za',
                            ).with_context(team=team_id.id,is_request=True,cfo_login=True).send_mail(res.id, force_send=True)

                        aspirant_team_member_id.write({'aspirant_member_requested': True})


            for each in post.get('list_of_member'):
                member_ids = request.env['jnr.aspirant.team.member'].sudo().search(
                    [('team_id', '=', team_id.id), ('user_type', '=', 'Member')])
                user = request.env['cfo.jnr.aspirants'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                mentor = request.env['mentors.jnr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                brand_ambassador = request.env['brand.ambassador.jnr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                if not user and not mentor and not brand_ambassador and  not member_ids:
                    return {'error': 'error'}
                else:
                    if len(member_ids) <= 3:
                        if each['user_type'] == 'Member':
                            if not request.env['jnr.aspirant.team.member'].sudo().search(
                                    [('related_user_id', '=', user.id), ('user_type', '=', 'Member')]):
                                request.env['jnr.aspirant.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_id': user.id,
                                    'team_member' : True,
                                    'user_type': each['user_type'],
                                    'member_status': 'Accept'
                                })
                                user.sudo().write({
                                    'team_status': 'Accept',
                                    'new_team_id': team_id.id,
                                    'aspirant_id' :team_id.id,
                                    'team_member' : True,
                                    'team_admin' :False,
                                })
                            elif request.env['jnr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Member'), ('aspirant_member_requested', '=', True)]):
                             request.env['jnr.aspirant.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_id': user.id,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                             })
                    else:
                        return {'member_limit_error': True}
                    if each['user_type'] == 'Admin':
                        team_id.aspirant_admin_id = user.id
                        if not request.env['jnr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Admin')]):
                            request.env['jnr.aspirant.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_id': user.id,
                                'team_admin':True,
                                'user_type': each['user_type'],
                                'member_status': 'Accept'
                            })
                            user.sudo().write({
                                'team_status': 'Accept',
                                'new_team_id': team_id.id,
                                'aspirant_id' :team_id.id,
                            })
                    if each['user_type'] == 'Leader':
                        team_id.aspirant_leader_id = user.id
                        team_leader_1 = request.env['jnr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Leader')])
                        if not request.env['jnr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Leader')]):
                            request.env['jnr.aspirant.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_id': user.id,
                                'team_leader' : True,
                                'user_type': each['user_type'],
                                'member_status': 'Accept'
                            })
                            user.sudo().write({
                                'team_status': 'Accept',
                                'new_team_id': team_id.id,
                                'aspirant_id' :team_id.id,
                                'team_leader' : True,
                                'team_admin' :False,
                            })
                            leader_admin = request.env['jnr.aspirant.team.member'].sudo().search([('related_user_id', '=', user.id)])
                            if len(leader_admin) > 1:
                                for leader_admin in leader_admin:
                                   leader_admin.related_user_id.write({
                                                                        'team_leader' : True,
                                                                        'team_admin' : True,
                                                                           })
                        if request.env['jnr.aspirant.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Leader'), ('aspirant_member_requested', '=', True)]):
                            request.env['jnr.aspirant.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_id': user.id,
                                'team_leader' : True,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })
                    if each['user_type'] == 'Mentor':
                        teamslt = []
                        team_id.mentor_id = mentor.id
                        mentor.sudo().write({
                            'team_ids':[(4, team_id.id)],
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                        })
                    if each['user_type'] == 'Brand Ambassador':
                        team_id.brand_amb_id = brand_ambassador.id
                        brand_ambassador.sudo().write({
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                            'aspirant_id' :team_id.id,
                            'team_ids':[(4, team_id.id)],
                        })
            
        
        request.env['jnr.aspirant.team.member'].sudo().search([('team_id', '=', False), ('related_user_id', '=', False)]).unlink()
        return {'success': 'success '}
    
    
    
    @http.route('/create_high_school_team', type='json', auth='public', website=True)
    def create_high_school_team(self, **post):
        if post.get('jnr_high_school') and not post.get('high_school_team'):
            jnr_highschool_id = request.env['academic.institution.jnr'].sudo().search(
                [('id', '=', int(post.get('jnr_high_school')))],
                limit=1)

            team_id = request.env['cfo.team.jnr'].sudo().create({
                'name': post.get('name'),
                'ref_name': post.get('sys_name'),
                'team_type': 'Secondary/High School',
                'cfo_competition_year': jnr_highschool_id.cfo_competition_year,
                'academic_admin_id': jnr_highschool_id.id,
                'cfo_comp': 'CFO JNR'
            })
            if post.get('highschool_member_list'):
                '''
                Send email for Join Our Team.
                '''
                for each_request in post.get('highschool_member_list'):
                    # res = request.env['cfo.jnr.aspirants'].sudo().search([('user_id', '=', int(each_request.get('user_id')))])
                    # team_member_id = request.env['jnr.highschool.team.member'].sudo().search(
                    #             [('related_user_aspirant_id', '=', res.id), ('member_status', '=', 'Accept'), ])
                    # res.sudo().write({
                    #         'is_request': True,
                    #         'new_team_id': team_id.id
                    #     })
                    # template = request.env.ref('cfo_snr_jnr.email_template_request_for_join',
                    #                            raise_if_not_found=False)
                    # if template:
                    #     template.sudo().with_context(
                    #         user_type=each_request.get('user_type'),
                    #         team_id=team_id.id,
                    #         team_name=team_id.name,
                    #         email_to=each_request.get('email')
                    #     ).send_mail(res.id, force_send=True)
                    # team_member_id.write({'member_requested':True})
                    #
                    if each_request.get('user_type') == 'Mentor' or each_request.get('user_type') == 'Brand Ambassador':
                        mentor_id = request.env['mentors.jnr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        amb_id = request.env['brand.ambassador.jnr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        if mentor_id:
                            template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor',
                                                              raise_if_not_found=False)
                            if template_mentor:
                                template_mentor.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id, is_request=True, cfo_login=True).send_mail(mentor_id.id,
                                                                                                           force_send=True)
                        if amb_id:
                            template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb',
                                                           raise_if_not_found=False)
                            if template_amb:
                                template_amb.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id, is_request=True, cfo_login=True).send_mail(amb_id.id,
                                                                                                           force_send=True)

                    if each_request.get('user_type') in ['Leader', 'Member']:
                        res = request.env['cfo.jnr.aspirants'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        print("\n\n\n=========member=====", res)
                        team_member_id = request.env['jnr.highschool.team.member'].sudo().search(
                            [('related_user_aspirant_id', '=', res.id), ('member_status', '=', 'Accept'), ])
                        res.sudo().write({
                            'is_request': True,
                            'new_team_id': team_id.id
                        })
                        template = request.env.ref('cfo_snr_jnr.email_template_request_for_join',
                                                   raise_if_not_found=False)
                        if template:
                            template.sudo().with_context(
                                user_type=each_request.get('user_type'),
                                team_id=team_id.id,
                                team_name=team_id.ref_name,
                                # email_to=each_request.get('email'),
                                email_cc='thecfo@charterquest.co.za',
                            ).with_context(team=team_id.id, is_request=True, cfo_login=True).send_mail(res.id,
                                                                                                       force_send=True)
                        team_member_id.write({'member_requested': True})
                team_id._compute_remaining_time_deadline()
            for each in post.get('list_of_member'):
                member_ids = request.env['jnr.highschool.team.member'].sudo().search(
                    [('team_id', '=', team_id.id), ('user_type', '=', 'Member')])
                user_aspirant = request.env['cfo.jnr.aspirants'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                user = request.env['academic.institution.jnr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                mentor = request.env['mentors.jnr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                brand_ambassador = request.env['brand.ambassador.jnr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                if not user and not mentor and not brand_ambassador and not member_ids and not user_aspirant:
                         return {'error': 'error'}
                else:
                    if len(member_ids) <= 3:
                        if each['user_type'] == 'Member':
                            if not request.env['jnr.highschool.team.member'].sudo().search(
                                    [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Member')]):
                                request.env['jnr.highschool.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id': user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                                user_aspirant.sudo().write({
                                        'team_member' : True,
                                        'aspirant_id':team_id.id
                                    })
                            if request.env['jnr.highschool.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Member'), ('member_requested', '=', True)]):
                                request.env['jnr.highschool.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id': user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                            })
                             
                                 
                    else:
                        return {'member_limit_error': True}
 
                    if each['user_type'] == 'Admin':
                        team_id.academic_admin_id = user.id
                        acadamic_admin_new_id = request.env['jnr.highschool.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Admin')])
                        request.env['jnr.highschool.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_id': user.id,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })
                        user.sudo().write({
                                           'team_admin':True,
                                           'cfo_team_ids':[(4, team_id.id)]
                                           })
                      
                    if each['user_type'] == 'Leader':
                        team_id.team_leader_id = user_aspirant.id
                        if not request.env['jnr.highschool.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader')]):
                            request.env['jnr.highschool.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Accept'
                            })
                            user_aspirant.sudo().write({
                                    'team_leader' : True,
                                    'aspirant_id':team_id.id
                                })
                        if request.env['jnr.highschool.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader'), ('member_requested', '=', True)]):
                            request.env['jnr.highschool.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })
 
                    if each['user_type'] == 'Mentor':
                        team_id.mentor_id = mentor.id
                        mentor.sudo().write({
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                            'team_ids':[(4, team_id.id)],
                        })
 
                    if each['user_type'] == 'Brand Ambassador':
                        team_id.brand_amb_id = brand_ambassador.id
                        brand_ambassador.sudo().write({
                            'new_team_id': team_id.id,
                            'team_ids':[(4, team_id.id)],
                        })
                jnr_highschool_id.write({'cfo_team_ids': [(4, team_id.id)]
                                   })
        if post.get('high_school_team'):
            jnr_highschool_id = request.env['academic.institution.jnr'].sudo().search(
                [('id', '=', int(post.get('jnr_high_school')))])
            team_id = request.env['cfo.team.jnr'].sudo().search([('id', '=', int(post.get('high_school_team')))], limit=1)
            member = request.env['jnr.highschool.team.member'].sudo().search([('team_id', '=', team_id.id)])
            for each in member:
                each.unlink()
            team_id.sudo().write({
                'name': post.get('name'),
                'ref_name': post.get('sys_name'),
                'team_type': 'Secondary/High School',
                'academic_admin_id': jnr_highschool_id.id,
                'cfo_competition_year': jnr_highschool_id.cfo_competition_year,
                'cfo_comp': 'CFO JNR'
            })
            if post.get('highschool_member_list'):
                '''
                Send email for Join Our Team.
                '''
                for each_request in post.get('highschool_member_list'):
                    # res = request.env['cfo.jnr.aspirants'].sudo().search([('user_id', '=', int(each_request.get('user_id')))])
                    # team_member_id = request.env['jnr.highschool.team.member'].sudo().search(
                    #             [('related_user_aspirant_id', '=', res.id), ('member_status', '=', 'Accept'), ])
                    # res.sudo().write({
                    #         'is_request': True,
                    #         'new_team_id': team_id.id
                    #     })
                    # print("\n\n\n\n===================77777777777")
                    # template = request.env.ref('cfo_snr_jnr.email_template_request_for_join',
                    #                            raise_if_not_found=False)
                    # if template:
                    #     template.sudo().with_context(
                    #         user_type=each_request.get('user_type'),
                    #         team_id=team_id.id,
                    #         team_name=team_id.name,
                    #         email_to=each_request.get('email')
                    #     ).send_mail(res.id, force_send=True)
                    # team_member_id.write({'member_requested':True})
                    if each_request.get('user_type') == 'Mentor' or each_request.get('user_type') == 'Brand Ambassador':
                        mentor_id = request.env['mentors.jnr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        amb_id = request.env['brand.ambassador.jnr'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        if mentor_id:
                            template_mentor = request.env.ref('cfo_snr_jnr.email_template_request_for_join_mentor',
                                                              raise_if_not_found=False)
                            if template_mentor:
                                template_mentor.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id, is_request=True, cfo_login=True).send_mail(mentor_id.id,
                                                                                                           force_send=True)
                        if amb_id:
                            template_amb = request.env.ref('cfo_snr_jnr.email_template_request_for_join_amb',
                                                           raise_if_not_found=False)
                            if template_amb:
                                template_amb.sudo().with_context(
                                    user_type=each_request.get('user_type'),
                                    team_id=team_id.id,
                                    team_name=team_id.ref_name,
                                    # email_to=each_request.get('email'),
                                    email_cc='thecfo@charterquest.co.za',
                                ).with_context(team=team_id.id, is_request=True, cfo_login=True).send_mail(amb_id.id,
                                                                                                           force_send=True)

                    if each_request.get('user_type') in ['Leader', 'Member']:
                        res = request.env['cfo.jnr.aspirants'].sudo().search(
                            [('user_id', '=', int(each_request.get('user_id')))])
                        print("\n\n\n=========member=====", res)
                        team_member_id = request.env['jnr.highschool.team.member'].sudo().search(
                            [('related_user_aspirant_id', '=', res.id), ('member_status', '=', 'Accept'), ])
                        res.sudo().write({
                            'is_request': True,
                            'new_team_id': team_id.id
                        })
                        template = request.env.ref('cfo_snr_jnr.email_template_request_for_join',
                                                   raise_if_not_found=False)
                        if template:
                            template.sudo().with_context(
                                user_type=each_request.get('user_type'),
                                team_id=team_id.id,
                                team_name=team_id.ref_name,
                                # email_to=each_request.get('email'),
                                email_cc='thecfo@charterquest.co.za',
                            ).with_context(team=team_id.id, is_request=True, cfo_login=True).send_mail(res.id,
                                                                                                       force_send=True)
                        team_member_id.write({'member_requested': True})
                team_id._compute_remaining_time_deadline()
            for each in post.get('list_of_member'):
                member_ids = request.env['jnr.highschool.team.member'].sudo().search(
                    [('team_id', '=', team_id.id), ('user_type', '=', 'Member')])
                user = request.env['academic.institution.jnr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                user_aspirant = request.env['cfo.jnr.aspirants'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                mentor = request.env['mentors.jnr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                brand_ambassador = request.env['brand.ambassador.jnr'].sudo().search(
                    [('email_1', '=', str(each['email']))], limit=1)
                if not user and not mentor and not brand_ambassador and  not member_ids and  not user_aspirant:
                    return {'error': 'error'}
                else:
                    if len(member_ids) <= 3:
                        if each['user_type'] == 'Member':
                            if not request.env['jnr.highschool.team.member'].sudo().search(
                                    [('related_user_aspirant_id', '=', user_aspirant.id)]):
                                request.env['jnr.highschool.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id':user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                                })
                                user_aspirant.sudo().write({
                                    'aspirant_id': team_id.id,
                                    'team_member' : True,
                                })
                        if request.env['jnr.highschool.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Member'), ('member_requested', '=', True)]):
                                request.env['jnr.highschool.team.member'].sudo().create({
                                    'team_id': team_id.id,
                                    'related_user_aspirant_id': user_aspirant.id,
                                    'user_type': each['user_type'],
                                    'member_status': 'Pending'
                            })
                    else:
                        return {'member_limit_error': True}
                    if each['user_type'] == 'Admin':
                        team_id.academic_admin_id = user.id
                        acadamic_new_admin_id = request.env['jnr.highschool.team.member'].sudo().search(
                                [('related_user_id', '=', user.id), ('user_type', '=', 'Admin')])
                        request.env['jnr.highschool.team.member'].sudo().create({
                            'team_id': team_id.id,
                            'related_user_id': user.id,
                            'user_type': each['user_type'],
                            'member_status': 'Pending'
                        })
                        user.sudo().write({
                            'cfo_team_ids':[(4, team_id.id)],
                            'team_admin':True,
                        })
                    if each['user_type'] == 'Leader':
                        team_id.team_leader_id = user_aspirant.id
                        if not request.env['jnr.highschool.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader'), ]):
                            request.env['jnr.highschool.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Accept'
                            })
                            user_aspirant.sudo().write({
                                'aspirant_id':team_id.id,
                                'team_leader' : True,
                                'team_admin' :False,
                            })
                        if request.env['jnr.highschool.team.member'].sudo().search(
                                [('related_user_aspirant_id', '=', user_aspirant.id), ('user_type', '=', 'Leader'), ('member_requested', '=', True)]):
                            request.env['jnr.highschool.team.member'].sudo().create({
                                'team_id': team_id.id,
                                'related_user_aspirant_id': user_aspirant.id,
                                'user_type': each['user_type'],
                                'member_status': 'Pending'
                            })
                   
                    if each['user_type'] == 'Mentor':
                        team_id.mentor_id = mentor.id
                        mentor.sudo().write({
                            'team_ids':[(4, team_id.id)],
                            'team_status': 'Pending',
                            'new_team_id': team_id.id
                        })
                    if each['user_type'] == 'Brand Ambassador':
                        team_id.brand_amb_id = brand_ambassador.id
                        brand_ambassador.sudo().write({
                            'team_status': 'Pending',
                            'new_team_id': team_id.id,
                            'team_ids':[(4, team_id.id)],
                        })
        request.env['jnr.highschool.team.member'].sudo().search([('team_id', '=', False), ('related_user_aspirant_id', '=', False)]).unlink()
        return {'success': 'success '}
    
    
    @http.route('/remove_member_school', type='json', auth="public", website=True)
    def remove_member_school(self, **post):
        team_id = request.env['cfo.team.jnr'].sudo().search([('id', '=', post.get('team_id'))])
        if post.get('member_type') == 'Brand Ambassador':
                amb_delete = team_id.write({'brand_amb_id':''})
        if post.get('member_type') == 'Mentor':
                mnt_delete = team_id.write({'mentor_id':''})
        if post.get('member_id'):
            member = request.env['snr.academic.team.member'].sudo().search([('id', '=', int(post.get('member_id')))])
            if member.user_type == 'Leader':
                member.related_user_id.write({'team_leader':False})
            if member:
                member.related_user_id.aspirant_id = False
                member.unlink()
        return True
    
    @http.route('/submit_cfo_jnr_report_data', type="json", auth="public", website=True)
    def submit_cfo_jnr_report_data(self, **post):
        aspirant_id = request.env['cfo.jnr.aspirants'].sudo().search([('id', '=', post.get('aspirant_id'))])
        team_id = request.env['cfo.team.jnr'].sudo().search([('id', '=', post.get('team_id'))])
        list_without_bio_member=[]
        for team_id in team_id:
            for team_member in team_id.highschool_team_member_ids:
                if team_member.related_user_aspirant_id and  not team_member.related_user_aspirant_id.updated_cfo_bio:
                    list_without_bio_member.append({'member_name':team_member.related_user_aspirant_id.partner_id.name,'member_type':team_member.user_type})
            if team_id.mentor_id and not team_id.mentor_id.updated_mentors_bio:
                    list_without_bio_member.append({'member_name':team_id.mentor_id.partner_id.name,'member_type':'Mentor'})
            if team_id.brand_amb_id and not team_id.brand_amb_id.updated_brand_amb_bio:
                    list_without_bio_member.append({'member_name':team_id.brand_amb_id.partner_id.name,'member_type':'Brand Ambassador'})
            if list_without_bio_member:
                return {'bio_not_upadate':True,'list_without_bio_member':list_without_bio_member}
            else:
                return {'jnr_aspirants':aspirant_id, 'aspirant_team':team_id}
        
    @http.route('/cfo_jnr_report', type="http", auth="public", website=True)
    def cfo_jnr_report(self,**post):
         if post.get('aspirant_id') and post.get('team_id'):
             aspirant_id = request.env['cfo.jnr.aspirants'].sudo().search([('id', '=', post.get('aspirant_id'))])
             team_id = request.env['cfo.team.jnr'].sudo().search([('id', '=', post.get('team_id'))])    
             return  request.render('cfo_snr_jnr.cfo_jnr_report_new', {'jnr_aspirants':aspirant_id, 'aspirant_team':team_id})
         
    @http.route('/cfo_jnr_report_form_new', type='http', auth='public', website=True)
    def cfo_snr_report_form(self, **post):
        print("\n\n\n\n\n========cfo jnr report====",post)
        team_id = request.env['cfo.team.jnr'].sudo().search([('id', '=', post.get('aspirant_team'))])
        template = request.env.ref('cfo_snr_jnr.email_template_for_success_report_jnr', raise_if_not_found=False)
        template_mentor = request.env.ref('cfo_snr_jnr.email_template_for_success_report_mentor_jnr',
                                          raise_if_not_found=False)
        template_amb = request.env.ref('cfo_snr_jnr.email_template_for_success_report_ambassador_jnr',
                                       raise_if_not_found=False)

        if team_id and team_id.mentor_id and template_mentor:
            template_mentor.sudo().with_context(
                team_name=team_id.ref_name,
                # email_to=team_id.mentor_id.email_1
            ).send_mail(team_id.mentor_id.id, force_send=True)

        if team_id and team_id.brand_amb_id and template_amb:
            template_amb.sudo().with_context(
                team_name=team_id.ref_name,
                # email_to=team_id.brand_amb_id.email_1
            ).send_mail(team_id.brand_amb_id.id, force_send=True)

        for aspirant_member in team_id.aspirant_team_member_ids:
            if template:
                template.sudo().with_context(
                    team_name=team_id.name,
                    # email_to=aspirant_member.related_user_id.email_1
                ).send_mail(aspirant_member.related_user_id.id, force_send=True)

            team_id.acknowledge_cfo_report = True
            team_id.cfo_report_submission_date = datetime.datetime.now()

        for highschool_member in team_id.highschool_team_member_ids:
            template = request.env.ref('cfo_snr_jnr.email_template_for_success_report', raise_if_not_found=False)
            template_highschool = request.env.ref('cfo_snr_jnr.email_template_for_success_report_jnr_highschool',
                                                raise_if_not_found=False)

            if template_highschool and highschool_member.related_user_id:
                template_highschool.sudo().with_context(
                    team_name=team_id.name,
                    # email_to=highschool_member.related_user_id.email_1
                ).send_mail(highschool_member.related_user_id.id, force_send=True)

            if template and highschool_member.related_user_aspirant_id:
                template.sudo().with_context(
                    team_name=team_id.name,
                    # email_to=highschool_member.related_user_aspirant_id.email_1
                ).send_mail(highschool_member.related_user_aspirant_id.id, force_send=True)
            team_id.acknowledge_cfo_report = True
            team_id.cfo_report_submission_date = datetime.datetime.now()

        if (post.get('pdf') or post.get('doc')):
            if post.get('pdf'):
                filename = post.get('pdf').filename      
                file = post.get('pdf')
                attach_id = request.env['ir.attachment'].sudo().create({
                                        'jnr_team_id': team_id.id,
                                        'name' :filename,
                                        'type': 'binary',
                                        'res_id':1,
                                        'datas_fname':filename,
                                        'datas': base64.b64encode(file.read()),
                                        'member_status': 'Pending',
                                    })
            if post.get('doc'):
                filename = post.get('doc').filename      
                file = post.get('doc')
                attach_id = request.env['ir.attachment'].sudo().create({
                                        'jnr_team_id': team_id.id,
                                        'name' :filename,
                                        'type': 'binary',
                                        'res_id': 2,
                                        'datas_fname':filename,
                                        'datas': base64.b64encode(file.read()),
                                        'member_status': 'Pending',
                                    })
        if (post.get('team_pdf') or post.get('tean_doc')):
            if post.get('team_pdf'):
                filename = post.get('team_pdf').filename
                file = post.get('team_pdf')
                attach_id = request.env['ir.attachment'].sudo().create({
                    'jnr_team_id': team_id.id,
                                        'name' :filename,
                                        'type': 'binary',
                                        'res_id': 3,
                                        'datas_fname':filename,
                                        'datas': base64.b64encode(file.read()),
                                        'member_status': 'Pending',
                })
            if post.get('team_doc'):
                filename = post.get('team_doc').filename
                file = post.get('team_doc')
                attach_id = request.env['ir.attachment'].sudo().create({
                    'jnr_team_id': team_id.id,
                                        'name' :filename,
                                        'type': 'binary',
                                        'res_id': 4,
                                        'datas_fname':filename,
                                        'datas': base64.b64encode(file.read()),
                                        'member_status': 'Pending',
                })
        if post.get('team_png'):
            filename = post.get('team_png').filename
            file = post.get('team_png')
            attach_id = request.env['ir.attachment'].sudo().create({
                'jnr_team_id': team_id.id,
                'name': filename,
                'type': 'binary',
                'datas_fname': filename,
                'datas': base64.b64encode(file.read()),
                'member_status': 'Pending',
            })
            return  request.render('cfo_snr_jnr.report_submit_success')
        if (post.get('pdf_db') or post.get('doc_db')):
            return  request.render('cfo_snr_jnr.report_submit_success')
    
