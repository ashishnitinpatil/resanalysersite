# Ranker...
# Licensed under Creative Commons Attribution 3.0 Unported License;
# Please refer to the LICENSE.txt for details.

import os, re, sys, time, logging
import json

latest_terms = ['AUTUMN 2012','RE-EXAM AUTUMN 2012']
grades = {'AA':10,'AB':9,'BB':8,'BC':7,'CC':6,'CD':5,'DD':4,'W':0,'FF':0,'SS':0}
terms = ['SPRING','AUTUMN','RE-EXAM','SUMMER']

department_data = json.load(open(os.path.join(os.getcwd(),'department_data.txt'),'r'))

class Analyser:
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
    # End of Analyser...

rank_data = {}
batches = {}
insti_mark_list = []
for dept in department_data:
    rank_data[dept] = {}
    dept_mark_list = []
    for batch in department_data[dept]:
        if batch not in batches:
            batches[batch] = True
        batch_mark_list = []
        for indi in department_data[dept][batch]:
            batch_mark_list.append(department_data[dept][batch][indi])
        batch_mark_list.sort(reverse=True)
        rank_data[dept][batch] = batch_mark_list
        dept_mark_list.extend(batch_mark_list)
    dept_mark_list.sort(reverse=True)
    rank_data[dept]["All"] = dept_mark_list
    insti_mark_list.extend(dept_mark_list)
insti_mark_list.sort(reverse=True)
rank_data["All"] = insti_mark_list

for batch in batches:
    insti_batch_mark_list = []
    for dept in department_data:
        if batch in department_data[dept]:
            batch_mark_list = []
            for indi in department_data[dept][batch]:
                batch_mark_list.append(department_data[dept][batch][indi])
            insti_batch_mark_list.extend(batch_mark_list)
    insti_batch_mark_list.sort(reverse=True)
    rank_data[batch] = insti_batch_mark_list

g4 = open(os.path.join(os.getcwd(),'rank_data.txt'),'w')
g4.write(json.dumps(rank_data))
g4.close()
print(len(rank_data["BT10"]))
print(rank_data["BT10"].index(9.54))
rakk_file = open(os.path.join(os.getcwd(),'rank_data.txt'),'r')
rakk_data = json.load(rakk_file)
print(len(rakk_data["CIVIL ENGINEERING"]["All"]))
print(rakk_data["All"].index(9.54))
data_file = open(os.path.join(os.getcwd(),'database.txt'),'r')
course_file = open(os.path.join(os.getcwd(),'course_data.txt'),'r')
rank_file = open(os.path.join(os.getcwd(),'rank_data.txt'),'r')
if data_file.closed:
    data_file = open(os.path.join(os.getcwd(),'database.txt'),'r')
if course_file.closed:
    course_file = open(os.path.join(os.getcwd(),'course_data.txt'),'r')
if rank_file.closed:
    rank_file = open(os.path.join(os.getcwd(),'rank_data.txt'),'r')
database = json.load(data_file)
course_data = json.load(course_file)
rank_data = json.load(rank_file)

