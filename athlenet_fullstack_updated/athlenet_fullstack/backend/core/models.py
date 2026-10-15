from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator
import re

def normalize_phone_number(phone):
    digits = re.sub(r'\D', '', phone or '')
    if len(digits) == 12 and digits.startswith('91'):
        digits = digits[2:]
    return digits if len(digits) == 10 else ''

SPORTS = [('Cricket','Cricket'),('Football','Football'),('Athletics','Athletics'),('Basketball','Basketball'),('Kabaddi','Kabaddi'),('Badminton','Badminton'),('Volleyball','Volleyball'),('Tennis','Tennis'),('Other','Other')]
ROLES = [('user','General User'),('player','Player'),('coach','Coach')]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLES, default='user')
    phone = models.CharField(max_length=20, blank=True)
    phone_key = models.CharField(max_length=10, unique=True, blank=True, null=True, editable=False)
    location = models.CharField(max_length=120, blank=True)
    pincode = models.CharField(max_length=6, blank=True, validators=[RegexValidator(regex=r'^[1-9][0-9]{5}$', message='Enter a valid 6-digit Indian PIN code.')])
    bio = models.TextField(blank=True)
    interests = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.user.username} ({self.role})'

class CoachProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='coach_details')
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=30, blank=True)
    sport = models.CharField(max_length=50, choices=SPORTS, blank=True)
    experience = models.PositiveIntegerField(default=0)
    academy = models.CharField(max_length=150, blank=True)
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    government_recognition = models.CharField(max_length=150, blank=True)
    verified = models.BooleanField(default=False)

class PlayerProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='player_details')
    age = models.PositiveIntegerField(null=True, blank=True)
    sport = models.CharField(max_length=50, choices=SPORTS, blank=True)
    level = models.CharField(max_length=30, blank=True)
    district = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, blank=True)
    experience = models.PositiveIntegerField(default=0)
    ranking = models.CharField(max_length=80, blank=True)
    statistics = models.TextField(blank=True)

class Achievement(models.Model):
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    proof = models.FileField(upload_to='achievements/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Opportunity(models.Model):
    coach = models.ForeignKey(CoachProfile, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=180)
    description = models.TextField()
    sport = models.CharField(max_length=50, choices=SPORTS)
    location = models.CharField(max_length=150)
    event_date = models.DateField()
    last_date = models.DateField()
    eligibility = models.TextField(blank=True)
    slots = models.PositiveIntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

class OpportunityApplication(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='applications')
    player = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='pending', choices=[('pending','Pending'),('accepted','Accepted'),('rejected','Rejected')])
    applied_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('opportunity','player')

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    post_type = models.CharField(max_length=30, default='discussion', choices=[('achievement','Achievement'),('camp','Training Camp'),('trial','Trial'),('recruitment','Recruitment'),('discussion','Discussion'),('awareness','Awareness')])
    sport = models.CharField(max_length=50, blank=True, choices=SPORTS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('post','user')

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('follower','following')

class News(models.Model):
    title = models.CharField(max_length=220)
    summary = models.TextField()
    content = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    pincode = models.CharField(max_length=6, blank=True, validators=[RegexValidator(regex=r'^[1-9][0-9]{5}$', message='Enter a valid 6-digit Indian PIN code.')])
    sport = models.CharField(max_length=50, blank=True)
    source_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

class Conversation(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_started')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_received')
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: unique_together = ('user1','user2')

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)