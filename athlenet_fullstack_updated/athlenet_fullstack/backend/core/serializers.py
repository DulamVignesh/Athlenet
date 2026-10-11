from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

class UserMiniSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    role = serializers.CharField(source='profile.role', read_only=True)
    photo = serializers.SerializerMethodField()
    def get_name(self,obj): return obj.get_full_name() or obj.username
    def get_photo(self,obj):
        try: return obj.profile.photo.url if obj.profile.photo else None
        except: return None
    class Meta:
        model=User; fields=['id','username','name','role','photo']

class MemberSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    sport = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    def get_sport(self,obj):
        try: return obj.player_details.sport
        except: pass
        try: return obj.coach_details.sport
        except: return ''
    def get_followers_count(self,obj): return obj.user.followers.count()
    def get_is_following(self,obj):
        req=self.context.get('request')
        return bool(req and req.user.is_authenticated and obj.user.followers.filter(follower=req.user).exists())
    class Meta:
        model=Profile; fields=['user','role','location','bio','photo','sport','followers_count','is_following']

class AchievementSerializer(serializers.ModelSerializer):
    class Meta: model=Achievement; fields='__all__'; read_only_fields=['player']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    email = serializers.SerializerMethodField()
    coach_details = serializers.SerializerMethodField()
    player_details = serializers.SerializerMethodField()
    pincode = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField(); following_count = serializers.SerializerMethodField()
    def get_pincode(self,obj):
        req=self.context.get('request')
        return obj.pincode if req and req.user.is_authenticated and req.user.pk==obj.user_id else ''
    def get_coach_details(self,obj):
        try:
            d=obj.coach_details
            return {'age':d.age,'gender':d.gender,'sport':d.sport,'experience':d.experience,'academy':d.academy,'verified':d.verified}
        except: return None
    def get_player_details(self,obj):
        try:
            d=obj.player_details
            return {'age':d.age,'sport':d.sport,'level':d.level,'district':d.district,'state':d.state,'experience':d.experience,'ranking':d.ranking,'statistics':d.statistics,'achievements':AchievementSerializer(d.achievements.all(),many=True).data}
        except: return None
    def get_followers_count(self,obj): return obj.user.followers.count()
    def get_following_count(self,obj): return obj.user.following.count()
    def get_email(self,obj):
        req=self.context.get('request')
        return obj.user.email if req and req.user.is_authenticated and req.user.pk==obj.user_id else ''
    class Meta: model=Profile; fields=['user','role','email','phone','location','pincode','bio','photo','coach_details','player_details','followers_count','following_count']

class OpportunitySerializer(serializers.ModelSerializer):
    coach_name=serializers.SerializerMethodField(); coach_verified=serializers.SerializerMethodField(); application_count=serializers.IntegerField(source='applications.count',read_only=True)
    applied=serializers.SerializerMethodField()
    def get_coach_name(self,obj): return obj.coach.profile.user.get_full_name() or obj.coach.profile.user.username
    def get_coach_verified(self,obj): return obj.coach.verified
    def get_applied(self,obj):
        req=self.context.get('request');
        if not req or not req.user.is_authenticated: return False
        try: return OpportunityApplication.objects.filter(opportunity=obj,player=req.user.profile.player_details).exists()
        except: return False
    class Meta: model=Opportunity; fields='__all__'; read_only_fields=['coach','created_at','active']

class PostSerializer(serializers.ModelSerializer):
    author=UserMiniSerializer(read_only=True); likes_count=serializers.IntegerField(source='likes.count',read_only=True); comments_count=serializers.IntegerField(source='comments.count',read_only=True); liked=serializers.SerializerMethodField()
    def get_liked(self,obj):
        req=self.context.get('request'); return bool(req and req.user.is_authenticated and obj.likes.filter(user=req.user).exists())
    class Meta: model=Post; fields='__all__'; read_only_fields=['author','created_at','updated_at']

class CommentSerializer(serializers.ModelSerializer):
    user=UserMiniSerializer(read_only=True)
    class Meta: model=Comment; fields=['id','post','user','text','created_at']; read_only_fields=['user','created_at']

class NewsSerializer(serializers.ModelSerializer):
    class Meta: model=News; fields='__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta: model=Notification; fields='__all__'

class MessageSerializer(serializers.ModelSerializer):
    sender=UserMiniSerializer(read_only=True)
    class Meta: model=Message; fields=['id','sender','text','created_at','read']; read_only_fields=['sender','created_at']
