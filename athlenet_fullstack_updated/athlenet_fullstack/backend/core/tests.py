from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from .models import Follow, PlayerProfile, Profile


class AccountFeatureTests(APITestCase):
    def registration_data(self, username, email, phone='9876543210', password='StrongPass!'):
        return {
            'username': username,
            'email': email,
            'password': password,
            'phone': phone,
            'pincode': '560001',
            'role': 'user',
        }

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            '/api/auth/register/',
            self.registration_data('weak-password', 'weak@example.com', password='lowercase'),
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('Password must be at least 8 characters', response.data['detail'])

    def test_registration_prevents_duplicate_mobile_with_country_code(self):
        first = self.client.post('/api/auth/register/', self.registration_data('first', 'first@example.com'))
        self.assertEqual(first.status_code, 201)

        second = self.client.post(
            '/api/auth/register/',
            self.registration_data('second', 'second@example.com', phone='+91 98765 43210'),
        )
        self.assertEqual(second.status_code, 400)
        self.assertIn('mobile number already exists', second.data['detail'])

    def test_login_uses_username_instead_of_email(self):
        User.objects.create_user(username='login-member', email='login@example.com', password='StrongPass!')

        username_login = self.client.post(
            '/api/auth/login/',
            {'username': 'login-member', 'password': 'StrongPass!'},
            format='json',
        )
        email_login = self.client.post(
            '/api/auth/login/',
            {'username': 'login@example.com', 'password': 'StrongPass!'},
            format='json',
        )

        self.assertEqual(username_login.status_code, 200)
        self.assertEqual(email_login.status_code, 401)

    def test_user_can_change_email_and_duplicate_email_is_rejected(self):
        user = User.objects.create_user(username='member', email='old@example.com', password='password')
        Profile.objects.create(user=user)
        User.objects.create_user(username='another', email='taken@example.com', password='password')
        self.client.force_authenticate(user=user)

        changed = self.client.patch('/api/me/', {'email': 'new@example.com'}, format='json')
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(changed.data['email'], 'new@example.com')

        duplicate = self.client.patch('/api/me/', {'email': 'TAKEN@example.com'}, format='json')
        self.assertEqual(duplicate.status_code, 400)

    def test_user_cannot_change_to_another_accounts_mobile(self):
        owner = User.objects.create_user(username='phone-owner', password='password')
        member = User.objects.create_user(username='phone-member', password='password')
        Profile.objects.create(user=owner, phone='9876543210', phone_key='9876543210')
        Profile.objects.create(user=member, phone='9123456789', phone_key='9123456789')
        self.client.force_authenticate(user=member)

        response = self.client.patch('/api/me/', {'phone': '+91 98765 43210'}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('mobile number already exists', response.data['detail'])

    def test_user_can_edit_profile_and_player_details_but_not_username(self):
        user = User.objects.create_user(username='profile-owner', password='password')
        profile = Profile.objects.create(user=user, role='player')
        PlayerProfile.objects.create(profile=profile, sport='Cricket')
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            '/api/me/',
            {'location': 'Pune', 'sport': 'Football', 'level': 'State', 'interests': 'Cricket, Football'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['location'], 'Pune')
        self.assertEqual(response.data['interests'], 'Cricket,Football')
        self.assertEqual(response.data['player_details']['sport'], 'Football')
        self.assertEqual(response.data['player_details']['level'], 'State')

        username_change = self.client.patch('/api/me/', {'username': 'new-name'}, format='json')
        self.assertEqual(username_change.status_code, 400)
        user.refresh_from_db()
        self.assertEqual(user.username, 'profile-owner')

    def test_connections_lists_followed_members(self):
        user = User.objects.create_user(username='follower', password='password')
        target = User.objects.create_user(username='followed', password='password')
        Profile.objects.create(user=user)
        Profile.objects.create(user=target)
        Follow.objects.create(follower=user, following=target)
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/connections/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([member['user']['username'] for member in response.data], ['followed'])
        self.assertTrue(response.data[0]['is_following'])

    def test_followers_lists_users_who_follow_current_user(self):
        user = User.objects.create_user(username='popular-member', password='password')
        follower = User.objects.create_user(username='fan', password='password')
        followed = User.objects.create_user(username='followed-by-member', password='password')
        Profile.objects.create(user=user)
        Profile.objects.create(user=follower)
        Profile.objects.create(user=followed)
        Follow.objects.create(follower=follower, following=user)
        Follow.objects.create(follower=user, following=followed)
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/followers/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([member['user']['username'] for member in response.data], ['fan'])

    def test_posts_can_be_filtered_by_author(self):
        from .models import Post

        owner = User.objects.create_user(username='post-owner', password='password')
        other = User.objects.create_user(username='other-author', password='password')
        Profile.objects.create(user=owner)
        Profile.objects.create(user=other)
        Post.objects.create(author=owner, content='My post')
        Post.objects.create(author=other, content='Another post')
        self.client.force_authenticate(user=owner)

        response = self.client.get('/api/posts/', {'author': owner.username})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([post['content'] for post in response.data], ['My post'])
