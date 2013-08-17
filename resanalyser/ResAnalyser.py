#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Name:        Result Analyser (Version 2.0)
#
# Author:      Asis aka !mmorta!
#
# Created:     11/05/2013 (V1.0 - 29/11/2012)
#
# Copyright:   (c) Asis 2013
#
# Licence:     Creative Commons Attribution-ShareAlike 3.0 Unported License.
#-------------------------------------------------------------------------------


# Imports from Python
import os, re, sys, json

# ATTENTION!!! UPDATE THIS EVERY TERM!!!
latest_terms = ['2013 SPRING','2013 SPRING RE-EXAM']

# Global Databases & required variables -->

result_file_addresses = []
# Following automatically takes in files from the 'Result' directory & adds them for analysis
for res_file in os.listdir(os.path.join(os.getcwd(),'Result')):
    result_file_addresses.append(os.path.join(os.getcwd(),'Result',res_file))
#result_file_addresses = ["G:\Study\Programming\Py\Result analysis\testing3.txt"]
database = {} # For individual student data storing
course_data = {} # For record keeping of every course for every sem
department_data = {} # For record keeping of students in each department & cur_cg
grades = {'AA':10,'AB':9,'BB':8,'BC':7,'CC':6,'CD':5,'DD':4,'W':0,'FF':0,'SS':10}
terms = ['SPRING','AUTUMN','RE-EXAM','SUMMER','WINTER']

# The Main function --> (to give all the pretty Command Line Interface like feel)
def main():
    ''' Firstly, we take in the result files/addresses, check if they are good. Then parse & later analyse them'''
    global result_file, result_file_addresses
    # Welcome Screen
    print(" \n\tResult Analyser by !mmorta!\
            \n\tPython Library for analysing result (PDF Parser with Analyser)")
    # Take in the address of the result file
    if not result_file_addresses:
        result_file_addresses = [input("\n\tAddress of the result file (e.g. C:\downloads\civ.pdf)")]
    # Check if the address is proper/correct
    for result_file_addr in result_file_addresses:
        try:
            result_file = open(result_file_addr,'r')
        except IOError:
            print("\n\tUnable to open the file!\n")
            result_file = None
            print("Exiting...")
            sys.exit(1) # Bad exit

        # File address is correct
        print("\n\tAddress %s seems correct..."%result_file_addr)

        print("\tProcessing result file %s..."%os.path.basename(result_file_addr))

        # Everything seems fine so just parse the file & extract the reqd data...
        PDF_Parser(result_file)
        result_file.close()
    # Write the data to files so we dont have to redo so much so often (if at all)
    g1 = open(os.path.join(os.getcwd(),'database.txt'),'w')
    g2 = open(os.path.join(os.getcwd(),'course_data.txt'),'w')
    g3 = open(os.path.join(os.getcwd(),'department_data.txt'),'w')
    g1.write(json.dumps(database))
    g2.write(json.dumps(course_data))
    g3.write(json.dumps(department_data))
    g1.close()
    g2.close()
    g3.close()
    # End of main()...

# Parsing stuff! -->
# A thorough overview of the raw PDF result file is necessary
# to understand the PDF_Parser function properly.

# Nasty name issues...
''' The PDF is doomed. Oops that is VNIT I suppose. Anyways, the PDF data is very very crude
and to make it look good & be so, I prettify things that are nasty. You can see below what it
does, these dicts are there to replace stuff so that our database is intact & nice & free from
repetitions & other name issues.'''
general_names_issues = {'SPORTS / YOGA / LIBRARY / NCC (--)':'SPORTS YOGA LIBRARY NCC',
                        'SPORTS/YOGA/LIBRARY/NCC (--)':'SPORTS YOGA LIBRARY NCC',
                        'SPORTS / YOGA/ LIBRARY/ NCC (AU)':'SPORTS YOGA LIBRARY NCC',
                        'SPORTS / YOGA / LIBRARY / NCC (AU)':'SPORTS YOGA LIBRARY NCC',
                        '& REUSE   \(DE\)':'INDUSTRIAL WASTEWATER TREATMENT, RECYCLE & REUSE',
                        'ENGINEERING   \(DE\)':'RAILWAY, AIRPORT, PORTS & HARBOR ENGINEERING',
                        'ENGINEERING   \(DC\)':'INTRODUCTION TO MATERIALS SCIENCE AND ENGINEERING'}

