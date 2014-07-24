#!/usr/bin/env python

import os
import re
import sys
import time
import json
import cPickle as pickle
import pprint
import logging
import webapp2
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
import datetime

today = datetime.datetime.today()
if today.month < 6:
    latest_term = "AUTUMN"
    latest_normal_term = str(today.year-1) + " " + latest_term
    latest_normal_term2 = str(today.year-1) + " " + "WINTER"
    acad_year = "{}-{}".format(today.year-1, today.year)

    latest_terms = [latest_normal_term,
                    latest_normal_term + " RE-EXAM",
                    latest_normal_term2]
else:
    latest_term = "SPRING"
    acad_year = "{}-{}".format(today.year, today.year+1)
    latest_normal_term = str(today.year) + " " + latest_term

    latest_terms = [latest_normal_term,
                    latest_normal_term + " RE-EXAM",
                    str(today.year) + " TERM SUMMER"]

grades = {'AA': 10, 'AB': 9, 'BB': 8, 'BC': 7, 'CC': 6,
          'SS': 10, 'CD': 5, 'DD': 4, 'FF': 0, 'W': 0}
terms = ['SPRING', 'AUTUMN', 'RE-EXAM', 'SUMMER']


database = dict() # For individual student data storing
course_data = dict() # Records of every course for every sem
department_data = dict() # Dept.-wise student records by cur_cg
cg_avgs = dict()
cg_distribution = dict()
cg_stats = dict()
course_stats = dict()
rank_data = dict()

from ResAnalyser import Analyser

def run_once():
    global cg_avgs, cg_distribution, cg_stats, course_data, course_stats, \
           database, department_data, rank_data

    with open('cg_avgs'+'.txt') as cur_file:
        cg_avgs = json.load(cur_file)
    with open('cg_distribution'+'.txt') as cur_file:
        cg_distribution = json.load(cur_file)
    with open('course_data'+'.txt') as cur_file:
        course_data = json.load(cur_file)
    with open('course_stats'+'.txt') as cur_file:
        course_stats = json.load(cur_file)
    with open('database'+'.txt') as cur_file:
        database = json.load(cur_file)
    with open('rank_data'+'.txt') as cur_file:
        rank_data = json.load(cur_file)

run_once()
#All the necessary funcs go here...

class MainHandler(webapp2.RequestHandler):
    def get(self):
        to_render = memcache.get('_static_main__')
        if not to_render:
            to_render = template.render("templates/index.html", {})
            memcache.set('_static_main__',to_render)
        self.response.out.write(to_render)

class CourseHandler(webapp2.RequestHandler):
    def get(self):
        template_values={}
        serial = self.request.get('serial')
        template_values['serial'] = serial
        if not serial or serial == "all":
            to_render = memcache.get('_static_courses_all__')
            if not to_render:
                path = "templates/course_all.html"
                data = sorted(course_data.keys())
                data = sorted(map(lambda x: (x,course_data[x]['Name']),course_data),key=lambda x: x[0])
##                categorised_data = {}
##                for each in data:
##                    if each[0][:3] not in categorised_data:
##                        categorised_data[each[0][:3]] = [each]
##                    else:
##                        categorised_data[each[0][:3]].append(each)
##                template_values['categorised_data'] = categorised_data
                template_values['data'] = data
                to_render = template.render(path, template_values)
                memcache.set('_static_courses_all__', to_render)
        else:
            q = self.request.get('q')
            path = "templates/courses.html"
            if q == 'data':
                data = course_data[serial]
            else:
                course = course_data[serial]['Name']
                template_values['course'] = course
                re = self.request.get('exclude_re')
                per = self.request.get('percent')
                exclude_re,percent = True,True
                if str(re) == '0':
                    exclude_re = False
                if str(per) == '0':
                    percent = False
                data = None
                do = Analyser()
                render_data = do.Course_Performance(serial,exclude_re,percent)
                template_values['terms'] = render_data[0]
                template_values['series'] = render_data[1]
                template_values['exclude_re'] = exclude_re
                template_values['percent'] = percent
            template_values['data'] = data
            to_render = template.render(path, template_values)
        self.response.out.write(to_render)

class StudentHandler(webapp2.RequestHandler):
    def render(self,roll):
        template_values={}
        roll = roll.upper()
        path = "templates/student.html"
        template_values['present'] = True
        template_values['roll'] = roll
        template_values['data'] = None
        if roll:
            if roll in database:
                data = database[roll]
                template_values['data'] = pprint.pformat(data)
                graph = self.request.get('graph')
                if not str(graph) == '0':
                    egp_str = self.request.get('egp')
                    egp = True
                    if str(egp_str) == '0':
                        egp = False
                    mem_template_values = memcache.get('_roll_'+str(roll)+str(graph)+str(egp))
                    if not mem_template_values:
                        template_values['graph'] = True
                        template_values['egp'] = egp
                        do = Analyser()
                        render_data = do.Student_Performance(roll,egp)
                        template_values['terms'] = render_data[0]
                        template_values['term_data'] = render_data[1]
                        ranks = {}
                        cg_roll = database[roll]['CGPA']
                        dept = database[roll]['Branch']
                        batch = database[roll]['Batch']
                        ranks['insti'] = (rank_data['All'].index(cg_roll) + 1,len(rank_data['All']))
                        ranks['dept'] = (rank_data[dept]['All'].index(cg_roll) + 1,len(rank_data[dept]['All']))
                        ranks['batch_dept'] = (rank_data[dept][batch].index(cg_roll) + 1,len(rank_data[dept][batch]))
                        ranks['batch_insti'] = (rank_data[batch].index(cg_roll) + 1,len(rank_data[batch]))
                        template_values['ranks'] = ranks
                    else: template_values = mem_template_values
                else: template_values['graph'] = False
                memcache.set('_roll_'+str(roll)+str(graph),template_values)
            else:
                template_values['present'] = False
        self.response.out.write(template.render(path, template_values))
    def get(self):
        roll = self.request.get('roll')
        self.render(roll)
    def post(self):
        roll = self.request.get('roll')
        self.render(roll)

