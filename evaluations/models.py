from django.db import models
from django.utils import timezone

class Student(models.Model):
    student_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.student_id} - {self.name or 'Unknown'}"


class Evaluation(models.Model):
    GENDER_CHOICES = (('male','Male'), ('female','Female'), ('unknown','Unknown'))
    id = models.AutoField(primary_key=True)

    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    student_id_raw = models.CharField(max_length=256)
    detected_items = models.JSONField(default=dict)

    completeness = models.BooleanField(default=False)
    missing = models.JSONField(default=list)
    score = models.FloatField(default=0.0)
    forwarded = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Eval {self.id} for {self.student_id_raw} at {self.created_at.isoformat()}"

    # Compute completeness, missing items, and score
    def compute_completeness(self, use_inference_if_unknown=True):
        detections = self.detected_items or {}

        # requirements components for each specific model
        REQUIREMENTS = {
            "type_a_male" : ["Polo", "Slack Pants", "Black Shoes"],
            "type_a_female" : ["black_shoes", "green_belt", "lu_blouse", "lu_logo", "skirt"],
            "buffalo" : ["buffalo_uniform"],
            "cs_dept_shirt" : ["cs_dept_shirt_uniform"]
        }

        best_match = "type_a_male"
        max_matches = -1

        # 2. Best Match Logic
        for unif_type, components in REQUIREMENTS.items():
            current_match_count = 0
            for item in components:
                if detections.get(item) is True:
                    if item in ["buffalo_uniform", "cs_dept_shirt_uniform"]:
                        current_match_count += 10
                    else:
                        current_match_count += 1

            # count the components and match it based on the model
            if current_match_count > max_matches:
                max_matches = current_match_count
                best_match = unif_type

        # validation for the best match
        required_list = REQUIREMENTS[best_match]

        # Compute missing items: missing required OR any detected False
        missing_items = []
        for item in required_list:
            if detections.get(item) is not True:
                missing_items.append(item)

        # 4. Update Model Fields
        self.missing = missing_items
        self.completeness = (len(self.missing) == 0)
        
        # Calculate Score
        total_required = len(required_list)
        if total_required > 0:
            found_count = total_required - len(self.missing)
            self.score = found_count / total_required
        else:
            self.score = 0.0

        self.save()

        return self.completeness, self.missing, self.score, best_match