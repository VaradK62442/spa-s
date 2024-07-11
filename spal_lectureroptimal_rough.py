'''
LOG:

lecturer quotas are not being respected idk why
otherwise seems correct? need to read more

'''

from readFile import SPASFileReader
from pprint import pprint as pp

filename = "instances/instance1.txt"
r = SPASFileReader(filename)
r.read_file()

# pp(r.students)
# pp(r.projects)
# pp(r.lecturers)

s_assignments = {student: None for student in r.students}
p_assignments = {project: [] for project in r.projects}
l_assignments = {lecturer: [] for lecturer in r.lecturers}

deletions = set()

for l_k in r.lecturers:
    # while some lecturer is under_subscribed
    while len(l_assignments[l_k]) < r.lecturers[l_k]['upper_quota']:
        # find pair (s_i, p_j) that satisfies criteria
        for stu in r.lecturers[l_k]['list']:
            for pro in r.students[stu]['list']:
                if s_assignments[stu] != pro \
                and pro in r.lecturers[l_k]['projects'] \
                and len(p_assignments[pro]) < r.projects[pro]['upper_quota'] \
                and stu in r.projects[pro]['list']:
                    s_i = stu
                    p_j = pro

                    if (s_i, p_j) not in deletions:
                        # break existing assignment
                        p = s_assignments[s_i]
                        if p is not None:
                            p_assignments[p].remove(s_i)
                            l_assignments[r.projects[p]['lecturer']].remove(s_i)
                            s_assignments[s_i] = None

                        s_assignments[s_i] = p_j
                        p_assignments[p_j].append(s_i)
                        l_assignments[l_k].append(s_i)

                        # update deletions
                        p_j_pos = r.students[s_i]['list'].index(p_j)
                        for p in r.students[s_i]['list'][p_j_pos+1:]:
                            deletions.add((s_i, p))

                    break


pp(s_assignments)
pp(p_assignments)
pp(l_assignments)