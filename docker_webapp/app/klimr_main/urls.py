from django.conf.urls import url, include
from rest_framework import routers
from klimr_main import views

router = routers.DefaultRouter()
router.register(r'info/course', views.CourseViewSet)
router.register(r'info/classroom', views.ClassroomViewSet)
router.register(r'info/discipline', views.DisciplineViewSet)
router.register(r'info/department', views.DepartmentViewSet)
router.register(r'info/group', views.GroupViewSet)
router.register(r'schedule', views.LessonViewSet)
router.register(r'info/person', views.PersonViewSet)
router.register(r'info/semester', views.SemesterViewSet)
router.register(r'info/student', views.StudentViewSet)
router.register(r'info/teacher', views.TeacherViewSet)
router.register(r'info/timing', views.LessonTimingViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
