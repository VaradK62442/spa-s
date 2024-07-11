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
        # iterate through all projects first
        # if fail to find, then iterate through students

        for s_i in self.lecturers[l_k]['list']:
            for p_j in self.students[s_i]['list']:
                # check conditions
                if self.check_pair_conditions(s_i, p_j, l_k):
                    return (s_i, p_j)


    def break_assignment(self, student):
        p = self.M[student]["assigned"]
        l = self.projects[p]["lecturer"]
        self.M[student]["assigned"] = None
        self.M[p]["assigned"].remove(student)
        self.M[l]["assigned"].remove(student)


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


    def run(self):
        self.while_loop()
        self.matching = {}

        for student in self.students:
            self.matching[student] = self.M[student]["assigned"] if self.M[student]["assigned"] else "  "

        return self.matching


def main():
    for k in range(1, 11):
        filename = f"instances/instance{k}.txt"
        print(f"instance{k}.txt".ljust(14) + " -> ", end=' ')
        s = SPALLecturerOptimal(filename)
        print(s.run())

if __name__ == "__main__":
    main()