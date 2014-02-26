# Licensed under Creative Commons Attribution 3.0 Unported License;
# Please refer to the LICENSE.txt for details.

import os, re, sys, time, logging
import json

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

from ResAnalyser import Analyser

##Following code generates course performances (best & worse)
"""course_performance = {}

for course in course_data:
    course_performance[course] = {}
    course_marklist = []
    for term in course_data[course]['Records']:
        term_marklist = course_data[course]['Records'][term].values()
        course_performance[course][term] = Analyser.Mean_Deviation(term_marklist)
    course_marklist.extend(term_marklist)
    course_performance[course]['All'] = Analyser.Mean_Deviation(course_marklist)

print("Best performing courses (according to mean of grades)")
best = sorted(course_performance,key=lambda x: course_performance[x]['All'][0], reverse=True) # Mean-wise
i,count = 1, 0
while i <= 20:
    cur_mean,cur_devn,cur_fail,cur_w,cur_no = course_performance[best[count]]['All']
    if cur_no >= 20:
        print(i+1,best[count],course_data[best[count]]['Name'],"Mean -",cur_mean,"| Deviation -",cur_devn,
        "|Fail -",cur_fail,"| W -",cur_w,"| No of Students -",cur_no)
        i += 1
    count += 1
print()
print()

print("Worst performing courses (according to mean of grades)")
i,count = -1,-1
while i >= -20:
    cur_mean,cur_devn,cur_fail,cur_w,cur_no = course_performance[best[count]]['All']
    if cur_no >= 20:
        print(-i,best[count],course_data[best[count]]['Name'],"Mean -",cur_mean,"| Deviation -",cur_devn,
        "|Fail -",cur_fail,"| W -",cur_w,"| No of Students -",cur_no)
        i -= 1
    count -= 1
print()"""

##insti_lvl = {}
##batch_lvl = {}
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
##meta_data = [[],[]]
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

## Following code generates rankwise list portable to excel. Edit branch, batch.
"""cur_marklist = []
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

##
##insti_grad = {}
##depart_grad = {}
##batch_grad = {}
##for each in rank_data:
##    if isinstance(rank_data[each],list):
##        batch_grad[each]= Analyser().Gradify(rank_data[each])
##    elif isinstance(rank_data[each],dict):
##        for batch in rank_data[each]:
##            cur = rank_data[each][batch]
##            try:
##                depart_grad[each][batch] = Analyser().Gradify(rank_data[each][batch])
##            except KeyError:
##                depart_grad[each] = {}
##                depart_grad[each][batch] = Analyser().Gradify(rank_data[each][batch])
##            if batch == "All":
##                insti_grad[each] = Analyser().Gradify(rank_data[each][batch])
##spit = open(os.path.join(os.getcwd(),"cg_distribution.txt"),'w')
##meta_data = [[],[]]
##print("\n\nInstitute Level Grading\n")
##for index, branch in enumerate(insti_grad):
##    print('{0:2}. '.format(index+1), "{0:40}".format(branch), insti_grad[branch])
##    meta_data[0].append([index+1, branch, insti_grad[branch]])
##print("\n\nBatch-wise Grading\n")
##for index, batch in enumerate(batch_grad):
##    print('{0:2}. '.format(index+1), "{0:40}".format(batch), batch_grad[batch])
##    meta_data[1].append([index+1, batch, batch_grad[batch]])
##print("\n\nDepartment Level Grading\n")
##for index, batch in enumerate(depart_grad):
##    print(batch)
##    for batches in depart_grad[batch]:
##        print('{0:2}. '.format(index+1), "{0:40}".format(batches), depart_grad[batch][batches])
##        meta_data[1].append([index+1, batch + batches, depart_grad[batch][batches]])
##json.dump(meta_data,spit)
#fgh = json.load(open(os.path.join(os.getcwd(),'cg_distribution.txt'),'r'))
#print(fgh['TrueFalse']['All'])

# Get the batch toppers for each branch.
##for dept in department_data:
##    for batch in department_data[dept]:
##        print dept, batch, database[max(department_data[dept][batch],
##                                    key=lambda x: department_data[dept][batch][x])]['Name']