# Copyright 2013 @!mmorta!
#
# Licensed under Creative Commons Attribution-ShareAlike 3.0 Unported License;
# Please refer to the LICENSE.txt for details.

#All the importing business goes here...
import os, re, sys, time, logging
import json
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import memcache


# Begin ResAnalyser --->

latest_term = ['AUTUMN 2012','RE-EXAM AUTUMN 2012']
database = {} # For individual student data storing
course_data = {} # For record keeping of every course for every sem
rank_data = {} # Marklists for all dept, batches, etc
grades = {'AA':10,'AB':9,'BB':8,'BC':7,'CC':6,'CD':5,'DD':4,'W':0,'FF':0,'SS':0}
terms = ['SPRING','AUTUMN','RE-EXAM','SUMMER']
data_file = open(os.path.join(os.getcwd(),'database.txt'),'r')
course_file = open(os.path.join(os.getcwd(),'course_data.txt'),'r')
rank_file = open(os.path.join(os.getcwd(),'rank_data.txt'),'r')

def gather_data(needed='Student'): # Load stuff from the txt files
    global database, course_data, rank_data, rank_file, course_file, data_file
    if needed == 'Course':
        if course_file.closed:
            course_file = open(os.path.join(os.getcwd(),'course_data.txt'),'r')
        course_data = json.load(course_file)
        course_file.close()
    else:
        if data_file.closed:
            data_file = open(os.path.join(os.getcwd(),'database.txt'),'r')
        if rank_file.closed:
            rank_file = open(os.path.join(os.getcwd(),'rank_data.txt'),'r')
        database = json.load(data_file)
        data_file.close()
        rank_data = json.load(rank_file)
        rank_file.close()

# Analysis shit! :-P  -->

