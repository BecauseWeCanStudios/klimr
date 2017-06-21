from django.contrib import admin
from klimr_main.models import Teacher

# Register your models here.


class TeacherAdmin(admin.ModelAdmin):
    fields = ('person', 'department')
    exclude = ('disciplines', 'groups', 'name')


admin.site.register(Teacher, TeacherAdmin)