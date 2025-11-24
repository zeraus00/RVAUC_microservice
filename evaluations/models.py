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
    student_id_raw = models.CharField(max_length=256)
    gender = models.CharField(max_length=16, default='', blank=True)
    detected_items = models.JSONField(default=dict)

    completeness = models.BooleanField(default=False)
    missing = models.JSONField(default=list)
    score = models.FloatField(default=0.0)
    forwarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Eval {self.id} for {self.student_id_raw} at {self.created_at.isoformat()}"

    # Infer gender based on detected items
    def infer_gender_from_items(self):
        d = self.detected_items or {}
        male_cues = bool(d.get('polo')) or bool(d.get('black_slacks'))
        female_cues = bool(d.get('blouse')) or bool(d.get('skirt'))

        if male_cues and not female_cues:
            return 'male'
        if female_cues and not male_cues:
            return 'female'
        return 'unknown'

    # Compute completeness, missing items, and score
    def compute_completeness(self, use_inference_if_unknown=True):
        d = self.detected_items or {}

        # Infer gender
        inferred_gender = self.infer_gender_from_items()
        if use_inference_if_unknown:
            self.gender = inferred_gender

        # Required items based on gender
        if self.gender == "male":
            required = ["polo", "logo", "black_slacks", "black_shoes"]
        elif self.gender == "female":
            required = ["blouse", "logo", "green_belt", "skirt", "black_shoes"]
        else:
            return False, [], 0.0, self.gender

        # Detected items that are True
        detected_set = []
        for item, value in d.items():
            if value == True:
                detected_set.append(item)

        # Compute missing items: missing required OR any detected False
        missing = []
        for item in required:
            if item not in detected_set:
                missing.append(item)
        for item, value in d.items():
            if value == False and item not in missing:
                missing.append(item)

        completeness = len(missing) == 0
        score = (len(required) - len([m for m in missing if m in required])) / len(required) if len(required) > 0 else 0.0

        return completeness, missing, score, self.gender
