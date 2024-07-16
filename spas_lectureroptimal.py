from readFile import SPASFileReader
from pprint import pprint as pp

class SPALLecturerOptimal:
    def __init__(self, filename):
        self.filename = filename
        r = SPASFileReader(self.filename)
        r.read_file()

        self.students = r.students
        self.projects = r.projects
        self.lecturers = r.lecturers
        self.blocking_pair = False
        self.stable_matching = {}

        self.M = {} # provisional assignments
        self.under_subscribed_lecturers = list(self.lecturers.keys())

        for student in self.students:
            self.M[student] = {"assigned": None}

        for project in self.projects:
            self.M[project] = {"assigned": set()}

        for lecturer in self.lecturers:
            self.M[lecturer] = {"assigned": set()}


    def delete(self, student, project):
        self.students[student]['list'].remove(project)
        self.projects[project]['list'].remove(student)


    def check_pair_conditions(self, s_i, p_j, l_k):
        # s_i is not provisionally assigned to p_j
        # and p_j in P_k is under subscribed
        # and s_i in L_k^j
        
        return self.M[s_i]["assigned"] != p_j \
        and p_j in self.lecturers[l_k]['projects'] \
        and len(self.M[p_j]["assigned"]) < self.projects[p_j]['upper_quota'] \
        and s_i in self.projects[p_j]['list']
        

    def find_valid_pair(self, l_k):
        # s_i is first valid on l_k list
        # p_j is first valid on s_i list

        for s_i in self.lecturers[l_k]['list']:
            for p_j in self.students[s_i]['list']:
                if self.check_pair_conditions(s_i, p_j, l_k):
                    return (s_i, p_j)


    def break_assignment(self, student):
        p = self.M[student]["assigned"]
        l = self.projects[p]["lecturer"]
        self.M[student]["assigned"] = None
        self.M[p]["assigned"].remove(student)
        self.M[l]["assigned"].remove(student)

        # add now under-subscribed lecturer to under_subscribed_lecturers
        # also add at correct position
        self.under_subscribed_lecturers.insert(int(l[1])-1, l)


    def provisionally_assign(self, student, project, lecturer):
        self.M[student]["assigned"] = project
        self.M[project]["assigned"].add(student)
        self.M[lecturer]["assigned"].add(student)


    def while_loop(self):
        while len(self.under_subscribed_lecturers) > 0:
            l_k = self.under_subscribed_lecturers[0]
            pair = self.find_valid_pair(l_k)
            if pair is not None:
                s_i, p_j = pair
            else:
                # cannot find a valid pair, continue to next lecturer
                self.under_subscribed_lecturers.remove(l_k)
                continue

            # if s_i is provisionally assigned to some project p, break assignment
            if self.M[s_i]["assigned"] is not None:
                self.break_assignment(s_i)

            # provisionally assign s_i to p_j and to l_k
            self.provisionally_assign(s_i, p_j, l_k)

            # for each successor p of p_j on s_i's list, delete(s_i, p)
            p_j_pos = self.students[s_i]['list'].index(p_j)
            for p in self.students[s_i]['list'][p_j_pos+1:]:
                self.delete(s_i, p)

            # check if lecturer is still under subscribed
            if len(self.M[l_k]["assigned"]) >= self.lecturers[l_k]["upper_quota"]:
                self.under_subscribed_lecturers.remove(l_k)

    # =======================================================================    
    # blocking pair types
    # =======================================================================    
    def blockingpair_1bi(self, student, project, lecturer):
        #  project and lecturer capacity
        cj, dk = self.projects[project]["upper_quota"], self.lecturers[lecturer]["upper_quota"]
        # no of students assigned to project in M
        project_occupancy, lecturer_occupancy = len(self.M[project]["assigned"]), len(self.M[lecturer]["assigned"])
        #  project and lecturer are both under-subscribed
        if project_occupancy < cj and lecturer_occupancy < dk:
            return True
        return False
    
    def blockingpair_1bii(self, student, project, lecturer):
        # p_j is undersubscribed, l_k is full and either s_i \in M(l_k)
        # or l_k prefers s_i to the worst student in M(l_k)
        cj, dk = self.projects[project]["upper_quota"], self.lecturers[lecturer]["upper_quota"]
        project_occupancy, lecturer_occupancy = len(self.M[project]["assigned"]), len(self.M[lecturer]["assigned"])
        #  project is undersubscribed and lecturer is full
        if project_occupancy < cj and lecturer_occupancy == dk:
            Mlk_students = self.M[lecturer]["assigned"]
            if student in Mlk_students: # s_i \in M(lk)
                return True
            student_rank = self.lecturers[lecturer]["rank"][student]
            for worst_student in self.M[lecturer]["assigned"]:
                worst_student_rank = self.lecturers[lecturer]["rank"][worst_student]
                if student_rank < worst_student_rank: # lk prefers s_i to her worst student in M(l_k)
                    return True                
        return False
    
    def blockingpair_1biii(self, student, project, lecturer):
        # p_j is full and l_k prefers s_i to the worst student in M(p_j)
        cj, project_occupancy = self.projects[project]["upper_quota"], len(self.M[project]["assigned"])
        if project_occupancy == cj:
            student_rank = self.projects[project]["rank"][student]
            for worst_student in self.M[project]["assigned"]:
                worst_student_rank = self.projects[project]["rank"][worst_student]
                if student_rank < worst_student_rank: # lk prefers s_i to her worst student in M(p_j)
                    return True    
        return False

    # =======================================================================    
    # Is M stable? Check for blocking pair
    # self.blocking_pair is set to True if blocking pair exists
    # =======================================================================
    def check_stability(self):        
        for student in self.students:
            preferred_projects = self.students[student]["list"]
            if self.M[student]["assigned"] != None:
                matched_project = self.M[student]["assigned"]
                rank_matched_project = self.students[student]["rank"][matched_project]
                A_si = self.students[student]["list"]
                preferred_projects = [pj for pj in A_si[:rank_matched_project]] # every project that s_i prefers to her matched project                                
        
            for project in preferred_projects:
                lecturer = self.projects[project]["lecturer"]
                if not self.blocking_pair:
                    self.blocking_pair = self.blockingpair_1bi(student, project, lecturer)
                if not self.blocking_pair:
                    self.blocking_pair = self.blockingpair_1bii(student, project, lecturer)
                if not self.blocking_pair:
                    self.blocking_pair = self.blockingpair_1biii(student, project, lecturer)
                
                if self.blocking_pair:
                #    print(student, project, lecturer)
                   break
            
            if self.blocking_pair:
                # print(student, project, lecturer)
                break
 
        
    def run(self):
        
        self.while_loop()
        self.check_stability()
        # construct stable matching with only students as keys
        for student in self.students:
            self.stable_matching[student] = self.M[student]["assigned"] if self.M[student]["assigned"] else "  "
            

        if not self.blocking_pair: return f"lecturer-optimal stable matching: {self.stable_matching}"
        else: return f"Unstable matching: {self.stable_matching}"


def main():
    # for k in range(1, 11):
    #     filename = f"instances/instance{k}.txt"
    #     print(f"instance{k}.txt".ljust(14) + " -> ", end=' ')
    #     s = SPALLecturerOptimal(filename)
    #     print(s.run())
    s = SPALLecturerOptimal("test3.txt")
    print(s.run())
    
if __name__ == "__main__":
    main()