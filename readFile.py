#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 24 13:47:18 2023

@author: sofiat
"""

class SPASFileReader:
    
    def __init__(self, filename):
        self.filename = filename
        self.no_students = 0
        self.no_projects = 0
        self.no_lecturers = 0  # assume number of lecturers <= number of projects
        self.students = {}                
        self.projects = {}
        self.lecturers = {}
        self.lp_rank = {}
        self.proj_rank = {}

    def read_file(self):  # reads the SPA-S instance
        with open(self.filename) as t:
            t = t.read().splitlines()
        #print(t)
        self.no_students, self.no_projects, self.no_lecturers = map(int, t[0].split())
        # print(self.no_students, self.no_projects, self.no_lecturers)
        # ------ build the students dictionary
        for elt in t[1:self.no_students+1]:
            entry = elt.split()
            student = f"s{entry[0]}"
            preferences = [f"p{k}" for k in entry[1:]]
            # store the index of each project on each student's preference list, for ease of deletion later on in the allocation
            rank = {proj: idx for idx, proj in enumerate(preferences)}
            self.students[student] = {"list": preferences, "rank": rank, "list_length": len(preferences), "head_idx": 0}
        

        # ------ build the projects dictionary

        for elt in t[self.no_students+1 : self.no_students+self.no_projects+1]:
            entry = elt.split()
            self.projects[f"p{entry[0]}"] = {"upper_quota": int(entry[1]), "lecturer": f"l{entry[2]}"}
            
        
        # ------ build the lecturers dictionary
        for elt in t[self.no_students+self.no_projects+1 : self.no_students+self.no_projects+self.no_lecturers+1]:
            entry = elt.split()
            lecturer = f"l{entry[0]}"
            capacity = int(entry[1])
            preferences = [f"s{i}" for i in entry[2:]]
            rank = {stud: idx for idx, stud in enumerate(preferences)}
            self.lecturers[lecturer] = {"upper_quota": capacity, "projects": set(), "list": preferences, "rank": rank}
        for project in self.projects:
            lec = self.projects[project]["lecturer"]
            self.lecturers[lec]["projects"].add(project)
            lecturer_list = self.lecturers[lec]["list"]
            project_list = [stu for stu in lecturer_list if project in self.students[stu]["list"]]
            rank = {stud: idx for idx, stud in enumerate(project_list)}
            self.projects[project]["list"] = project_list
            self.projects[project]["rank"] = rank
            


                    
#------------------------------------------------------------------------------------------------
# s = SPASFileReader("instances/instance1.txt")
# s.read_file()

# for i in s.students:
#     print(f"{i} :::> {s.students[i]}")
# print()
# for p in s.projects:
#     print(f"{p} :::> {s.projects[p]}")
# print()   
# for l in s.lecturers:
#     print(f"{l} :::> {s.lecturers[l]}")