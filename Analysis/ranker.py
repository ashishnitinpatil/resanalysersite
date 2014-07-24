#!/usr/bin/env python
# Ranker...
# Licensed under Creative Commons Attribution 3.0 Unported License;

import os
import re
import sys
import time
import logging
import json

from ResAnalyser import *

with open(os.path.join(os.getcwd(),'department_data.txt'),'r') as department_data_file:
     department_data = json.load(department_data_file)

rank_data = dict()
batches = dict()
insti_mark_list = list()
for dept in department_data:
    rank_data[dept] = dict()
    dept_mark_list = list()
    for batch in department_data[dept]:
        if batch not in batches:
            batches[batch] = True
        batch_mark_list = list()
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
    insti_batch_mark_list = list()
    for dept in department_data:
        if batch in department_data[dept]:
            batch_mark_list = list()
            for indi in department_data[dept][batch]:
                batch_mark_list.append(department_data[dept][batch][indi])
            insti_batch_mark_list.extend(batch_mark_list)
    insti_batch_mark_list.sort(reverse=True)
    rank_data[batch] = insti_batch_mark_list

print("\n\tRanking done.")
with open(os.path.join(os.getcwd(),'rank_data.txt'),'w') as g4:
    print("\n\tGenerated rank_data.txt")
    g4.write(json.dumps(rank_data))

