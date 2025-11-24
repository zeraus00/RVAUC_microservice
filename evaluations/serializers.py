from rest_framework import serializers
from .models import Evaluation, Student


class EvaluationSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Evaluation
        fields = [
            'id',
            'student',
            'student_id',
            'student_id_raw',
            'gender',
            'detected_items',
            'completeness',
            'missing',
            'score',
            'forwarded',
            'created_at'
        ]

        read_only_fields = [
            'id',
            'student',
            'gender',
            'completeness',
            'missing',
            'score',
            'forwarded',
            'created_at'
        ]

    def validate(self, data):
        detected = self.initial_data.get("detected_items")
        if not detected:
            raise serializers.ValidationError({"detected_items": "Detected items are required."})

        if not self.initial_data.get("student_id") and not data.get("student_id_raw"):
            raise serializers.ValidationError({"student_id": "Student number is required."})

        return data

    def create(self, validated_data):
        student_number = self.initial_data.get("student_id") or validated_data.get("student_id_raw")

        # Create/find student
        student = None
        if student_number:
            student, _ = Student.objects.get_or_create(student_id=student_number)

        validated_data['student'] = student
        validated_data.pop('student_id', None)

        validated_data['gender'] = "unknown"
        eval_obj = super().create(validated_data)

        # Compute results
        completeness, missing, score, inferred_gender = eval_obj.compute_completeness()

        eval_obj.completeness = completeness
        eval_obj.missing = missing
        eval_obj.score = score
        eval_obj.gender = inferred_gender

        eval_obj.save()

        return eval_obj
