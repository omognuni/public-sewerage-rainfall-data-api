from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicAPITest(TestCase):
    '''public user api 테스트'''
    
    def setUp(self):
        self.client = APIClient()
    
    def test_create_user_success(self):
        '''회원가입 테스트'''
        payload = {
            'username': 'testname',
            'password': 'testpass',
        }
        
        res = self.client.post(CREATE_USER_URL, payload)
        
        user = get_user_model().objects.get(username=payload['username'])
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)
        
    def test_password_too_short_error(self):
        '''짧은 비밀번호 입력 시 에러 '''
        payload = {
            'username': 'testname',
            'password': 'pw',
            'name': 'testname',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            username=payload['username']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        '''로그인 시 토큰 생성'''
        payload = {
            'username': 'testname',
            'password': 'testpass',
        }

        get_user_model().objects.create_user(**payload)
        
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        '''잘못된 계정 입력 시 토큰 미생성'''
        payload1 = {
            'username': 'testname',
            'password': 'testpass',
        }
        res = self.client.post(CREATE_USER_URL, payload1)
        
        payload2 = {
            'username': 'testname',
            'password': 'wrong',
        }

        res = self.client.post(TOKEN_URL, payload2)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    
    