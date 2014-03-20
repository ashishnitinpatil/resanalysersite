#!/usr/bin/env python
from __future__ import print_function

import os, re, sys, time, logging
import json

from ResAnalyser import Analyser

# Begin ResAnalyser --->

latest_terms = ['2013 SPRING','2013 SPRING RE-EXAM']
database = {} # For individual student data storing
course_data = {} # For record keeping of every course for every sem
grades = {'AA':10,'AB':9,'BB':8,'BC':7,'CC':6,'CD':5,'DD':4,'W':'W','FF':'FF','SS':'SS'}
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
rank_data = json.load(open(os.path.join(os.getcwd(),'rank_data.txt'),'r'))
##print(len(department_data["CIVIL ENGINEERING"]["BT11"]))
##print(department_data["CIVIL ENGINEERING"]["BT11"])

#Following code generates course performances (best & worse cgs, Ws, FFs)
def course_perf():
    course_performance = {}
    course_stats = {}

    for course in course_data:
        course_performance[course] = {}
        course_marklist = []
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
    spit.close()

# Following generates performance ranks (average CGs)
def avg_cgs():
    insti_lvl = {}
    batch_lvl = {}
    for each in rank_data:
        if isinstance(rank_data[each],list):
            cur = rank_data[each]
            batch_lvl[each]= sum(cur)/len(cur)
        elif isinstance(rank_data[each],dict):
            for batch in rank_data[each]:
                cur = rank_data[each][batch]
                batch_lvl[' '.join([each, '('+str(batch)+')'])] = sum(cur)/len(cur)
                if batch == "All":
                    insti_lvl[each] = sum(cur)/len(cur)
    print("""
             *****INSTI LEVEL Average CGs*****
             """)
    spit = open(os.path.join(os.getcwd(),"cg_avgs.txt"),'w')
    meta_data = [[],[]]
    for index, branch in enumerate(sorted(insti_lvl,key=lambda x: insti_lvl[x],reverse=True)):
        print('{0:2}. '.format(index+1), "{0:40}".format(branch), insti_lvl[branch])
        meta_data[0].append([index+1, branch, insti_lvl[branch]])
    print("""
             *****BATCH LEVEL Average CGs*****
             """)
    for index, batch in enumerate(sorted(batch_lvl,key=lambda x: batch_lvl[x],reverse=True)):
        print('{0:2}. '.format(index+1), "{0:50}".format(batch), batch_lvl[batch])
        meta_data[1].append([index+1, batch, batch_lvl[batch]])
    json.dump(meta_data,spit)
    spit.close()

# Following code generates rankwise list portable to excel. Edit branch, batch.
def rank_list(bra='MECHANICAL ENGINEERING', bat='BT10'):
    cur_marklist = []
    for roll in database:
        if database[roll]['Branch'] == bra:
            if database[roll]['Batch'] == bat:
                if latest_terms[1] in database[roll]['Records']:
                    cur_term = latest_terms[1]
                else:
                    cur_term = latest_terms[0]
                cur_marklist.append((database[roll]['Records'][cur_term]['CGPA'],database[roll]['Name']))
    j = Analyser()
    ranked = Analyser.Ranking(cur_marklist)
    print(ranked)
    civil = open('rank list {0} {1}.txt'.format(bra, bat),'w')
    big_str = ''
    for each in ranked:
        for every in each[1]:
            big_str += ','.join((str(each[0]),every,str(each[2]))) + '\n'
    civil.write(big_str)
    civil.close()

# Following code is for getting gradified stats (batch-wise, branch-wise, etc)
def grade_stats():
    big_data = {}
    for percent, cumulative in ((False,False),(True,False),(False,True),(True,True)):
        insti_grad = {}
        depart_grad = {}
        batch_grad = {}
        for each in rank_data:
            if isinstance(rank_data[each],list):
                batch_grad[each]= Analyser().Gradify(rank_data[each],percent, cumulative)
            elif isinstance(rank_data[each],dict):
                for batch in rank_data[each]:
                    cur = rank_data[each][batch]
                    try:
                        depart_grad[each][batch] = Analyser().Gradify(rank_data[each][batch],percent, cumulative)
                    except KeyError:
                        depart_grad[each] = {}
                        depart_grad[each][batch] = Analyser().Gradify(rank_data[each][batch],percent, cumulative)
                    if batch == "All":
                        insti_grad[each] = Analyser().Gradify(rank_data[each][batch],percent, cumulative)
        spit = open(os.path.join(os.getcwd(),"cg_distribution.txt"),'w')
        meta_data = {}
        print("\n\nInstitute Level Grading\n")
        for index, branch in enumerate(insti_grad):
            print('{0:2}. '.format(index+1), "{0:40}".format(branch), insti_grad[branch])
            meta_data[branch] = {}
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

# Get the batch toppers for each branch.
def get_toppers():
    for dept in department_data:
        for batch in department_data[dept]:
            print(dept, batch, database[max(department_data[dept][batch],
                                        key=lambda x: department_data[dept][batch][x])]['Name'])

# Get most common names/surnames
def most_common_name():
    from collections import Counter
    import pprint
    all_names = " ".join(database[stud]['Name'] for stud in database).split()
    for i,tup in enumerate(Counter(all_names).most_common(20)):
        print(i+1, ". ", tup[0], ' (', tup[1],')', sep='' )

##course_perf()
##avg_cgs()
##grade_stats()
most_common_name()

