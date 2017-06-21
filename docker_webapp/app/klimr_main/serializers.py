from collections import OrderedDict
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from klimr_main import models


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Semester
        fields = ('id', 'start_on', 'test_week_on', 'test_week_end_on', 'session_on', 'session_end_on')


class ShortSemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Semester
        fields = ('id', 'start_on')

class LessonTimingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LessonTiming
        fields = ('id', 'start', 'end')


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        fields = ('id', 'first_name', 'middle_name', 'last_name', 'students', 'teachers')
        read_only_fields = ('students', 'teachers')


class ShortPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        fields = ('id', 'first_name', 'middle_name', 'last_name')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = ('id', 'name', 'description')


class ShortDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = ('id', 'name')


class CourseSerializer(serializers.ModelSerializer):
    # TODO Teachers
    # TODO Groups
    department = ShortDepartmentSerializer()

    class Meta:
        model = models.Course
        fields = ('id', 'name', 'description', 'department')
        depth = 1


class ShortCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ('id', 'name')


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = ('id', 'person', 'department')


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discipline
        fields = ('id', 'name', 'description', 'teachers')


class ShortDisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Discipline
        fields = ('id', 'name')


class ShortGroupSerializer(serializers.ModelSerializer):
    course = ShortCourseSerializer(read_only=True)
    last_semester = ShortSemesterSerializer(read_only=True)

    class Meta:
        model = models.Group
        fields = ('id', 'name', 'course', 'last_semester') 


class ShortSubgroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subgroup
        fields = ('id', 'name')


class GroupDetails(object):
    def __init__(self, group, state):
        self.name = group.name
        self.course = group.course
        self.year = group.states.count() - 1 // 2
        self.praepostor = state.praepostor.person_id
        primary_subgroups = state.subgroup_set.filter(primary=True)


class PrimarySubgroupData(object):
    def __init__(self, subgroup, students):
        self.subgroup = subgroup
        self.students = students


class ShortStudentSerializer(serializers.ModelSerializer):
    # TODO Teachers
    # TODO Stats
    # TODO ExpelledInThisSemester
    person = ShortPersonSerializer()
    expelled = serializers.BooleanField()
    # department = ShortDepartmentSerializer()

    class Meta:
        model = models.Student
        # person_id, student_id
        fields = ('id', 'person', 'expelled')
        # depth = 1


class PrimarySubgroupDataSerializer(serializers.Serializer):
    subgroup = ShortSubgroupSerializer()
    students = ShortStudentSerializer(many=True)


class GroupStateSerializer(serializers.ModelSerializer):
    course = ShortCourseSerializer()

    def to_representation(self, obj):
        result = super(GroupStateSerializer, self).to_representation(obj)
        primary_subgroups = obj.subgroup_set
        print(primary_subgroups.count())
        if primary_subgroups is not None:
            if primary_subgroups.count() > 1: 
                result['primary_subgroups'] = [
                    {
                        'subgroup': x.id,
                        'name': x.name,
                        'students': ShortStudentSerializer(x.student_set.all(), many=True).data
                    }
                    for x in primary_subgroups.all()
                ]
            elif primary_subgroups.count() == 1:
                result['students'] = ShortStudentSerializer(primary_subgroups.first().student_set.all(), many=True).data
            else:
                result['students'] = []
            result['year'] = str(obj.year)
        return result

    class Meta:
        model = models.GroupSemesterState
        fields = ('id', 'name', 'course', 'praepostor')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ('id', 'name', 'last_semester')


# class NewGroupSerializer(serializers.Serializer):
#     name = serializers.CharField(min_length=2, max_length=255)
#     semester = serializers.IntegerField()
#     course = serializers.IntegerField()
#     praepostor = serializers.IntegerField()


class TeacherSerializer(serializers.ModelSerializer):
    department = ShortDepartmentSerializer()

    def to_representation(self, instance):
        result = super(TeacherSerializer, self).to_representation(instance)
        result['disciplines'] = ShortDisciplineSerializer(instance.disciplines, many=True).data
        print(instance.groups)
        result['groups'] = ShortGroupSerializer(instance.groups, many=True).data
        return result

    class Meta:
        model = models.Teacher
        fields = ('id', 'department')


class ShortTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = ('id', 'person', 'name')


class StudentSerializer(serializers.ModelSerializer):
    # TODO Teachers
    # TODO Stats
    # person = PersonSerializer()
    # department = ShortDepartmentSerializer()

    class Meta:
        model = models.Student
        fields = ('person', 'first_semester')
        # depth = 1


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Classroom
        fields = ('id', 'name', 'classroom_type', 'comments')


class ShortClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Classroom
        fields = ('id', 'name')


class LessonSerializer(serializers.ModelSerializer):
    discipline = ShortDisciplineSerializer()
    classroom = ShortClassroomSerializer()
    teacher = ShortTeacherSerializer()
    groups = ShortSubgroupSerializer(many=True)

    class Meta:
        model = models.Lesson
        fields = ('id', 'date', 'start_time', 'end_time', 'discipline',
                  'teacher', 'classroom', 'groups', 'state', 'reason')
