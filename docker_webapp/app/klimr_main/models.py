import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
import django.utils.timezone
    


# TODO Order


class Semester(models.Model):
    start_on = models.DateField()
    test_week_on = models.DateField(unique_for_year='start_on')
    test_week_end_on = models.DateField(unique_for_year='start_on')
    session_on = models.DateField(unique_for_year='start_on')
    session_end_on = models.DateField(unique_for_year='start_on')

    def __str__(self):
        return '%s' % (str(self.start_on))


class Holiday(models.Model):
    date = models.DateField()
    reason = models.CharField(max_length=100, unique_for_year='date')

    def __str__(self):
        return '%s: %s' % (str(self.date), self.reason)


class LessonTiming(models.Model):
    start = models.TimeField()
    end = models.TimeField()

    class Meta:
        unique_together = (("start", "end"), )

    def __str__(self):
        return 'Lesson %s - %s' % (str(self.start), str(self.end))


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def get_teachers(self):
        return Teacher.objects.filter(person=self.id)

    def get_teachers_departments(self):
        return Department.objects.filter(teacher__in=self.get_teachers())

    def get_students(self):
        return Student.objects.filter(person=self.id)

    def get_students_departments(self):
        return Department.objects.filter(student__in=self.get_students())

    def is_student(self):
        return self.get_students().count() != 0

    def is_teacher(self):
        return self.get_teachers().count() != 0

    def __str__(self):
        return '%s %s %s' % (self.first_name, self.middle_name, self.last_name)


class KlimrUser(models.Model):
    djuser = models.OneToOneField(User, on_delete=models.CASCADE)
    person = models.OneToOneField(Person, on_delete=models.PROTECT)
    registered_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'KU:%s %s %s' % (
            self.person.first_name,
            self.person.middle_name,
            self.person.last_name
        )


class Department(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, blank=True)
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    department = models.ForeignKey(Department)

    def __str__(self):
        return self.name


class Group(models.Model):
    """
    Literally, just a hack to connect all the group changes w/o
    composed PK (because user input is really unreliable, and
    angry/evil praepostor can take other group's name and it will
    lead us to a conflict that could be prevented programatically)

    TODO Autoremove groups w/o any states
    """
    course = models.ForeignKey(Course)

    @property
    def first_semester(self):
        if self.states.count() > 0:
            return self.states.earliest().semester
        return None

    @property
    def last_semester(self):
        return self.states.latest().semester or None
    
    @property
    def name(self):
        return self.states.latest().name

    def __str__(self):
        fs = self.first_semester
        fsstart = 'NO SUBGROUP'
        if fs is not None:
            fsstart = str(fs.start_on)
        return '%s (%s)' % (
            self.course.name, fsstart
        )

    def save(self, *args, **kwargs):
        return super(Group, self).save(*args, **kwargs)