class StatsHandler(webapp2.RequestHandler):
    def get(self):
        template_values={}
        path = "templates/stats.html"
        template_values['present'] = True
        batch = self.request.get('batch','')
        branch = self.request.get('branch','')
        if not branch and not batch: # Display all statistics links
            data = memcache.get('_stats_data')
            if not data:
                data = {'Lists':[],'Dicts':{}}
                for each in cg_distribution['FalseFalse']:
                    if isinstance(cg_distribution['FalseFalse'][each], list):
                        data['Lists'].append(each)
                    else:
                        data['Dicts'][each] = sorted(list(cg_distribution['FalseFalse'][each].keys()))
                data['Lists'] = sorted(data['Lists'])
                memcache.set('_stats_data',data)
            template_values['data'] = data
        else:                        # Display the relevant statistics
            cumulative = self.request.get('cumulative',False)
            percent = self.request.get('percent',True)

            if str(percent) == '0':
                percent = False
            else:
                percent = True
            if str(cumulative) == '0':
                cumulative = False
            else:
                cumulative = True
            template_values['percent'] = percent
            template_values['cumulative'] = cumulative
            template_values['branch'] = branch
            template_values['batch'] = batch
            series = memcache.get('_stats_'+str(percent)+str(cumulative)+str(branch)+str(batch))
            if not series:
                if not branch:
                    series = cg_distribution[str(percent)+str(cumulative)][batch]
                else:
                    if not batch:
                        series = cg_distribution[str(percent)+str(cumulative)][branch]['All']
                    else:
                        series = cg_distribution[str(percent)+str(cumulative)][branch][batch]
                memcache.set('_stats_'+str(percent)+str(cumulative)+str(branch)+str(batch),series)
            template_values['series'] = series
        self.response.out.write(template.render(path, template_values))

class CommentsHandler(webapp2.RequestHandler):
    def get(self):
        to_render = memcache.get('_static_comments')
        if not to_render:
            to_render = template.render("templates/comments.html", {})
            memcache.set('_static_comments',to_render)
        self.response.out.write(to_render)

class PerformanceHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        q = self.request.get('q', False)
        if q == 'batchwise':
            to_render = memcache.get('_perf_batchwise')
            if not to_render:
                template_values['perfdata'] = cg_avgs[1]
                to_render = template.render("templates/perfbatchwise.html", template_values)
                memcache.set('_perf_batchwise', to_render)
        else:
            to_render = memcache.get('_perf_complete')
            if not to_render:
                template_values['perfdata'] = cg_avgs[0]
                to_render = template.render("templates/performance.html", template_values)
                memcache.set('_perf_complete', to_render)
        self.response.out.write(to_render)

class CoursePerfHandler(webapp2.RequestHandler):
    def get(self):
        to_render = memcache.get('_perf_course')
        if not to_render:
            stats = []
            for cur in sorted(course_stats):
                stats.append([cur, course_stats[cur]])
            template_values = {'course_stats': stats}
            to_render = template.render("templates/course_perf.html", template_values)
            memcache.set('_perf_course',to_render)
        self.response.out.write(to_render)

class PrivacyHandler(webapp2.RequestHandler):
    def get(self):
        to_render = memcache.get('_static_privacy')
        if not to_render:
            to_render = template.render("templates/privacy.html", {})
            memcache.set('_static_privacy',to_render)
        self.response.out.write(to_render)

class TOSHandler(webapp2.RequestHandler):
    def get(self):
        to_render = memcache.get('_static_tos')
        if not to_render:
            to_render = template.render("templates/tos.html", {})
            memcache.set('_static_tos',to_render)
        self.response.out.write(to_render)

class AboutHandler(webapp2.RequestHandler):
    def get(self):
        to_render = memcache.get('_static_about')
        if not to_render:
            to_render = template.render("templates/about.html", {})
            memcache.set('_static_about',to_render)
        self.response.out.write(to_render)

class ChangelogHandler(webapp2.RequestHandler):
    def get(self):
        to_render = memcache.get('_static_changelog')
        if not to_render:
            to_render = template.render("templates/changelog.html", {})
            memcache.set('_static_changelog',to_render)
        self.response.out.write(to_render)

def handle_404(request, response, exception):
    logging.exception(exception)
    response.write('Oops! Yoou seem to have wandered off! '
                   'The requested url/page does not exist. ')
    response.set_status(404)

def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('A server error occurred! Report has been logged. '
                   'If you think this is SEVERE & NOT your fault, '
                   'kindly report it to me by any convenient means :) '
                   '<ashishnitinpatil@gmail.com>')
    response.set_status(500)


app = webapp2.WSGIApplication([('/',MainHandler),
                               ('/courses',CourseHandler),
                               ('/student',StudentHandler),
                               ('/tos',TOSHandler),
                               ('/about',AboutHandler),
                               ('/privacy',PrivacyHandler),
                               ('/comments',CommentsHandler),
                               ('/changelog',ChangelogHandler),
                               ('/stats',StatsHandler),
                               ('/performance',PerformanceHandler),
                               ('/courseperf',CoursePerfHandler),],
                               debug=True)
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500