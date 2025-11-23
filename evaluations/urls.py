from django.urls import path
from .views import EvaluationCreateView, EvaluationListView, LastEvaluationForStudentView, EvaluationSearchPostView

urlpatterns = [
    path('create/', EvaluationCreateView.as_view(), name='evaluation-create'),
    path('evaluationlist/', EvaluationListView.as_view(), name='evaluation-list'),
    path('last/<str:student_id>/', LastEvaluationForStudentView.as_view(), name='evaluation-last'),
    path('search-post/', EvaluationSearchPostView.as_view(), name='evaluation-serch-post')
]