class GroupSemesterState(models.Model):
    """
    Chronology of group states

    TODO Remove group when removing last state?
    """
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, related_name='states')
    praepostor = models.ForeignKey('Student', blank=True, null=True)
    semester = models.ForeignKey(Semester)

    @property
    def course(self):
        return self.group.course

    @property
    def year(self):
        prv = Semester.objects.filter(start_on__lt=self.semester.start_on)
        return (prv.count() // 2) + 1

    def __str__(self):
        return self.name + ' (' + str(self.semester.start_on) + ')'

    class Meta:
        get_latest_by = 'semester__start_on'


class Subgroup(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(GroupSemesterState)
    primary = models.BooleanField()
    disciplines = models.ManyToManyField('Discipline')
    teachers = models.ManyToManyField('Teacher')

    def __str__(self):
        return str(self.group) + ', ' + self.name


class Teacher(models.Model):
    # Note that it's not OneToOne, so we can keep the history
    # of teacher's updates (e.g. transfers between departments)
    person = models.ForeignKey(Person, related_name='teachers')
    department = models.ForeignKey(Department)
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)  # TODO Remove field

    class Meta:
        unique_together = (("person", "department"), )

    @property
    def disciplines(self):
        return Discipline.objects.filter(teachers=self.id)

    @property
    def groups(self):
        return Group.objects.filter(id__in=Lesson.objects.filter(teacher=self).values_list('groups', flat=True))

    @property
    def name(self):
        return str(self.person)

    def __str__(self):
        return str(self.person) + ' @ ' + self.department.name


class Student(models.Model):
    # Same as in Teacher, FK instead of OneToOne so we can
    # track transfers and stuff
    person = models.ForeignKey(Person, related_name='students')
    subgroups = models.ManyToManyField(Subgroup)
    expelled_in = models.ForeignKey(Semester, null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    @property
    def expelled(self):
        return self.expelled_in is not None

    def __str__(self):
        if self.expelled_in is not None:
            return str(self.person) + ' (expelled ' + str(self.expelled_in) + ')'
        return str(self.person)


class Discipline(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    teachers = models.ManyToManyField(Teacher)
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Classroom(models.Model):
    name = models.CharField(max_length=100)
    # Why? I don't know
    CLASSROOM_TYPES = (
        (-1, 'N/A'),
        (0, 'Other'),
        (1, 'Small lecture hall'),
        (2, 'Small laboratory'),
        (3, 'Big lecture hall'),
        (4, 'Teachers\' room'),
    )
    classroom_type = models.IntegerField(
        choices=CLASSROOM_TYPES,
        default=-1,
    )
    comments = models.TextField(max_length=1000)  # e.g. "How to get there"

    def __str__(self):
        return self.name


class Assignment(models.Model):
    discipline = models.ForeignKey(Discipline)
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return '%s: %s' % (str(self.discipline), self.name)


class CompletedAssignment(models.Model):
    student = models.ForeignKey(Student)
    assignment = models.ForeignKey(Assignment)
    completed_on = models.DateField(default=django.utils.timezone.now)

    def __str__(self):
        return '%s completed \'%s\'@%s' % (
            str(self.student),
            self.assignment.name,
            str(self.completed_on)
        )


class LessonPrototype(models.Model):
    WEEKDAYS = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    day_of_week = models.IntegerField(choices=WEEKDAYS)
    WEEKTYPES = (
        (0, 'Both'),
        (1, 'Odd'),
        (2, 'Even')
    )
    weektype = models.IntegerField(choices=WEEKTYPES)
    start_time = models.ForeignKey(LessonTiming, related_name="start_time")
    end_time = models.ForeignKey(LessonTiming, related_name="end_time")
    discipline = models.ForeignKey(Discipline)
    teacher = models.ForeignKey(Teacher)
    classroom = models.ForeignKey(Classroom)
    groups = models.ManyToManyField(Subgroup)

    def __str__(self):
        return '%s (lt%s - lt%s) w/ %s' % (
            self.discipline.name,
            self.start_time.id,
            self.end_time.id, str(self.teacher)
        )


class Lesson(models.Model):
    date = models.DateField()
    start_time = models.ForeignKey(LessonTiming, related_name="start_time")
    end_time = models.ForeignKey(LessonTiming, related_name="end_time")
    discipline = models.ForeignKey(Discipline)
    teacher = models.ForeignKey(Teacher)
    classroom = models.ForeignKey(Classroom)
    groups = models.ManyToManyField(Subgroup)
    assignments = models.ManyToManyField(Assignment, blank=True)
    LESSON_STATES = (
        (0, 'Scheduled'),
        (1, 'On Time'),
        (2, 'Arrived'),
        (3, 'Cancelled')
    )
    state = models.IntegerField(choices=LESSON_STATES)
    reason = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return '%s@%s (lt%s - lt%s) w/ %s' % (
            self.discipline.name,
            str(self.date), self.start_time.id,
            self.end_time.id, str(self.teacher)
        )

    class Meta:
        ordering = ['date', 'start_time__start']


class QueueRecord(models.Model):
    student = models.ForeignKey(Student)  # Sorry, dear teachers
    lesson = models.ForeignKey(Lesson)
    assignments = models.ManyToManyField(Assignment, blank=True)
    REASON_CHOICES = (
        (0, "Autograph"),
        (1, "Assignment"),
        (2, "Question"),
    )
    reason = models.IntegerField(choices=REASON_CHOICES)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%d (%s)' % (self.id, str(self.student))


class Measurement(models.Model):
    user = models.ForeignKey(Person)
    lesson = models.ForeignKey(Lesson)
    record = models.ForeignKey(QueueRecord)
    # Offset from the start of first lesson of same discipline and type
    time = models.IntegerField()


class AdvisedQueue(models.Model):
    record = models.ForeignKey(QueueRecord, on_delete=models.PROTECT)
    rank = models.IntegerField()

    class Meta:
        unique_together = (("record", "rank"), )


class Achievement(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=511)
    image = models.ImageField(height_field=512, width_field=512)


admin.site.register(Semester)
admin.site.register(Holiday)
admin.site.register(LessonTiming)
admin.site.register(Person)
admin.site.register(KlimrUser)
admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Group)
admin.site.register(GroupSemesterState)
admin.site.register(Subgroup)
admin.site.register(Student)
admin.site.register(Discipline)
admin.site.register(Classroom)
admin.site.register(Assignment)
admin.site.register(CompletedAssignment)
admin.site.register(Lesson)
admin.site.register(QueueRecord)
admin.site.register(Measurement)
admin.site.register(AdvisedQueue)
admin.site.register(Achievement)