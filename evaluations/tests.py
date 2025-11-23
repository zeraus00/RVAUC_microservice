from django.test import TestCase
from .models import Evaluation

class InferenceTests(TestCase):
    def test_infer_male(self):
        e = Evaluation(student_id_raw="x", detected_items={"polo":True,"black_slacks":True})
        self.assertEqual(e.infer_gender_from_items(), 'male')

    def test_infer_female(self):
        e = Evaluation(student_id_raw="x", detected_items={"blouse":True,"skirt":True})
        self.assertEqual(e.infer_gender_from_items(), 'female')

    def test_conflict(self):
        e = Evaluation(student_id_raw="x", detected_items={"polo":True,"black_slacks":True,"blouse":True,"skirt":True})
        self.assertEqual(e.infer_gender_from_items(), 'unknown')
