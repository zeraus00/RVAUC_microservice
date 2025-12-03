from django.contrib import admin
from .models import Student, Evaluation

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id','name')

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('id','student','student_id_raw','gender','completeness','score','forwarded','created_at')
    list_filter = ('gender','completeness','forwarded')
    readonly_fields = ('created_at',)
