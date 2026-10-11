from datetime import date
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import *

def valid_password(password):
    return (
        len(password) >= 8
        and any(char.islower() for char in password)
        and any(char.isupper() for char in password)
        and any(not char.isalnum() for char in password)
    )

def notify(user,msg,link=''):
    Notification.objects.create(user=user,message=msg,link=link)

def token_response(user):
    refresh=RefreshToken.for_user(user)
    return {'access':str(refresh.access_token),'refresh':str(refresh),'user':UserMiniSerializer(user).data}

class RegisterView(APIView):
    permission_classes=[AllowAny]
    @transaction.atomic
    def post(self,request):
        d=request.data; email=str(d.get('email','')).strip(); username=d.get('username') or email; password=d.get('password','')
        if not username or not password or not email: return Response({'detail':'Username, email and password are required.'},400)
        try: validate_email(email)
        except ValidationError: return Response({'detail':'Enter a valid email address.'},400)
        if not isinstance(password,str) or not valid_password(password): return Response({'detail':'Password must be at least 8 characters and include an uppercase letter, a lowercase letter, and a special character.'},400)
        phone=str(d.get('phone','')).strip(); phone_key=normalize_phone_number(phone)
        if phone and not phone_key: return Response({'detail':'Enter a valid 10-digit mobile number, optionally prefixed with +91.'},400)
        if User.objects.filter(username=username).exists() or User.objects.filter(email__iexact=email).exists(): return Response({'detail':'An account with this username/email already exists.'},400)
        if phone_key and any(normalize_phone_number(value)==phone_key for value in Profile.objects.exclude(phone='').values_list('phone',flat=True)): return Response({'detail':'An account with this mobile number already exists.'},400)
        role=d.get('role','user')
        if role not in ['user','player','coach']: return Response({'detail':'Invalid role.'},400)
        pincode=str(d.get('pincode','')).strip()
        try:
            Profile._meta.get_field('pincode').clean(pincode,None)
        except ValidationError as exc:
            return Response({'pincode':exc.messages},400)
        if not pincode: return Response({'pincode':['A 6-digit Indian PIN code is required.']},400)
        user=User.objects.create_user(username=username,email=d.get('email'),password=d.get('password'),first_name=d.get('first_name',''),last_name=d.get('last_name',''))
        user.email=email
        user.save(update_fields=['email'])
        try:
            with transaction.atomic():
                p=Profile.objects.create(user=user,role=role,phone=phone,phone_key=phone_key or None,location=d.get('location',''),pincode=pincode,bio=d.get('bio',''))
        except IntegrityError:
            user.delete()
            return Response({'detail':'An account with this mobile number already exists.'},400)
        if request.FILES.get('photo'): p.photo=request.FILES['photo']; p.save()
        if role=='coach':
            CoachProfile.objects.create(profile=p,age=d.get('age') or None,gender=d.get('gender',''),sport=d.get('sport',''),experience=d.get('experience') or 0,academy=d.get('academy',''),government_recognition=d.get('government_recognition',''),certificate=request.FILES.get('certificate'))
        elif role=='player':
            player=PlayerProfile.objects.create(profile=p,age=d.get('age') or None,sport=d.get('sport',''),level=d.get('level',''),district=d.get('district',''),state=d.get('state',''),experience=d.get('experience') or 0,ranking=d.get('ranking',''),statistics=d.get('statistics',''))
            if request.FILES.get('achievement_proof') and d.get('achievement_title'):
                Achievement.objects.create(player=player,title=d.get('achievement_title'),description=d.get('achievement_description',''),year=d.get('achievement_year') or None,proof=request.FILES['achievement_proof'])
        return Response(token_response(user),status=201)

class LoginView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        identity=request.data.get('username') or request.data.get('email'); password=request.data.get('password')
        user=authenticate(username=identity,password=password)
        if not user:
            try: user=User.objects.get(email=identity); user=authenticate(username=user.username,password=password)
            except User.DoesNotExist: user=None
        if not user: return Response({'detail':'Invalid credentials.'},401)
        return Response(token_response(user))

