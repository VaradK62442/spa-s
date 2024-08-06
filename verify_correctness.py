from instanceGenerator import SPAS as InstanceGenerator
from spas_lectureroptimal import SPALLecturerOptimal
from spas_studentoptimal import SPASStudentOptimal
from enumerateSMs import ESMS

import math
import os
from tqdm import tqdm


class VerifyCorrectness:
    def __init__(self, total_students, lower_project_bound, upper_project_bound, write_to_file):
        self._total_students = total_students
        self._lower_project_bound = lower_project_bound
        self._upper_project_bound = upper_project_bound
        self._write_to_file = write_to_file

        self._default_filename = 'instance.txt'
        self._results_dir = 'results/'
        self._correct_count = 0
        self._incorrect_count = 0


    def generate_instances(self, filename=None):
        s = InstanceGenerator(self._total_students, self._lower_project_bound, self._upper_project_bound)
        s.instance_generator_no_tie()
        if filename is None:
            filename = self._default_filename
        s.write_instance_no_ties(filename)
        return s


    def verify_instance(self, filename=None):
        if filename is None:
            filename = self._default_filename

        e = ESMS(filename)
        s = SPASStudentOptimal(filename)
        l = SPALLecturerOptimal(filename)

        e.choose(1)
        s.run()
        l.run()

        return l.stable_matching == e.all_matchings[-1] and s.stable_matching == e.all_matchings[0]
    

    def run(self):
        s = self.generate_instances()
        if self.verify_instance():
            self._correct_count += 1
        else:
            self._incorrect_count += 1
            if self._write_to_file:
                s.write_instance_no_ties(f"{self._results_dir}incorrect_instance_{self._incorrect_count}.txt")
    

    def show_results(self):
        print(f"""
            Total students: {self._total_students}
            Lower project bound: {self._lower_project_bound}
            Upper project bound: {self._upper_project_bound}
            Repetitions: {self._correct_count + self._incorrect_count}

            Correct: {self._correct_count}
            Incorrect: {self._incorrect_count}
              """)


def main():
    TOTAL_STUDENTS = 5
    LOWER_PROJECT_BOUND = 2
    UPPER_PROJECT_BOUND = 3
    REPETITIONS = 100_000
    WRITE_TO_FILE = True

    assert UPPER_PROJECT_BOUND <= int(math.ceil(0.5 * TOTAL_STUDENTS)), "Upper project bound is too high"
    assert WRITE_TO_FILE and os.path.isdir('results'), "Please create a 'results' directory"

    v = VerifyCorrectness(TOTAL_STUDENTS, LOWER_PROJECT_BOUND, UPPER_PROJECT_BOUND, WRITE_TO_FILE)
    for _ in tqdm(range(REPETITIONS)):
        v.run()

    v.show_results()
    

if __name__ == '__main__':
    main()