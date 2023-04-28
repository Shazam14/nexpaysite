from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase

class RegistrationAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_url = '/api/register/'  # Update with your registration API URL

    def test_registration_api_view(self):
        # Define test data
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            # Add any other required fields for registration
        }

        # Send POST request to registration API
        response = self.client.post(self.registration_url, data=data)

        # Assert the response status code, expected to be HTTP_201_CREATED for successful registration
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Add more assertions to test the response data or other expected behavior
