from django.urls import path
from .views import EvaluationCreateView, EvaluationListView, LastEvaluationForStudentView

urlpatterns = [
    path('create/', EvaluationCreateView.as_view(), name='evaluation-create'),
    path('', EvaluationListView.as_view(), name='evaluation-list'),
    path('last/<str:student_id>/', LastEvaluationForStudentView.as_view(), name='evaluation-last'),
]
