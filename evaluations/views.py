from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Evaluation
from .serializers import EvaluationSerializer
import os, requests
from django.utils import timezone
from django.db.models import Q

FORWARD_BACKEND_URL = os.getenv('FORWARD_BACKEND_URL')
BACKEND_API_TOKEN = os.getenv('BACKEND_API_TOKEN')


class EvaluationCreateView(generics.ListCreateAPIView):
    queryset = Evaluation.objects.all()
    serializer_class = EvaluationSerializer

    def perform_create(self, serializer):
        eval_obj = serializer.save(created_at=timezone.now())

        payload = {
            "student_id": eval_obj.student.student_id if eval_obj.student else eval_obj.student_id_raw,
            "student_id_raw": eval_obj.student_id_raw,
            "gender": eval_obj.gender,
            "detected_items": eval_obj.detected_items,
            "completeness": eval_obj.completeness,
            "missing": eval_obj.missing,
            "score": eval_obj.score,
            "timestamp": eval_obj.created_at.isoformat(),
            "evaluation_id": eval_obj.id,
        }

        if FORWARD_BACKEND_URL:
            try:
                headers = {'Content-Type': 'application/json'}
                if BACKEND_API_TOKEN:
                    headers['Authorization'] = f"Bearer {BACKEND_API_TOKEN}"

                resp = requests.post(
                    FORWARD_BACKEND_URL,
                    json=payload,
                    headers=headers,
                    timeout=5
                )
                resp.raise_for_status()
                eval_obj.forwarded = True
                eval_obj.save()

            except Exception as e:
                print("Forwarding failed:", e)


class EvaluationListView(generics.ListAPIView):
    queryset = Evaluation.objects.all().order_by('-created_at')
    serializer_class = EvaluationSerializer


class LastEvaluationForStudentView(APIView):
    def get(self, request, student_id):
        evaluation = Evaluation.objects.filter(
            Q(student__student_id=student_id) | Q(student_id_raw=student_id)
        ).order_by('-created_at').first()

        if not evaluation:
            return Response(
                {"error": f"No evaluation found for this student: {student_id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EvaluationSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)
