from django.urls import path
from .views import EvaluationCreateView, EvaluationListView, LastEvaluationForStudentView

urlpatterns = [
    path('create/', EvaluationCreateView.as_view(), name='evaluation-create'),
    path('evaluation-list/', EvaluationListView.as_view(), name='evaluation-list'),
    path('student_id/<str:student_id>/', LastEvaluationForStudentView.as_view(), name='student_id-evaluation'),
]