class Analyser:
    def All_Courses(self,serial=True, terms=True, alphabetically = True):
        data = []
        for each in course_data:
            to_print = str(each)
            if serial:
                to_print += ' || Serial - ' + str(course_data[each]['Serial'])
            if terms:
                course_terms = list(course_data[each]['Records'].keys())
                to_print += ' || Terms - ' + str(course_terms)
            data.append(to_print)
        if alphabetically:
            data.sort()
        return data
    def Individual_Record(self,roll,term=None):
        if roll in database:
            if not term:
                return database[roll]
            else:
                return database[roll]['Records'][term]
    def Make_Marklist(self,course=False,course_term=None,branch=None,batch=None,term=latest_term[0],cg=False,sg=False,names=False):
        mark_list = []
        if course and course in course_data:
            if course_term and course_term in course_data[course]['Records']:
                for rolls in course_data[course]['Records'][course_term]:
                    mark_list.append(course_data[course]['Records'][course_term][rolls])
                return mark_list
            else:
                big_list = []
                for course_term in course_data[course]['Records']:
                    mark_list.append(course_term)
                    for rolls in course_data[course]['Records'][course_term]:
                        if names:
                            mark_list.append((course_data[course]['Records'][course_term][rolls],rolls))
                        else:
                            mark_list.append(course_data[course]['Records'][course_term][rolls])
                    big_list.append(mark_list)
                    mark_list = []
                return big_list
        elif cg:
            for roll in database:
                cur_cg = database[roll]['CGPA']
                should_add = True
                if branch:
                    if not database[roll]['Branch'] == branch:
                        should_add = False
                if batch:
                    if not batch == database[roll]['Batch']:
                        should_add = False
                if should_add:
                    if names:
                        name = database[roll]['Name']
                        mark_list.append((cur_cg,name))
                    else:
                        mark_list.append(cur_cg)
            return mark_list
        elif sg:
            for roll in database:
                should_add = True
                if branch:
                    if not database[roll]['Branch'] == branch:
                        should_add = False
                if batch:
                    if not batch == database[roll]['Batch']:
                        should_add = False
                if should_add:
                    for cur_term in database[roll]['Records']:
                        if cur_term == term:
                            cur_sg = database[roll]['Records'][cur_term]['SGPA']
                            if names:
                                name = database[roll]['Name']
                                mark_list.append((cur_sg,name))
                            else:
                                mark_list.append(cur_sg)
                            break
            return mark_list
        return [] # If the input was wrong, we dont want to return None.
    def Mean_Deviation(self,marklist): # Takes marks, outputs mean & std deviation
        if len(marklist) > 0:
            if not isinstance(marklist[0],tuple):
                total = sum(marklist)
                fail = 0
                N = len(marklist)
                for each in marklist:
                    if not each:
                        fail += 1
                N = N - fail
                devn = 0
                if N: # Division by zero error avoidance
                    mean = total/N
                else:
                    mean = total
                for each in marklist:
                    if each:
                        devn += (mean - each)**2
                if N:
                    devn = (devn/N)**0.5
                return mean, devn, fail
            else:
                total = 0
                fail = 0
                for each in marklist:
                    total += each[0]
                    if not each[0]:
                        fail += 1
                N = len(marklist)
                N = N - fail
                devn = 0
                if N: # Division by zero error avoidance
                    mean = total/N
                else:
                    mean = total
                for each in marklist:
                    if each[0]:
                        devn += (mean - each[0])**2
                if N:
                    devn = (devn/N)**0.5
                return mean, devn, fail
    def Gradify(self,marklist,percent=True,cumulative=False):
        categories = [[10,0],[9,0],[8,0],[7,0],[6,0],[5,0],[4,0],['F',0]]
        if cumulative:
            categories = [[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],['F',0]]
        for mark in marklist:
            if isinstance(mark,tuple):
                mark = mark[0]
            if mark == 0:
                categories[7][1] += 1
            for i in range(len(categories)-1):
                if mark >= categories[i][0]:
                    categories[i][1] += 1
                    if not cumulative:
                        break
        if percent:
            total = 0
            for i in range(len(categories)):
                total += categories[i][1]
            for i in range(len(categories)):
                categories[i][1] = categories[i][1]*100/total
        return categories
    def Ranking(self,marklist):
        if marklist:
            if not isinstance(marklist[0],tuple):
                return sorted(marklist,reverse=True)
            else:
                data_dict = {}
                marks_list = []
                for each in marklist:
                    if each[0] in data_dict:
                        data_dict[each[0]].append(each[1])
                    else:
                        data_dict[each[0]] = [each[1]]
                    marks_list.append(each[0])
                marks_list = set(marks_list)
                to_return = []
                for mark in sorted(marks_list,reverse=True):
                    cur_data = sorted(data_dict[mark])
                    to_return.append((len(to_return)+1,cur_data))
                return to_return
    def Course_Performance(self,course,exclude_re=True,percent=True,cumulative=False):
        # Need terms & their graded data.
        poss_grades = [10,9,8,7,6,5,4,'F']
        big_list = self.Make_Marklist(course)
        big_list.sort(key=(lambda k: k[0]))
        graded_list = []
        course_terms = []
        for each in big_list:
            if exclude_re and each[0][-1] == 'M':
                continue
            course_terms.append(each[0].encode('ascii','ignore'))
            graded_list.append(self.Gradify(each[1:],percent,cumulative))
        assert len(course_terms) == len(graded_list)
        to_return = [course_terms,[]]
        for i in range(len(poss_grades)):
            cur = {}
            cur['name'] = str(poss_grades[i])
            cur['data'] = []
            for k in range(len(graded_list)):
                cur['data'].append(graded_list[k][i][1])
            to_return[1].append(cur)
        return to_return
    def Student_Performance(self,roll,egp=True):
        # Need terms, egps, term-wise course grades
        to_return, terms, term_data = [], [], []
        stud_data = database[roll]
        for term in sorted(stud_data['Records'].keys()):
            cur_data = {}
            if egp:
                cur_data['egp'] = stud_data['Records'][term]['EGP']
            else:
                cur_data['sg'] = stud_data['Records'][term]['SGPA']
            cur_data['courses'], cur_data['data'] = [], []
            cur_data['name'] = term.encode('ascii','ignore')
            for course in stud_data['Records'][term]['Courses']:
                cur_data['courses'].append(course.encode('ascii','ignore'))
                cur_data['data'].append(stud_data['Records'][term]['Courses'][course])
            term_data.append(cur_data)
            terms.append(cur_data['name'])
        for i in range(len(term_data)):
            term_data[i]['color'] = i
        to_return.append(terms)
        to_return.append(term_data)
        return to_return


    # End of Analyser...