duplication_issues = {'BUILDING DESIGN AND DRAWING':'BUILDING DESIGN DRAWING',
                      'COMMUNICATION SKILL':'COMMUNICATION SKILLS',
                      'ENVIRONMENTAL ENGINEERING-II':'ENVIRONMENTAL ENGINEERING II',
                      'MATHEMATICS - I':'MATHEMATICS I',
                      'MINI PROJECT - I':'MINI PROJECT',
                      'PAVEMENT DESIGN':'PAVEMENT ANALYSIS DESIGN',
                      'PHYSICS - I':'PHYSICS I','PHYSICS':'PHYSICS I',
                      'PROJECT PLANNING MANAGEMENT':'PROJECT PLANNING AND MANAGEMENT',
                      'PSYCHOLOGY AND HRM':'PSYCHOLOGY HRM',
                      'SPORTS YOGA/ LIBRARY/ NCC':'SPORTS','SPORTS YOGA LIBRARY NCC':'SPORTS',
                      'SPORTS/YOGA/LIBRARY/NCC':'SPORTS',
                      'STRUCTURAL ANALYSIS LABORATORY':'STRUCTURAL ANALYSIS LAB',
                      'SURVEYING - I':'SURVEYING I',
					  'RELIABLITY AND MAINTENANCE ENGINEERING':'RELIABILITY AND MAINTENANCE ENGINEERING',
					  'PROJECT PHASE-I':'PROJECT PHASE I','PROJECT PHASE - I':'PROJECT PHASE I',
					  'PROJECT PHASE-II':'PROJECT PHASE II','PROJECT PHASE - II':'PROJECT PHASE II',
                      'ADV. I. C. ENGINE':'ADVANCED IC ENGINE',
                      'APPLICATION':'APPLICATIONS',
                      'CHARACTERISATION OF MATERIAL':'CHARACTERISATION OF MATERIALS',
                      'CHEMICAL REACTION ENGINEERING-I':'CHEMICAL REACTION ENGINEERING',
                      'COMPUTER ORGANISATION':'COMPUTER ORGANIZATION',
                      'CONCEPTS IN PROGARMMING LANGUAGES':'CONCEPTS IN PROGRAMMING LANGUAGES',
                      'CONTROL SYSTEM - I':'CONTROL SYSTEM I','CONTROL SYSTEM':'CONTROL SYSTEM I','CONTROL SYSTEM':'CONTROL SYSTEM I',
                      'CONTROL SYSTEM - I LAB':'CONTROL SYSTEM I LAB','CONTROL SYSTEMS - I LAB':'CONTROL SYSTEM I LAB',
                      'CONTROL SYSTEM - II':'CONTROL SYSTEM II','CONTROL SYSTEM - II LAB':'CONTROL SYSTEM II LAB',
                      'DATA MINING DATA WEARHOUSING':'DATA MINING AND DATA WEARHOUSING',
                      'DATA STRUCTURES PROGRAM DESIGN':'DATA STRUCTURES AND PROGRAM DESIGN - I','DATA STRUCTURES AND PROGRAM DESIGN':'DATA STRUCTURES AND PROGRAM DESIGN - I',
                      'DATA STRUCTURES PROGRAM DESIGN II':'DATA STRUCTURES AND PROGRAM DESIGN - II','DATA STRUCTURES AND PROGAME DESIGN - II':'DATA STRUCTURES AND PROGRAM DESIGN - II',
                      'DIGITAL CIRCUITS LOGIC DESIGN':'DIGITAL CIRCUITS AND LOGIC DESIGN',
                      'DISCRETE MATHS GRAPH THEORY':'DISCRETE MATHS AND GRAPH THEORY',
                      'ELECTRICAL MACHINE-I':'ELECTRICAL MACHINE I','ELECTRICAL MACHINES-I':'ELECTRICAL MACHINE I',
                      'ELECTRICAL MACHINE-II':'ELECTRICAL MACHINE II','ELECTRICAL MACHINES I LAB':'ELECTRICAL MACHINE I LAB',
                      'ELECTRICAL POWER SYSTEM-I':'ELECTRICAL POWER SYSTEM I','ELECTRICAL POWER SYSTEM - II':'ELECTRICAL POWER SYSTEM II',
                      'ELECTRONIC PRODUCT ENGG W/S':'ELECTRONIC PRODUCT ENGG. WORKSHOP',
                      'ELECTRONICS DEVICE AND CIRCUITS':'ELECTRONICS DEVICES AND CIRCUITS','ELECTRONICS DEVICE AND CIRCUITS LAB':'ELECTRONICS DEVICES AND CIRCUITS LAB',
                      'ELECTRONIC DEVICES CIRCUITS':'ELECTRONIC DEVICES AND CIRCUITS','ELECTRONICS DEVICE CIRCUITS LAB':'ELECTRONICS DEVICES AND CIRCUITS LAB',
                      'ELECTRONICS DEVICE CIRCUITS LAB':'ELECTRONICS DEVICES AND CIRCUITS LAB','ENERGY CONVERSION - I':'ENERGY CONVERSION I',
                      'ENERGY CONVERSION- II':'ENERGY CONVERSION II','ENERGY CONVERSION- II LAB':'ENERGY CONVERSION II LAB',
                      'ENGINEERING METALLUGY LAB':'ENGINEERING METALLURGY LAB',
                      'ENVIRONMENTAL ENGINEERING-I':'ENVIRONMENTAL ENGINEERING I','ENVIRONMENTAL ENGINEERING':'ENVIRONMENTAL ENGINEERING I',
                      'GEOLOGY - I':'GEOLOGY I','GEOLOGY - II':'GEOLOGY II',
                      'GRAPHICS BASIC DESIGN':'GRAPHICS AND BASIC DESIGN',
                      'HEAT TRANSFER':'HEAT TRANSFER I','HEAT TRANSFER-II':'HEAT TRANSFER II',
                      'INTRODUCTION TO MINE TECHNOLOGY':'INTRODUCTION TO MINING TECHNOLOGY',
                      'LINEAR ELECTRONIC CIRCUIT':'LINEAR ELECTRONIC CIRCUITS','LINEAR ELECTRONIC CIRCUIT LAB':'LINEAR ELECTRONIC CIRCUITS LAB',
                      'MACHINE DESIGN - I':'MACHINE DESIGN I','MACHINE DESIGN - II':'MACHINE DESIGN II','MACHINE DESIGN -II':'MACHINE DESIGN II',
                      'MANUFACTURING PROCESS - II':'MANUFACTURING PROCESS II',
                      'MANUFACTURING PROCESS AUTOMATION':'MANUFACTURING PROCESSES AUTOMATION',
                      'MASS TRANSFER':'MASS TRANSFER I','MASS TRANSFER - I':'MASS TRANSFER I','MASS TRANSFER - II':'MASS TRANSFER II',
                      'MATHEMATICS - II':'MATHEMATICS II',
                      'MEASUREMENT INSTRUMENTATION':'MEASUREMENT AND INSTRUMENTATION','MEASUREMENT INSTRUMENTATION LAB':'MEASUREMENT AND INSTRUMENTATION LAB',
                      'MECHANICAL OPERATION':'MECHANICAL OPERATIONS',
                      'MICROPROCESSORS-BASED SYSTEMS':'MICROPROCESSORS BASED SYSTEMS','MICROPROCESSOR BASED SYSTEMS':'MICROPROCESSORS BASED SYSTEMS',
                      'MINE SURVEYING - II':'MINE SURVEYING II','MINE VENTILATION CLIMATE ENGINEERING':'MINE VENTILATION AND CLIMATE ENGINEERING',
                      'MINING MACHINERY- II':'MINING MACHINERY II',
                      'NEUROFUZZY TECHNIQUES':'NEURO FUZZY TECHNIQUES',
                      'NON DISTRUCTIVE TESTING':'NON DESTRUCTIVE TESTING',
                      'OPERATING SYSTEM':'OPERATING SYSTEMS','OPERATION RESEARCH':'OPERATIONS RESEARCH',
                      'OVERVIEW OF COMM. SYSTEMS':'OVERVIEW OF COMMUNICATION SYSTEMS',
                      'PETROLEUM REFINERY ENGINEERING':'PETROLIUM REFINERY ENGINEERING',
                      'PHYSICS - III':'PHYSICS III','PHYSICS':'PHYSICS I',
                      'PSYCHOLOGY ED':'PSYCHOLOGY AND ED','PSYCHOLOGY E.D.':'PSYCHOLOGY AND ED',
                      'RADIO FREQUENCY CIRCUIT DESIGN LAB.':'RADIO FREQUENCY CIRCUIT DESIGN LAB',
                      'REFRIGERATION CRYOGENICS':'REFRIGERATION AND CRYOGENICS',
                      'REMOTE SENSING GIS':'REMOTE SENSING AND GIS',
                      'SAFETY AND RISK ANALYSIS':'SAFETY RISK ANALYSIS',
                      'SECONDARY SPECIAL STEEL MAKING':'SECONDARY AND SPECIAL STEEL MAKING',
                      'SIGNALS SYSTEMS':'SIGNALS AND SYSTEMS',
                      'SOFTWARE LAB - I':'SOFTWARE LAB I','SOFTWARE LAB - II':'SOFTWARE LAB II',
                      'STRUCTURAL DESIGN - II':'STRUCTURAL DESIGN II',
                      'SWITCHGEAR AND PROTECTION STUDY\)':'SWITCHGEAR AND PROTECTION',
                      'THEORY OF MACHINE - I':'THEORY OF MACHINE I','THEORY OF MACHINES - I':'THEORY OF MACHINE I',
                      'TRANSPORT PHENOMENON':'TRANSPORT PHENOMENA',
                      'SURVERYING':'SURVEYING',
                      'ADVANCE BUILDING MATERIALS':'ADVANCED BUILDING MATERIALS',
                      'CONTEMPORARY DESIGN THEORY CRITISISM':'CONTEMPORARY DESIGN THEORY CRITICISM'}

