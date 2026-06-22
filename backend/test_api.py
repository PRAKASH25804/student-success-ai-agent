import unittest
import json
import os
import sys

# Ensure backend directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Gemini Key for unit tests to prevent network requirements in basic test phases
os.environ['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', 'mock_testing_key_123')

from backend.app import app
from backend.db import init_db

class TestStudentSuccessAgentAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Configure app for testing
        app.config['TESTING'] = True
        cls.client = app.test_client()
        with app.app_context():
            init_db()

    def test_01_serve_home(self):
        """Test if the entry route serves index.html"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_02_get_profile(self):
        """Test retrieving the student profile data"""
        response = self.client.get('/api/profile')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('profile', data)
        self.assertEqual(data['profile']['id'], 1)

    def test_03_post_profile(self):
        """Test updating student profile variables"""
        payload = {
            "name": "Jane Tester",
            "email": "jane@university.edu",
            "career_goal": "Data Scientist",
            "skills": "R, Python, Jupyter, Statistics"
        }
        response = self.client.post(
            '/api/profile',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        
        # Verify changes took effect
        response_get = self.client.get('/api/profile')
        data_get = json.loads(response_get.data)
        self.assertEqual(data_get['profile']['name'], 'Jane Tester')
        self.assertEqual(data_get['profile']['career_goal'], 'Data Scientist')

    def test_04_chat_history_and_clear(self):
        """Test chat operations and clear logs"""
        # Retrieve history
        response = self.client.get('/api/chat/history')
        self.assertEqual(response.status_code, 200)
        
        # Clear logs
        response_clear = self.client.post('/api/chat/clear')
        self.assertEqual(response_clear.status_code, 200)
        data_clear = json.loads(response_clear.data)
        self.assertEqual(data_clear['status'], 'success')

    def test_05_get_analytics(self):
        """Test summary retrieval for Chart.js rendering"""
        response = self.client.get('/api/analytics')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('analytics', data)
        self.assertIn('resume_history', data['analytics'])
        self.assertIn('skill_history', data['analytics'])

if __name__ == '__main__':
    unittest.main()
