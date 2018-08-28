class Subject:
    def __init__(self, number, name, year):
        self.number = number
        self.name = name
        self.year = year
        self.progress = set()
        self.start_date = None
        self.students = []
        self.teachers = []
        self.homeworks = []
        self.tests = []
        self.final_exams = []

    def __str__(self):
        return "<Subject {0} {1} in year {2}>".format(self.number, self.name, self.year)

    def finish_action(self, action):
        self.progress.add(action)

    def add_final_exam(self, final_exam):
        self.final_exams.append(final_exam)

    def add_student(self, student):
        self.students.append(student)

    def add_teacher(self, teacher):
        self.teachers.append(teacher)

    def clear_final_exams(self):
        self.final_exams = []

    def clear_students(self):
        self.students.clear()

    def clear_teachers(self):
        self.teachers.clear()

    def get_final_exam_by_date_time(self, date_time):
        for final_exam in self.final_exams:
            if final_exam.date_time == date_time:
                return final_exam
