#!/usr/bin/env python
# Licensed under Creative Commons Attribution 3.0 Unported License;

import os
import re
import sys
import time
import logging
import json

from ResAnalyser import *

# Begin ResAnalyser --->

database = dict() # For individual student data storing
course_data = dict() # For record keeping of every course for every sem

def gather_data(): # Load stuff from the txt files
    global database, course_data
    with open(os.path.join(os.getcwd(),'database.txt'),'r') as data_file:
        database = json.load(data_file)
    with open(os.path.join(os.getcwd(),'course_data.txt'),'r') as course_file:
        course_data = json.load(course_file)

##dt = open(os.path.join(os.getcwd(),'database.txt'),'r')
##database = json.load(dt)
##course_data = json.load(open(os.path.join(os.getcwd(),'course_data.txt'),'r'))
##input("AS")
gather_data()
with open(os.path.join(os.getcwd(),'department_data.txt'),'r') as department_file:
    department_data = json.load(department_file)
with open(os.path.join(os.getcwd(),'rank_data.txt'),'r') as rank_file:
    rank_data = json.load(rank_file)
##print(len(department_data["CIVIL ENGINEERING"]["BT11"]))
##print(department_data["CIVIL ENGINEERING"]["BT11"])

##Following code generates course performances (best & worse cgs, Ws, FFs)
"""course_performance = dict()
course_stats = dict()

for course in course_data:
    course_performance[course] = dict()
    course_marklist = list()
    for term in course_data[course]['Records']:
        term_marklist = list(course_data[course]['Records'][term].values())
        course_performance[course][term] = Analyser().Mean_Deviation(term_marklist)
        course_marklist.extend(term_marklist)
    course_performance[course]['All'] = Analyser().Mean_Deviation(course_marklist)
min_studs = 50
print("Best performing courses (according to mean of grades)")
course_stats['Best CGs'] = [(c,course_data[c]['Name'],course_performance[c]['All'][0])
                        for c in sorted(course_performance,key=lambda x: course_performance[x]['All'][0], reverse=True) if course_data[c]['Students'] >= min_studs][:20] # Mean-wise
course_stats['Worst CGs'] = [(c,course_data[c]['Name'],course_performance[c]['All'][0])
                        for c in sorted(course_performance,key=lambda x: course_performance[x]['All'][0]) if course_data[c]['Students'] >= min_studs][:20] # Mean-wise
course_stats['Most Ws'] = [(c,course_data[c]['Name'],course_data[c]['W'])
                        for c in sorted(course_data,key=lambda x: course_data[x]['W'], reverse=True) if course_data[c]['Students'] >= min_studs][:20] # Most Ws
course_stats['Most FFs'] = [(c,course_data[c]['Name'],course_data[c]['FF'])
                        for c in sorted(course_data,key=lambda x: course_data[x]['FF'], reverse=True) if course_data[c]['Students'] >= min_studs][:20] # Most FFs

course_stats['Most W %'] = [(c,course_data[c]['Name'],course_data[c]['W']*100/course_data[c]['Students'])
                        for c in sorted(course_data,key=lambda x: course_data[x]['W']*100/course_data[x]['Students'], reverse=True) if course_data[c]['Students'] >= min_studs][:20] # Most Ws percent
course_stats['Most FF %'] = [(c,course_data[c]['Name'],course_data[c]['FF']*100/course_data[c]['Students'])
                        for c in sorted(course_data,key=lambda x: course_data[x]['FF']*100/course_data[x]['Students'], reverse=True) if course_data[c]['Students'] >= min_studs][:20] # Most FFs percent
for each in course_stats:
    print(each)
    print(course_stats[each])
spit = open(os.path.join(os.getcwd(),"course_stats.txt"),'w')
json.dump(course_stats,spit)
spit.close()"""

### Following generates performance ranks (average CGs)
##insti_lvl = dict()
##batch_lvl = dict()
##for each in rank_data:
##    if isinstance(rank_data[each],list):
##        cur = rank_data[each]
##        batch_lvl[each]= sum(cur)/len(cur)
##    elif isinstance(rank_data[each],dict):
##        for batch in rank_data[each]:
##            cur = rank_data[each][batch]
##            batch_lvl[' '.join([each, '('+str(batch)+')'])] = sum(cur)/len(cur)
##            if batch == "All":
##                insti_lvl[each] = sum(cur)/len(cur)
##print("""
##         *****INSTI LEVEL Average CGs*****
##         """)
##spit = open(os.path.join(os.getcwd(),"cg_avgs.txt"),'w')
##meta_data = [list(),list()]
##for index, branch in enumerate(sorted(insti_lvl,key=lambda x: insti_lvl[x],reverse=True)):
##    print('{0:2}. '.format(index+1), "{0:40}".format(branch), insti_lvl[branch])
##    meta_data[0].append([index+1, branch, insti_lvl[branch]])
##print("""
##         *****BATCH LEVEL Average CGs*****
##         """)
##for index, batch in enumerate(sorted(batch_lvl,key=lambda x: batch_lvl[x],reverse=True)):
##    print('{0:2}. '.format(index+1), "{0:50}".format(batch), batch_lvl[batch])
##    meta_data[1].append([index+1, batch, batch_lvl[batch]])
##json.dump(meta_data,spit)
##spit.close()

