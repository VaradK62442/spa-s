from instanceGenerator import SPAS as InstanceGenerator
from spas_lectureroptimal import SPALLecturerOptimal
from enumerateSMs import ESMS

import math
from pprint import pprint as pp
from matplotlib import pyplot as plt
from tqdm import tqdm


class VerifyCorrectness:
    def __init__(self, total_students, lower_project_bound, upper_project_bound, write_to_file):
        self._total_students = total_students
        self._lower_project_bound = lower_project_bound
        self._upper_project_bound = upper_project_bound
        self._write_to_file = write_to_file

        self._default_filename = 'instance.txt'
        self._results_dir = 'results/'
        self._results_filename = '_results.txt'
        self._correct_count = 0
        self._incorrect_count = 0


    def generate_instances(self):
        s = InstanceGenerator(self._total_students, self._lower_project_bound, self._upper_project_bound)
        s.instance_generator_no_tie()
        s.write_instance_no_ties(self._default_filename)
        return s


    def verify_instance(self, filename=None):
        if filename is None:
            filename = self._default_filename

        e = ESMS(filename)
        s = SPALLecturerOptimal(filename)

        e.choose(1)
        s.run()

        return s.stable_matching == e.all_matchings[-1]
    

    def run(self):
        def write_msg_to_file(msg):
            if self._write_to_file:
                with open(self._results_dir + self._results_filename, 'a') as f:
                    f.write(msg)

        s = self.generate_instances()
        if self.verify_instance():
            self._correct_count += 1
            write_msg_to_file(f"PASS: Instance occurs last in list of all matchings\n")
        else:
            self._incorrect_count += 1
            write_msg_to_file(f"FAIL: Instance does not occur in list of all matchings - {self._incorrect_count}\n")
            if self._write_to_file:
                s.write_instance_no_ties(f"{self._results_dir}incorrect_instance_{self._incorrect_count}.txt")
    

    def show_results(self):
        print(f"Correct: {self._correct_count}\nIncorrect: {self._incorrect_count}")

        # _, ax = plt.subplots()
        # ax.bar(['Correct', 'Incorrect'], (
        #     self._correct_count, self._incorrect_count
        # ))
        # plt.show()


def main():
    TOTAL_STUDENTS = 5
    LOWER_PROJECT_BOUND = 2
    UPPER_PROJECT_BOUND = 3
    REPETITIONS = 1_000
    WRITE_TO_FILE = False

    assert UPPER_PROJECT_BOUND <= int(math.ceil(0.5 * TOTAL_STUDENTS)), "Upper project bound is too high"

    v = VerifyCorrectness(TOTAL_STUDENTS, LOWER_PROJECT_BOUND, UPPER_PROJECT_BOUND, WRITE_TO_FILE)
    for _ in tqdm(range(REPETITIONS)):
        v.run()

    v.show_results()
    

if __name__ == '__main__':
    main()