def PDF_Parser(file):

    global database, course_data, department_data

    def is_no_of_credit(char):
        try:
            no_credits = int(char)
            if no_credits == 0:
                return 10 # For type_resolving purposes
            if no_credits < 9:
                return no_credits
        except:
            return False

    def is_gpa(gpa):
        try:
            gpa = float(gpa)
            if gpa <= 10.0:
                return gpa
        except:
            return 0

    def getdata(line):
        start = line.find("Td (") + 4
        end = line[start:].find(")Tj ET")+start
        result = line[start:end]
        return result

    def prettify(course): # Course names have nasty raw data & duplication issues
        if course in general_names_issues:
            return general_names_issues[course]
        if course in duplication_issues:
            return duplication_issues[course]
        else:
            course_split = course.split()
            if not len(course_split) == 1:
                legit = ''
                for each in course_split:
                    if re.match(r'[a-zA-Z0-9.-]+',each):
                        legit += each + ' '
                legit = legit[:-1]
                if legit in duplication_issues:
                    legit = duplication_issues[legit]
                general_names_issues[course] = legit
                return legit
            else:
                general_names_issues[course] = course
                return course

    def prettify_name(name):
        prettified = name
        if prettified[-1] == '\xa0':
            prettified = prettified[:-1]
        if prettified[-1] in ('Â',chr(194)):
            prettified = prettified[:-1]
        return prettified

    def get_stud_type(roll):
        # Classifying the student based on his Roll type...
        if roll[:2] == 'BT':
            cur_stud_type = 'B. Tech.'
        elif roll[:2] in ('BA','AR'):
            cur_stud_type = 'B. Arch.'
        elif roll[:2] == 'MT':
            cur_stud_type = 'M. Tech.'
        elif roll[0] in ['L','N','R','S','T','U','V','W','X','Y','Z']:
            cur_stud_type = 'First Year B. Tech.'
        elif roll[:4] == 'VNIT':
            cur_stud_type = 'Super Senior'
        else:
            cur_stud_type = 'Dont Know'
        if cur_stud_type == 'B. Tech.':
            if int(roll[2:4]) <= 8:
                cur_stud_type = 'Super Senior'
        return cur_stud_type

    def get_batch(roll,stud_type):
        if stud_type == 'First Year B. Tech.' or roll[:2] == 'AR':
            if latest_terms[0][0] == "S":
                batch = str(int(latest_terms[0][-4:])-1)
            else:
                batch = latest_terms[0][:4]
        else:
            batch = roll[:4]
        return batch

    def individual():
        all_details = {'Branch':None,'CGPA':0,'Credits_Total':0,'EGP_Total':0,'W':0,'FF':0}
        cur_line = file.readline()
        cur_name = getdata(file.readline())
        if cur_name == "GRADE CARD":
            return
        cur_roll = getdata(file.readline())
        cur_stud_type = get_stud_type(cur_roll)
        # Trashing out unrequired data...
        for i in range(5):
            file.readline()
        cur_branch = getdata(file.readline()).replace('&','AND')
        cur_name = prettify_name(cur_name)
        cur_batch = get_batch(cur_roll,cur_stud_type)
        all_details['Name'] = cur_name
        all_details['Roll'] = cur_roll
        all_details['Stud Type'] = cur_stud_type
        all_details['Branch'] = cur_branch
        all_details['Batch'] = cur_batch
        all_details['Records'] = {}
        if cur_roll in database:
            all_details = database[cur_roll]
        good_to_go = True
        #if cur_stud_type in ('Super Senior','Dont Know'):
        #    good_to_go = False
        while good_to_go:
            cur_data = getdata(cur_line)
            if cur_data:
                if cur_data.split()[0] in terms:
                    cur_term = cur_data
                    if cur_term[-1] == ' ':
                        cur_term = cur_term[:-1]
                    cur_term = cur_term.split()
                    if 'AUTUMN'in cur_term:
                        cur_term[cur_term.index('AUTUMN')] = 'WINTER'
                    cur_term.reverse()
                    cur_term = ' '.join(cur_term)
                    all_details['Records'][cur_term] = {'CGPA':0,'SGPA':0,'Courses':{}}
                    cur_block = []
                    while not cur_data == "Credit":
                        cur_line = file.readline()
                        cur_data = getdata(cur_line)
                        cur_block.append(cur_data)
                        if cur_data in grades and is_no_of_credit(cur_block[-2]):
                            cur_grade = grades[cur_data]
                            cur_grade_raw = cur_data
                            cur_line = file.readline()
                            cur_data = getdata(cur_line)
                            cur_block.append(cur_data)
                            course = cur_block[-4]
                            if cur_block[-3][:2] == '\(':
                                del cur_block[-3]
                            no_credits = is_no_of_credit(cur_block[-3])
                            if no_credits == 10:
                                no_credits = 0
                            serial = cur_block[-1]
                            if course[0] == '\\':
                                course = cur_block[-5]
                                if cur_block[-4][:2] == '\(':
                                    del cur_block[-4]
                                    course_credits = cur_block[-3]
                                    serial = cur_block[-1]
                                else:
                                    course_credits = cur_block[-4]
                                    serial = cur_block[-2]
                            course_raw = course
                            course_name = prettify(course)
                            course = serial
                            cur_block = []
                            good_to_add = True
                            # Fuck Super Senior Data
                            if int(cur_term[:4]) <= 2009:
                                good_to_add = False
                            elif int(cur_term[:4]) == 2009 and not cur_term in ('2009 AUTUMN RE-EXAM','2009 AUTUMN'):
                                good_to_add = False
                            if good_to_add:
                                # First adding the data to course_database
                                if serial in course_data:
                                    if not cur_branch in course_data[course]['Branches']:
                                        course_data[course]['Branches'].append(cur_branch)
                                    if cur_term in course_data[course]['Records']:
                                        course_data[course]['Records'][cur_term][cur_roll] = cur_grade
                                    else:
                                        course_data[course]['Records'][cur_term] = {}
                                        course_data[course]['Records'][cur_term][cur_roll] = cur_grade
                                    course_data[course]['Students'] += 1
                                else:
                                    course_data[course] = {'Name':course_name,'Records':{},'Branches':[cur_branch],'Credits':no_credits, 'W':0, 'FF':0, 'Students':1}
                                    course_data[course]['Records'][cur_term] = {}
                                    course_data[course]['Records'][cur_term][cur_roll] = cur_grade

                                # Now adding stuff to the student's database
                                if cur_grade_raw == 'W':
                                    all_details['W'] += 1
                                    course_data[course]['W'] += 1
                                elif cur_grade_raw == 'FF':
                                    all_details['FF'] += 1
                                    course_data[course]['FF'] += 1
                                all_details['Records'][cur_term]['Courses'][serial] = cur_grade

                    if is_gpa(cur_block[-2]) and not len(cur_block) < 7:
                        cgpa_sem = is_gpa(cur_block[-2])
                        egp_tot = float(cur_block[-3])
                        creds_tot = float(cur_block[-4])
                        sgpa_sem = is_gpa(cur_block[-5])
                        if cur_block[-6].find('.') > -1:
                            egp_sem = float(cur_block[-6])
                        else:
                            egp_sem = 0
                        #creds_sem = float(cur_block[-7])
                        all_details['Records'][cur_term]['CGPA'] = cgpa_sem
                        all_details['Records'][cur_term]['SGPA'] = sgpa_sem
                        all_details['Records'][cur_term]['EGP'] = egp_sem
                        #all_details['Records'][cur_term]['Credits Earned'] = creds_sem
                        all_details['Records'][cur_term]['EGP_Total'] = egp_tot
                        all_details['Records'][cur_term]['Credits_Total'] = creds_tot
                        if cur_term in latest_terms:
                            all_details['CGPA'] = cgpa_sem
                            all_details['Credits_Total'] = creds_tot
                            all_details['EGP_Total'] = egp_tot

            if cur_line == "endstream"+chr(10):
                database[cur_roll] = all_details
                cur_cg = all_details['CGPA']
                if not cur_branch:
                    print(all_details['Roll'],all_details['Name'])
                if cur_branch in department_data:
                    if cur_batch in department_data[cur_branch]:
                        department_data[cur_branch][cur_batch][cur_roll] = cur_cg
                    else:
                        department_data[cur_branch][cur_batch] = {cur_roll:cur_cg}
                else:
                    department_data[cur_branch] = {cur_batch:{cur_roll:cur_cg}}
                break
            cur_line = file.readline()

    cur_line = file.readline()
    while not cur_line in ["%%EOF","%%EOF"+chr(10)]:
        cur_line = file.readline()
        if cur_line == "1 1 1 rg"+chr(10):
            individual()

    print("\tFile fully parsed...")
    print("\tData ready to be analysed...")
    # End of PDF Parser...


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
    def Make_Marklist(self,course=False,course_term=None,branch=None,batch=None,term=latest_terms[0],cg=False,sg=False,names=False):
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
        categories = [[10,0],[9,0],[8,0],[7,0],[6,0],[5,0],[4,0]]#,['F',0]]
        if cumulative:
            categories = [[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0]]#,['F',0]]
        for mark in marklist:
            if isinstance(mark,tuple):
                mark = mark[0]
            #if mark == 0:
            #    categories[7][1] += 1
            for i in range(len(categories)-1):
                if mark >= categories[i][0]:
                    categories[i][1] += 1
                    if not cumulative:
                        break
        if percent:
            total = len(marklist)
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
                cur_data['courses'].append((course_data[course]['Name']+' ('+course+')').encode('ascii','ignore'))
                cur_data['data'].append(stud_data['Records'][term]['Courses'][course])
            term_data.append(cur_data)
            terms.append(cur_data['name'])
        for i in range(len(term_data)):
            term_data[i]['color'] = i
        to_return.append(terms)
        to_return.append(term_data)
        return to_return

    # End of Analyser


# The main() caller... Finally :)
if __name__ == '__main__':
    main()