class MeView(APIView):
    def get(self,request): return Response(ProfileSerializer(request.user.profile,context={'request':request}).data)
    def patch(self,request):
        p=request.user.profile
        email=str(request.data.get('email',request.user.email)).strip()
        if 'email' in request.data:
            try: validate_email(email)
            except ValidationError: return Response({'detail':'Enter a valid email address.'},400)
            if User.objects.filter(email__iexact=email).exclude(pk=request.user.pk).exists(): return Response({'detail':'An account with this email address already exists.'},400)
        phone=str(request.data.get('phone',p.phone)).strip()
        phone_key=normalize_phone_number(phone)
        if 'phone' in request.data:
            if phone and not phone_key: return Response({'detail':'Enter a valid 10-digit mobile number, optionally prefixed with +91.'},400)
            if phone_key and any(normalize_phone_number(value)==phone_key for value in Profile.objects.exclude(pk=p.pk).exclude(phone='').values_list('phone',flat=True)): return Response({'detail':'An account with this mobile number already exists.'},400)
        if 'pincode' in request.data:
            pincode=str(request.data['pincode']).strip()
            try:
                Profile._meta.get_field('pincode').clean(pincode,None)
            except ValidationError as exc:
                return Response({'pincode':exc.messages},400)
            p.pincode=pincode
        for f in ['location','bio']:
            if f in request.data: setattr(p,f,request.data[f])
        if 'phone' in request.data:
            p.phone=phone
            p.phone_key=phone_key or None
        if 'email' in request.data:
            request.user.email=email
        if request.FILES.get('photo'): p.photo=request.FILES['photo']
        try:
            with transaction.atomic():
                p.save()
                if 'email' in request.data: request.user.save(update_fields=['email'])
        except IntegrityError:
            return Response({'detail':'An account with this mobile number already exists.'},400)
        return Response(ProfileSerializer(p,context={'request':request}).data)

class DashboardView(APIView):
    def get(self,request):
        loc=request.query_params.get('location') or request.user.profile.location
        pincode=request.user.profile.pincode
        opp=Opportunity.objects.filter(active=True,last_date__gte=date.today()).order_by('event_date')[:6]
        news=News.objects.filter(active=True)
        if pincode:
            news=news.filter(Q(pincode=pincode)|(Q(pincode='')&(Q(location__iexact=loc)|Q(location=''))))
        elif loc:
            news=news.filter(Q(location__iexact=loc)|Q(location=''))
        news=news.order_by('-published_at')[:6]
        posts=Post.objects.select_related('author').order_by('-created_at')[:10]
        return Response({'opportunities':OpportunitySerializer(opp,many=True,context={'request':request}).data,'news':NewsSerializer(news,many=True).data,'posts':PostSerializer(posts,many=True,context={'request':request}).data})

class OpportunityListCreateView(APIView):
    def get(self,request):
        qs=Opportunity.objects.filter(active=True).select_related('coach__profile__user').order_by('-created_at')
        for key in ['sport','location']:
            if request.query_params.get(key): qs=qs.filter(**{f'{key}__icontains':request.query_params[key]})
        q=request.query_params.get('q','').strip()
        if q:
            qs=qs.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(sport__icontains=q)|Q(location__icontains=q)|Q(eligibility__icontains=q))
        return Response(OpportunitySerializer(qs,many=True,context={'request':request}).data)
    def post(self,request):
        try: coach=request.user.profile.coach_details
        except: return Response({'detail':'Only coaches can create opportunities.'},403)
        s=OpportunitySerializer(data=request.data)
        if s.is_valid(): obj=s.save(coach=coach); return Response(OpportunitySerializer(obj,context={'request':request}).data,201)
        return Response(s.errors,400)

class OpportunityDetailView(APIView):
    def get(self,request,pk): return Response(OpportunitySerializer(get_object_or_404(Opportunity,pk=pk),context={'request':request}).data)
    def post(self,request,pk):
        obj=get_object_or_404(Opportunity,pk=pk)
        try: player=request.user.profile.player_details
        except: return Response({'detail':'Only players can apply.'},403)
        app,created=OpportunityApplication.objects.get_or_create(opportunity=obj,player=player,defaults={'message':request.data.get('message','')})
        if not created: return Response({'detail':'You already applied.'},400)
        notify(obj.coach.profile.user,f'{request.user.get_full_name() or request.user.username} applied for {obj.title}.')
        return Response({'detail':'Application submitted.'},201)

class PostListCreateView(APIView):
    def get(self,request):
        posts=Post.objects.select_related('author').order_by('-created_at')
        author=request.query_params.get('author','').strip()
        if author: posts=posts.filter(author__username=author)
        return Response(PostSerializer(posts,many=True,context={'request':request}).data)
    def post(self,request):
        s=PostSerializer(data=request.data)
        if s.is_valid(): obj=s.save(author=request.user); return Response(PostSerializer(obj,context={'request':request}).data,201)
        return Response(s.errors,400)

class LikeView(APIView):
    def post(self,request,pk):
        post=get_object_or_404(Post,pk=pk); like,created=Like.objects.get_or_create(post=post,user=request.user)
        if not created: like.delete(); return Response({'liked':False,'count':post.likes.count()})
        if post.author_id!=request.user.id: notify(post.author,f'{request.user.get_full_name() or request.user.username} liked your post.')
        return Response({'liked':True,'count':post.likes.count()})

class CommentView(APIView):
    def get(self,request,pk): return Response(CommentSerializer(Comment.objects.filter(post_id=pk).order_by('created_at'),many=True).data)
    def post(self,request,pk):
        s=CommentSerializer(data={'post':pk,'text':request.data.get('text','')})
        if s.is_valid(): obj=s.save(user=request.user); return Response(CommentSerializer(obj).data,201)
        return Response(s.errors,400)

