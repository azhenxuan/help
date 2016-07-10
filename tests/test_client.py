import unittest
import os
import time
from flask import url_for
from flask_login import login_user
from app import create_app, db
from app.models import UserModule, Consultation, User, Module
from app.main.api import *

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

        # Create user
        self.test_token = os.environ.get('test_token')

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Platform to facilitate consultations between users.' in response.data)

    # def test_login(self):
    #     response = self.client.get(url_for('main.index'), query_string=dict(token=self.test_token), follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(b'Hi, Ken Oung Yong Quan' in response.data)
    #     with self.client.session_transaction() as sess:
    #         self.assertEqual(sess.get('token'), self.test_token)
    #     time.sleep(5)

    def test_login_get_provide_help_logout(self):
        # Login
        response = self.client.get(url_for('main.index'), query_string=dict(token=self.test_token), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Hi, Ken Oung Yong Quan' in response.data)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('token'), self.test_token)

        # Visit get_help page
        response = self.client.get(url_for('main.get_help'), follow_redirects=True)
        self.assertTrue(b'Consults' in response.data)

        # Visit provide_help page
        response = self.client.get(url_for('main.provide_help'), follow_redirects=True)
        self.assertTrue(b'Fill in the form to create a new consultation.' in response.data)
        time.sleep(5)

        # Logout
        response = self.client.get(url_for('main.logout'), follow_redirects=True)
        self.assertTrue(b'You have successfully logged out' in response.data)
        time.sleep(5)


    def test_error_404(self):
        response = self.client.get('/nothing-here')
        self.assertEqual(response.status_code, 404)
        self.assertTrue(b"There's Nothing Here" in response.data)

    def test_error_401(self):
        response = self.client.get('/get_help', follow_redirects=True)
        self.assertTrue(b"You are currently logged out." in response.data)





    # def test_register_and_login(self):
    #     # register a new account
    #     response = self.client.post(url_for('auth.register'), data={
    #         'email': 'john@example.com',
    #         'username': 'john',
    #         'password': 'cat',
    #         'password2': 'cat'
    #     })
    #     self.assertTrue(response.status_code == 302)

    #     # login with the new account
    #     response = self.client.post(url_for('auth.login'), data={
    #         'email': 'john@example.com',
    #         'password': 'cat'
    #     }, follow_redirects=True)
    #     self.assertTrue(re.search(b'Hello,\s+john!', response.data))
    #     self.assertTrue(
    #         b'You have not confirmed your account yet' in response.data)

    #     # send a confirmation token
    #     user = User.query.filter_by(email='john@example.com').first()
    #     token = user.generate_confirmation_token()
    #     response = self.client.get(url_for('auth.confirm', token=token),
    #                                follow_redirects=True)
    #     self.assertTrue(
    #         b'You have confirmed your account' in response.data)

    #     # log out
    #     response = self.client.get(url_for('auth.logout'), follow_redirects=True)
    #     self.assertTrue(b'You have been logged out' in response.data)
