from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from klimr_main.serializers import *
from klimr_main.models import Semester, Holiday, LessonTiming, Person, \
    Department, Course, Teacher, Discipline, Lesson, \
    Student, Group, GroupSemesterState, Classroom
from rest_framework import viewsets, mixins
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response


class ShortGenericViewset(viewsets.GenericViewSet):
    """
    Viewset that uses different serializers for list and
    retrieve
    """
    short_serializer_class = None
    short_queryset = None

    def get_short_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.short_queryset`.

        This method should always be used rather than accessing
        `self.short_queryset` directly, as `self.short_queryset` gets evaluated
        only once, and those results are cached for all subsequent requests.
        """
        if self.short_queryset is None:
            short_queryset = self.queryset
        else:
            short_queryset = self.short_queryset

        assert short_queryset is not None, (
            "'%s' should either include a `queryset` or `short_queryset`"
            " attributes, or override the `get_short_queryset()` method."
            % self.__class__.__name__
        )

        if isinstance(short_queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            short_queryset = short_queryset.all()
        return short_queryset

    def get_short_serializer_class(self):
        """
        Return the class to use for the short serializer.
        Defaults to using `self.short_serializer_class`.
        """
        if (self.short_serializer_class) is None:
            serializer_class = self.serializer_class
        else:
            serializer_class = self.short_serializer_class
        assert serializer_class is not None, (
            "'%s' should either include a `short_serializer_class` or "
            "`serializer_class` attributes, or override the "
            "`get_short_serializer_class()` method."
            % self.__class__.__name__
        )

        return serializer_class

    def get_short_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing short output.
        """
        serializer_class = self.get_short_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


class ShortListModelMixin(object):
    """
    List a queryset.
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_short_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_short_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_short_serializer(queryset, many=True)
        return Response(serializer.data)


class SemesterViewSet(viewsets.ModelViewSet):
    """
    Directory API: semesters information endpoint
    """
    queryset = Semester.objects.all().order_by('start_on')
    serializer_class = SemesterSerializer


class LessonTimingViewSet(viewsets.ModelViewSet):
    """
    Directory API: lesson time infromation endpoint
    """
    queryset = LessonTiming.objects.all().order_by('start')
    serializer_class = LessonTimingSerializer


class PersonViewSet(viewsets.ModelViewSet):
    """
    Directory API: person (student/teacher) information endpoint
    """
    # TODO Separate views instead of viewsets, as we want to get
    # teacher/student entities
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    Directory API: department information endpoint
    """
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    Directory API: course information endpoint
    """
    queryset = Course.objects.all().order_by('name')
    serializer_class = CourseSerializer


class DisciplineViewSet(ShortGenericViewset,
                        ShortListModelMixin,
                        viewsets.ModelViewSet):
    """
    Directory API: discipline information endpoint
    TODO Retrieve/Groups
    TODO Retrieve/Departments
    TODO Nested Teachers
    """
    queryset = Discipline.objects.all().order_by('name')
    serializer_class = DisciplineSerializer
    short_serializer_class = ShortDisciplineSerializer


class GroupViewSet(ShortListModelMixin,
                   ShortGenericViewset):
    """
    Group information directory
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    short_queryset = Group.objects.all()
    short_serializer_class = ShortGroupSerializer

    def retrieve(self, request, pk=None):
        group = get_object_or_404(Group.objects, pk=pk)
        return Response(GroupStateSerializer(group.states.latest()).data)

    @list_route(methods=['get', 'post'], url_path='(?P<pk>[0-9]+)/state')
    def state_list(self, request, pk=None):
        if request.method is 'POST':
            pass
        else:
            group = get_object_or_404(Group.objects, pk=pk)
            return Response(GroupStateSerializer(group.states.all(), many=True).data)

    @detail_route(methods=['get'], url_path='state/(?P<state_pk>[0-9]+)')
    def state_details(self, request, pk=None, state_pk=None):
        state = get_object_or_404(
            GroupSemesterState.objects.filter(group=pk),
            pk=state_pk
        )
        return Response(GroupStateSerializer(state).data)



class TeacherViewSet(mixins.CreateModelMixin,
                     ShortListModelMixin,
                     ShortGenericViewset):
    """
    Directory API: teacher information endpoint

    NOTE: Positive ID is treated as Person ID and response will contain
    all the Teacher objects (and some details) related to specified Person.
    Negative ID is treated as Teacher ID, which basically means:

    IF YOU WANT TO DELETE ONE SPECIFIC PERSON-TEACHER RELATION, USE NEGATIVE ID
    OF RELATION (e.g. -20) INSTEAD OF PERSON ID, BECAUSE OTHERWISE YOU WILL
    DELETE EVERY TEACHER-PERSON RELATION CONNECTED TO THAT PERSON!

    TODO Ordering
    """

    queryset = Teacher.objects.order_by('person').distinct()
    serializer_class = TeacherSerializer
    short_queryset = Person.objects.filter(
        id__in=Teacher.objects.all().values_list('person_id', flat=True)
    )
    short_serializer_class = ShortPersonSerializer

    def retrieve(self, request, pk=None):
        # # TODO Try to simplify this code by rewriting code w/o proxy objects
        if int(pk) < 0:
            teacher_relation = get_object_or_404(Teacher.objects, pk=-int(pk))
            return Response(TeacherSerializer(teacher_relation).data)
        #
        teacher_person = get_object_or_404(Person.objects, pk=pk)
        teachers = teacher_person.get_teachers()
        return Response(TeacherSerializer(teachers, many=True).data)

    def destroy(self, request, pk=None):
        if pk > 0:
            teacher_person = get_object_or_404(Person.objects, pk=pk)
            Teacher.objects.filter(person=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            get_object_or_404(Teacher.objects, pk=-int(pk)).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class StudentViewSet(ShortListModelMixin,
                     ShortGenericViewset):
    """
    DOES NOT WORK YET
    Directory API: students information endpoint
    TODO Retrieve
    """

    queryset = Student.objects.order_by('person').distinct()
    serializer_class = StudentSerializer
    short_queryset = Person.objects.filter(
        id__in=Student.objects.all().values_list('person_id', flat=True)
    )
    short_serializer_class = ShortPersonSerializer

    def retrieve(self, request, pk=None):
        # TODO This code is copy-pasted from above, so, make sure you checked
        # all the TODOS there
        if int(pk) < 0:
            student_relation = get_object_or_404(Student.objects, pk=-int(pk))
            return Response(StudentSerializer(student_relation).data)

        student_person = get_object_or_404(Person.objects, pk=pk)

        #return Response(serializer.data)


class ClassroomViewSet(ShortListModelMixin,
                       ShortGenericViewset):
    """
    Directory API: classroom information endpoint
    """
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    short_queryset = Classroom.objects.all()
    short_serializer_class = ShortClassroomSerializer


class LessonViewSet(viewsets.ModelViewSet):
    """
    Lesson information endpoint
    use /lesson/group/GROUP_ID/
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    @list_route(methods=['get', 'post'], url_path='group/(?P<group_pk>[0-9]+)')
    def lessons_for_group(self, request, group_pk=None):
        qs = Lesson.objects.all().filter(groups=group_pk)
        return Response(LessonSerializer(qs, many=True).data)

