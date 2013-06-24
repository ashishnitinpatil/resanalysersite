# Copyright 2013 @!mmorta!
#
# Licensed under Creative Commons Attribution-ShareAlike 3.0 Unported License;
# Please refer to the LICENSE.txt for details.

import os, re, sys, time, logging
import json

# Begin ResAnalyser --->

cruse = {}
latest_terms = ['2013 SPRING','2013 SPRING RE-EXAM']
database = {} # For individual student data storing
course_data = {} # For record keeping of every course for every sem
grades = {'AA':10,'AB':9,'BB':8,'BC':7,'CC':6,'CD':5,'DD':4,'W':0,'FF':0,'SS':0}
terms = ['SPRING','AUTUMN','RE-EXAM','SUMMER']

def gather_data(): # Load stuff from the txt files
	global database, course_data
	database = json.load(open(os.path.join(os.getcwd(),'database.txt'),'r'))
	course_data = json.load(open(os.path.join(os.getcwd(),'course_data.txt'),'r'))

##dt = open(os.path.join(os.getcwd(),'database.txt'),'r')
##database = json.load(dt)
##course_data = json.load(open(os.path.join(os.getcwd(),'course_data.txt'),'r'))
##input("AS")
gather_data()
department_data = json.load(open(os.path.join(os.getcwd(),'department_data.txt'),'r'))
print(len(department_data["CIVIL ENGINEERING"]["BT11"]))
print(department_data["CIVIL ENGINEERING"]["BT11"])
# Analysis shit! :-P  -->
class Analyser:
    def All_Courses(serial=True, terms=True, alphabetically = True):
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
    def Individual_Record(roll,term=None):
        if roll in database:
            if not term:
                return database[roll]
            else:
                return database[roll]['Records'][term]
    def Make_Marklist(self,course=False,course_term=None,multi=False,branch=None,batch=None,term=latest_terms[0],cg=False,sg=False,names=False):
        mark_list = []
        if course and course in course_data:
            if course_term and course_term in course_data[course]['Records']:
                for rolls in course_data[course]['Records'][course_term]:
                    mark_list.append(course_data[course]['Records'][course_term][rolls])
                return mark_list
            else:
                if multi: big_list = []
                for course_term in course_data[course]['Records']:
                    for rolls in course_data[course]['Records'][course_term]:
                        if names:
                            mark_list.append((course_data[course]['Records'][course_term][rolls],rolls))
                        else:
                            mark_list.append(course_data[course]['Records'][course_term][rolls])
                    if multi: big_list.append(mark_list)
                if multi: return big_list
                return mark_list
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
    def Mean_Deviation(marklist): # Takes marks, outputs mean & std deviation
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
    def Gradify(self,marklist,cumulative=False):
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
        return categories
    def Ranking(marklist):
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
    def Course_Performance(self,course):
        course_terms = sorted(course_data[course]['Records'].keys())
        to_return = [course_terms]
        poss_grades = [10,9,8,7,6,5,4,'F']
        big_list = self.Make_Marklist(course,multi=True)
        graded_list = []
        for each in big_list:
            graded_list.append(self.Gradify(each))
        logging.info(course_terms)
        logging.info(graded_list)
        assert len(course_terms) == len(graded_list)
        for i in range(len(poss_grades)):
            cur = {}
            cur['name'] = str(poss_grades[i])
            cur['data'] = []
            for k in range(len(big_list)):
                cur['data'].append(big_list[k][i])
            graded_list.append(cur)
        to_return.append(graded_list)
        return to_return

    # End of Analyser...

print(Analyser().Make_Marklist('ADV. DESIGN OF STEEL STRUCTURES',multi=True))