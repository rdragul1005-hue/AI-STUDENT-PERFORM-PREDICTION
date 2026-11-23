import html
import tempfile
import unittest
from pathlib import Path

from app import COURSES, app, init_db


class StudentPerformanceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        app.config.update(TESTING=True, DATABASE=str(Path(self.temp_dir.name) / "test.sqlite"))
        init_db()
        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def sign_in(self):
        return self.client.post(
            "/login",
            data={"name": "Asha Student", "register_number": "TEST001"},
            follow_redirects=True,
        )

    def test_welcome_page_shows_college_and_project_identity(self):
        response = self.client.get("/")
        self.assertIn(b"MUTHAYAMMAL ENGINEERING COLLEGE", response.data)
        self.assertIn(b"STUDENT PERFORMANCE PREDICTION", response.data)
        self.assertIn(b"campus.svg", response.data)

    def test_login_saves_student_and_dashboard_lists_all_courses(self):
        response = self.sign_in()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Asha Student", response.data)
        for course in COURSES.values():
            self.assertIn(course["name"].encode(), response.data)

    def test_quiz_is_locked_until_five_minutes_are_recorded(self):
        self.sign_in()
        response = self.client.get("/quiz/c", follow_redirects=True)
        self.assertIn(b"Study this course for at least 5 minutes", response.data)

        response = self.client.post("/api/time", json={"language": "c", "seconds": 300})
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/time", json={"language": "c", "seconds": 45})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["language_seconds"], 45)

    def test_every_course_has_five_lessons_and_a_ten_question_quiz(self):
        self.sign_in()
        for language, course in COURSES.items():
            self.assertEqual(len(course["lessons"]), 5)
            self.assertEqual(len(course["quiz"]), 10)
            self.assertEqual(len(course["practice"]), 5)
            for page in range(1, 6):
                response = self.client.get(f"/materials/{language}/{page}")
                self.assertEqual(response.status_code, 200)
                self.assertIn(b"PRACTICAL PROGRAM", response.data)
                self.assertIn(
                    course["practice"][page - 1],
                    html.unescape(response.get_data(as_text=True)),
                )
            for _ in range(7):
                self.client.post("/api/time", json={"language": language, "seconds": 45})
            response = self.client.get(f"/quiz/{language}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.count(b'class="question-card"'), 10)

    def test_passing_quiz_updates_course_completion_and_report(self):
        self.sign_in()
        for _ in range(7):
            self.client.post("/api/time", json={"language": "c", "seconds": 45})
        answers = {
            f"answer_{index}": str(question[2] if index < 7 else (question[2] + 1) % 4)
            for index, question in enumerate(COURSES["c"]["quiz"])
        }
        response = self.client.post("/quiz/c/submit", data=answers, follow_redirects=True)
        self.assertIn(b"Course completed", response.data)
        response = self.client.get("/report")
        self.assertIn(b"7 / 10", response.data)
        self.assertIn(b"COMPLETED", response.data)

    def test_failed_quiz_can_be_retaken(self):
        self.sign_in()
        for _ in range(7):
            self.client.post("/api/time", json={"language": "c", "seconds": 45})
        answers = {f"answer_{index}": "9" for index in range(10)}
        response = self.client.post("/quiz/c/submit", data=answers, follow_redirects=True)
        self.assertIn(b"give it another go", response.data)
        self.assertIn(b"Retake quiz", response.data)


if __name__ == "__main__":
    unittest.main()