class FollowView(APIView):
    def post(self,request,username):
        target=get_object_or_404(User,username=username)
        if target==request.user: return Response({'detail':'You cannot follow yourself.'},400)
        f,created=Follow.objects.get_or_create(follower=request.user,following=target)
        if not created: f.delete(); return Response({'following':False})
        notify(target,f'{request.user.get_full_name() or request.user.username} started following you.')
        return Response({'following':True})

class ProfileByUsernameView(APIView):
    def get(self,request,username):
        u=get_object_or_404(User,username=username); return Response(ProfileSerializer(u.profile,context={'request':request}).data)

class MembersView(APIView):
    def get(self,request):
        qs=Profile.objects.exclude(user=request.user).select_related('user','player_details','coach_details').order_by('-created_at')
        q=request.query_params.get('q','').strip()
        location=request.query_params.get('location','').strip()
        role=request.query_params.get('role','').strip()
        sport=request.query_params.get('sport','').strip()
        if q:
            qs=qs.filter(Q(user__username__icontains=q)|Q(user__first_name__icontains=q)|Q(user__last_name__icontains=q)|Q(bio__icontains=q)|Q(location__icontains=q))
        if location: qs=qs.filter(location__icontains=location)
        if role: qs=qs.filter(role=role)
        if sport: qs=qs.filter(Q(player_details__sport__icontains=sport)|Q(coach_details__sport__icontains=sport)).distinct()
        return Response(MemberSerializer(qs[:60],many=True,context={'request':request}).data)

class ConnectionsView(APIView):
    def get(self,request):
        qs=Profile.objects.filter(user__followers__follower=request.user).select_related('user','player_details','coach_details').distinct().order_by('user__username')
        return Response(MemberSerializer(qs,many=True,context={'request':request}).data)

class NewsView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        qs=News.objects.filter(active=True).order_by('-featured','-published_at')
        loc=request.query_params.get('location')
        pincode=request.query_params.get('pincode','').strip()
        if pincode: qs=qs.filter(Q(pincode=pincode)|Q(pincode=''))
        elif loc: qs=qs.filter(Q(location__iexact=loc)|Q(location=''))
        return Response(NewsSerializer(qs,many=True).data)

class NotificationsView(APIView):
    def get(self,request): return Response(NotificationSerializer(request.user.notifications.order_by('-created_at')[:50],many=True).data)
    def post(self,request): request.user.notifications.filter(read=False).update(read=True); return Response({'ok':True})

class SearchView(APIView):
    def get(self,request):
        q=request.query_params.get('q','').strip()
        if not q: return Response({'users':[],'opportunities':[],'news':[]})
        users=User.objects.filter(Q(username__icontains=q)|Q(first_name__icontains=q)|Q(last_name__icontains=q)).select_related('profile')[:15]
        opp=Opportunity.objects.filter(Q(title__icontains=q)|Q(description__icontains=q)|Q(sport__icontains=q)|Q(location__icontains=q),active=True)[:15]
        news=News.objects.filter(Q(title__icontains=q)|Q(summary__icontains=q)|Q(sport__icontains=q)|Q(location__icontains=q),active=True).order_by('-featured','-published_at')[:15]
        return Response({'users':UserMiniSerializer(users,many=True).data,'opportunities':OpportunitySerializer(opp,many=True,context={'request':request}).data,'news':NewsSerializer(news,many=True).data})

class ConversationView(APIView):
    def get(self,request):
        qs=Conversation.objects.filter(Q(user1=request.user)|Q(user2=request.user)).order_by('-updated_at')
        out=[]
        for c in qs:
            other=c.user2 if c.user1_id==request.user.id else c.user1
            out.append({'id':c.id,'other':UserMiniSerializer(other).data,'last_message':c.messages.order_by('-created_at').values_list('text',flat=True).first()})
        return Response(out)
    def post(self,request):
        other=get_object_or_404(User,id=request.data.get('user_id'))
        c=Conversation.objects.filter(Q(user1=request.user,user2=other)|Q(user1=other,user2=request.user)).first()
        if not c: c=Conversation.objects.create(user1=request.user,user2=other)
        return Response({'id':c.id},201)

class MessagesView(APIView):
    def get(self,request,pk):
        c=get_object_or_404(Conversation,pk=pk)
        if request.user not in [c.user1,c.user2]: return Response({'detail':'Forbidden'},403)
        return Response(MessageSerializer(c.messages.order_by('created_at'),many=True).data)
    def post(self,request,pk):
        c=get_object_or_404(Conversation,pk=pk)
        if request.user not in [c.user1,c.user2]: return Response({'detail':'Forbidden'},403)
        text=request.data.get('text','').strip()
        if not text: return Response({'detail':'Message is required.'},400)
        m=Message.objects.create(conversation=c,sender=request.user,text=text); c.save()
        other=c.user2 if c.user1_id==request.user.id else c.user1; notify(other,f'New message from {request.user.get_full_name() or request.user.username}.')
        return Response(MessageSerializer(m).data,201)
