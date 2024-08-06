from spas_studentoptimal import SPASStudentOptimal
from spas_lectureroptimal import SPALLecturerOptimal
from instanceGenerator import SPAS as InstanceGenerator

from itertools import permutations
from tqdm import tqdm
from pprint import pprint as pp

# TODO: split this into optimalLyingStudent and optimalLyingLecturer
# TODO: parameterise more so that any person + multiple people can lie


class OptimalLying:
    def __init__(self, filename: str):
        self.filename = filename
        self.s = SPASStudentOptimal(self.filename)
        self.l = SPALLecturerOptimal(self.filename)
        self.s.run()
        self.l.run()


    def find_student_happiness(self, stable_matching: dict) -> int:
        # find total happiness of student s1 given a stable matching
        # happiness is the sum of the ranks of the assigned projects
        # e.g. if rank is 1 2 3 and assigned is 2, then happiness is 1
        # lower happiness is better
        # unassigned is len(students) happiness value
        return self.s.students['s1']['rank'][stable_matching['s1']] if stable_matching['s1'] != '' else len(self.s.students)
    

    def find_lecturer_happiness(self, stable_matching: dict) -> int:
        return sum([
            self.l.lecturers['l1']['rank'][student]
            for student in [s for s in stable_matching if stable_matching[s] in self.l.lecturers['l1']['projects']]
        ])
    

    def optimise_happiness(self, optimiser: SPASStudentOptimal | SPALLecturerOptimal, optimiser_data: dict, happiness_finder: callable, stable_matching: dict) -> dict:
        """
        Function to optimise the happiness value for a given set of parameters.

        :param optimiser: is the algorithm to use
        :param optimiser_data: is the data required to optimise the happiness value (either self.s.students or self.l.lecturers)
        :param happiness_finder: is the function to find the happiness value (find_{student or lecturer}_happiness)
        :param stable_matching: is the stable matching to use
        """
        if optimiser == SPASStudentOptimal: person = 's1'
        else: person = 'l1'
        better_happiness_perms = []
        preference_list = optimiser_data[person]['list']
        permutation_list = list(permutations(preference_list))

        current_happiness = happiness_finder(stable_matching)

        for perm in permutation_list:
            o = optimiser(self.filename)
            if type(o) == SPASStudentOptimal:
                o.students[person]['list'] = list(perm)
                o.students[person]['rank'] = {s: i for i, s in enumerate(list(perm))}
            elif type(o) == SPALLecturerOptimal:
                # print(perm)
                o.lecturers[person]['list'] = list(perm)
                o.lecturers[person]['rank'] = {s: i for i, s in enumerate(list(perm))}
                for project in o.lecturers[person]['projects']:
                    # update ranks
                    project_list = [s for s in list(perm) if project in o.students[s]['list']]
                    rank = {s: i for i, s in enumerate(project_list)}
                    o.projects[project]['list'] = project_list
                    o.projects[project]['rank'] = rank
            o.run()

            new_happiness = happiness_finder(o.stable_matching)
            if new_happiness < current_happiness:
                better_happiness_perms.append(perm)

        return {
            "better_happiness_perms": better_happiness_perms,
            "all_perms": permutation_list
        }
    

    def run(self):
        student_data = self.optimise_happiness(SPASStudentOptimal, self.s.students, self.find_student_happiness, self.s.stable_matching)
        lecturer_data = self.optimise_happiness(SPALLecturerOptimal, self.l.lecturers, self.find_lecturer_happiness, self.l.stable_matching)

        return student_data, lecturer_data
    

def display_results(results: list):
    for student_data, _ in results:
        if len(student_data['better_happiness_perms']) > 0:
            print(f"Student happiness can be improved by lying")


def main():
    TOTAL_STUDENTS = 5
    LOWER_PROJECT_BOUND = 2
    UPPER_PROJECT_BOUND = 3
    REPETITIONS = 10_000

    results = []
    for _ in tqdm(range(REPETITIONS)):
        i = InstanceGenerator(TOTAL_STUDENTS, LOWER_PROJECT_BOUND, UPPER_PROJECT_BOUND)
        i.instance_generator_no_tie()
        i.write_instance_no_ties('i.txt')

        o = OptimalLying('i.txt')

        # print(f"Starting student preference list: {o.s.students['s1']['list']}")
        # print(f"Starting lecturer preference list: {o.l.lecturers['l1']['list']}")
        # print(f"Student happiness: {o.find_student_happiness(o.s.stable_matching)}")
        # print(f"Lecturer happiness: {o.find_lecturer_happiness(o.l.stable_matching)}")
        # print(f"Student stable matching: {o.s.stable_matching}")
        # print(f"Lecturer stable matching: {o.l.stable_matching}")

        student_data, lecturer_data = o.run()
        results.append((student_data, lecturer_data))

    display_results(results)


if __name__ == "__main__":
    main()    