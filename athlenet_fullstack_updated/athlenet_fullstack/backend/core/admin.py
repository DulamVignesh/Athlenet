from django.contrib import admin
from .models import *
for model in [Profile, CoachProfile, PlayerProfile, Achievement, Opportunity, OpportunityApplication, Post, Comment, Like, Follow, News, Conversation, Message, Notification]:
    admin.site.register(model)