# <--- End of ResAnalyser

#All the necessary funcs go here...

gather_data() # Initialize!
#All the handlers must be below the funcs...

class MainHandler(webapp2.RequestHandler):
    def get(self):
        path = "index.html"
        template_values={}
        self.response.out.write(template.render(path, template_values))

class CourseHandler(webapp2.RequestHandler):
    def get(self):
        template_values={}
        course = self.request.get('course')
        template_values['course'] = course
        gather_data('Course')
        if course in (None,False,"","all"):
            path = "course_all.html"
            data = sorted(course_data.keys())
            template_values['data'] = data
        else:
            path = "courses.html"
            q = self.request.get('q')
            if q == 'data':
                data = course_data[course]
            else:
                re = self.request.get('exclude_re')
                per = self.request.get('percent')
                exclude_re,percent = True,True
                if str(re) == '0':
                    exclude_re = False
                if str(per) == '0':
                    percent = False
                data = None
                render_data = memcache.get('_course_'+str(course)+str(exclude_re)+str(percent))
                if not render_data:
                    do = Analyser()
                    render_data = do.Course_Performance(course,exclude_re,percent)
                    memcache.set('_course_'+str(course)+str(exclude_re)+str(percent),render_data)
                template_values['terms'] = render_data[0]
                template_values['series'] = render_data[1]
                template_values['exclude_re'] = exclude_re
                template_values['percent'] = percent
            template_values['data'] = data
        self.response.out.write(template.render(path, template_values))

class StudentHandler(webapp2.RequestHandler):
    def render(self,roll):
        template_values={}
        roll = self.request.get('roll')
        roll = roll.upper()
        path = "student.html"
        template_values['present'] = True
        template_values['roll'] = roll
        data = None
        if roll:
            gather_data()
            if roll in database:
                data = database[roll]
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
        template_values['data'] = data
        self.response.out.write(template.render(path, template_values))
    def get(self):
        roll = self.request.get('roll')
        self.render(roll)
    def post(self):
        roll = self.request.get('roll')
        self.render(roll)

class MarklistHandler(webapp2.RequestHandler):
    def get(self):
        path = "marklist.html"
        template_values={}
        self.response.out.write(template.render(path, template_values))
    def post(self):
        template_values={}
        path = "marklist.html"
        gather_data()
        serial = self.request.get('serial')
		#terms = self.request.get('terms')
        get_data = Analyser()
        if serial == 'on': serial = True
        else: serial = False
		#if terms == 'on': terms = True
		#else: terms = False
        data = get_data.Make_Marklist()
        template_values['data'] = data
        self.response.out.write(template.render(path, template_values))

class PrivacyHandler(webapp2.RequestHandler):
    def get(self):
        path = "privacy.html"
        template_values={}
        self.response.out.write(template.render(path, template_values))

class TOSHandler(webapp2.RequestHandler):
    def get(self):
        path = "tos.html"
        template_values={}
        self.response.out.write(template.render(path, template_values))

class AboutHandler(webapp2.RequestHandler):
    def get(self):
        path = "about.html"
        template_values={}
        self.response.out.write(template.render(path, template_values))

class TestHandler(webapp2.RequestHandler):
    def get(self):
        path = "testing.html"
        data = [49.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4]
        template_values={'data':data}
        self.response.out.write(template.render(path, template_values))

class Test2Handler(webapp2.RequestHandler):
    def get(self):
        path = "testing2.html"
        check_for_data()
        data = database
        template_values={'data':data}
        self.response.out.write(template.render(path, template_values))

def handle_404(request, response, exception):
    logging.exception(exception)
    response.write('Oops! Yoou seem to have wandered off! The requested page does not exist.')
    response.set_status(404)

def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('A server error occurred! Report has been logged. Work underway asap.')
    response.set_status(500)


#Alas, the main app (appengine def)...
app = webapp2.WSGIApplication([('/',MainHandler),('/courses',CourseHandler),('/student',StudentHandler),('/marklist',MarklistHandler),('/tos',TOSHandler),('/about',AboutHandler),('/privacy',PrivacyHandler),('/testing',TestHandler),('/testing2',Test2Handler)],
                              debug=True)
app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500