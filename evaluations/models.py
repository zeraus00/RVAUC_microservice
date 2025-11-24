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

    def infer_gender_from_items(self):
        d = self.detected_items or {}
        male_cues = bool(d.get('polo')) and bool(d.get('black_slacks'))
        female_cues = bool(d.get('blouse')) and bool(d.get('skirt'))

        if male_cues and not female_cues:
            return 'male'
        if female_cues and not male_cues:
            return 'female'
        return 'None'

    def compute_completeness(self, use_inference_if_unknown=True):
        d = self.detected_items or {}
        gender = self.infer_gender_from_items()

        # Use inferred gender if original is unknown
        if use_inference_if_unknown and self.gender == "unknown":
            self.gender = gender

        # REQUIREMENTS
        if self.gender == "male":
            required = {"polo", "logo", "black_slacks", "black_shoes"}
        elif self.gender == "female":
            required = {"blouse", "logo", "green_belt", "skirt", "black_shoes"}
        else:
            # gender unknown, cannot compute proper completeness
            return False, [], 0.0, self.gender

        detected_set = {k for k, v in d.items() if v is True}

        missing = sorted(list(required - detected_set))

        completeness = (len(missing) == 0)

        score = (len(required) - len(missing)) / len(required)

        return completeness, missing, score, self.gender