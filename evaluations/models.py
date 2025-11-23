from django.db import models
from django.utils import timezone

class Student(models.Model):
    student_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.student_id} - {self.name or 'Unknown'}"

class Evaluation(models.Model):
    GENDER_CHOICES = (('male','Male'), ('female','Female'), ('unknown','Unknown'))

    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    student_id_raw = models.CharField(max_length=256, blank=True, default='')
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES, default='unknown')
    detected_items = models.JSONField(default=dict)

    completeness = models.BooleanField(default=False)
    missing = models.JSONField(default=list)
    score = models.FloatField(default=0.0)
    forwarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Eval {self.id} for {self.student_id_raw} at {self.created_at.isoformat()}"

    def infer_gender_from_items(self):
        d = self.detected_items or {}
        male_cues = bool(d.get('polo')) and bool(d.get('black_slacks'))
        female_cues = bool(d.get('blouse')) and bool(d.get('skirt'))

        if male_cues and not female_cues:
            return 'male'
        if female_cues and not male_cues:
            return 'female'
        return 'unknown'

    def compute_completeness(self, use_inference_if_unknown=True):
        d = self.detected_items or {}
        used_gender = self.gender
        if used_gender == 'unknown' and use_inference_if_unknown:
            inferred = self.infer_gender_from_items()
            if inferred != 'unknown':
                used_gender = inferred

        missing = []
        if used_gender == 'male':
            if not (d.get('polo') and d.get('logo')):
                if not d.get('polo'):
                    missing.append('polo')
                if not d.get('logo'):
                    missing.append('logo')
            if not d.get('black_slacks'):
                missing.append('black_slacks')
            if not d.get('black_shoes'):
                missing.append('black_shoes')
            required_count = 4

        elif used_gender == 'female':
            if not (d.get('blouse') and d.get('logo')):
                if not d.get('blouse'):
                    missing.append('blouse')
                if not d.get('logo'):
                    missing.append('logo')
            if not d.get('green_belt'):
                missing.append('green_belt')
            if not d.get('skirt'):
                missing.append('skirt')
            if not d.get('black_shoes'):
                missing.append('black_shoes')
            required_count = 5

        else:
            if not d.get('logo'):
                missing.append('logo')
            if not d.get('black_shoes'):
                missing.append('black_shoes')
            required_count = 2

        completeness = (len(missing) == 0)
        detected_count = max(0, required_count - len(missing))
        score = detected_count / required_count if required_count else 0.0

        return completeness, missing, score, used_gender