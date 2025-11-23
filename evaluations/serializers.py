from rest_framework import serializers
from .models import Evaluation, Student

class EvaluationSerializer(serializers.ModelSerializer):
    student_id = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Evaluation
        fields = ['id','student','student_id','student_id_raw','gender','detected_items',
                  'completeness','missing','score','forwarded','created_at']
        read_only_fields = ['id','completeness','missing','score','forwarded','created_at','student']

    def create(self, validated_data):
        student_key = self.initial_data.get('student_id') or validated_data.get('student_id_raw')
        student = None
        if student_key:
            student, _ = Student.objects.get_or_create(student_id=student_key)

        validated_data.pop('student_id', None)
        validated_data['student'] = student

        eval_obj = super().create(validated_data)

        completeness, missing, score, used_gender = eval_obj.compute_completeness(use_inference_if_unknown=True)
        eval_obj.completeness = completeness
        eval_obj.missing = missing
        eval_obj.score = score

        if eval_obj.gender == 'unknown' and used_gender in ('male','female'):
            eval_obj.gender = used_gender

        eval_obj.save()
        return eval_obj