## Following code generates rankwise list portable to excel. Edit branch, batch.
"""cur_marklist = list()
for roll in database:
    if database[roll]['Branch'] == 'MECHANICAL ENGINEERING':
        if database[roll]['Batch'] == 'BT10':
            if latest_terms[1] in database[roll]['Records']:
                cur_term = latest_terms[1]
            else:
                cur_term = latest_terms[0]
            cur_marklist.append((database[roll]['Records'][cur_term]['CGPA'],database[roll]['Name']))
j = Analyser()
ranked = Analyser.Ranking(cur_marklist)
print(ranked)
civil = open('mech.txt','w')
big_str = ''
for each in ranked:
    for every in each[1]:
        big_str += ','.join((str(each[0]),every,str(each[2]))) + '\n'
civil.write(big_str)
civil.close()"""

## Following code is for getting gradified stats (batch-wise, branch-wise, etc)
"""
big_data = dict()
for percent, cumulative in ((False,False),(True,False),(False,True),(True,True)):
    insti_grad = dict()
    depart_grad = dict()
    batch_grad = dict()
    for each in rank_data:
        if isinstance(rank_data[each],list):
            batch_grad[each]= Analyser().Gradify(rank_data[each],percent, cumulative)
        elif isinstance(rank_data[each],dict):
            for batch in rank_data[each]:
                cur = rank_data[each][batch]
                try:
                    depart_grad[each][batch] = Analyser().Gradify(rank_data[each][batch],percent, cumulative)
                except KeyError:
                    depart_grad[each] = dict()
                    depart_grad[each][batch] = Analyser().Gradify(rank_data[each][batch],percent, cumulative)
                if batch == "All":
                    insti_grad[each] = Analyser().Gradify(rank_data[each][batch],percent, cumulative)
    spit = open(os.path.join(os.getcwd(),"cg_distribution.txt"),'w')
    meta_data = dict()
    print("\n\nInstitute Level Grading\n")
    for index, branch in enumerate(insti_grad):
        print('{0:2}. '.format(index+1), "{0:40}".format(branch), insti_grad[branch])
        meta_data[branch] = dict()
        meta_data[branch]['All'] = insti_grad[branch]
    print("\n\nBatch-wise Grading\n")
    for index, batch in enumerate(batch_grad):
        print('{0:2}. '.format(index+1), "{0:40}".format(batch), batch_grad[batch])
        meta_data[batch] = batch_grad[batch]
    print("\n\nDepartment Level Grading\n")
    for index, batch in enumerate(depart_grad):
        print(batch)
        for batches in depart_grad[batch]:
            print('{0:2}. '.format(index+1), "{0:40}".format(batches), depart_grad[batch][batches])
            meta_data[batch][batches] = depart_grad[batch][batches]
    if not cumulative:
        meta_data['All'] = [[10, 0], [9, 0], [8, 0], [7, 0], [6, 0], [5, 0], [4, 0]]#, ['F', 0]]
    else:
        meta_data['All'] = [[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0]]#,['F',0]]
    if not percent:
        for branch in insti_grad:
            for i in range(len(meta_data['All'])):
                meta_data['All'][i][1] += insti_grad[branch][i][1]
    big_data[str(percent)+str(cumulative)] = meta_data
# Manual override for All in percent (it adds all! shit!)
for cumulative in (True,False):
    total = sum([mark[1] for mark in big_data['FalseFalse']['All']])
    for i in range(len(big_data['True'+str(cumulative)]['All'])):
        big_data['True'+str(cumulative)]['All'][i][1] = big_data['False'+str(cumulative)]['All'][i][1]*100/total
    print(big_data['False'+str(cumulative)]['All'],big_data['True'+str(cumulative)]['All'])
json.dump(big_data,spit)
spit.close()
#print(Analyser().Gradify([4,5,6,7,8,9],True,True))"""