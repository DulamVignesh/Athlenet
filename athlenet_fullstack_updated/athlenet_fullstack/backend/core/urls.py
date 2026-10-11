from django.urls import path
from .views import *
urlpatterns=[
 path('auth/register/',RegisterView.as_view()),path('auth/login/',LoginView.as_view()),path('me/',MeView.as_view()),path('dashboard/',DashboardView.as_view()),
 path('opportunities/',OpportunityListCreateView.as_view()),path('opportunities/<int:pk>/',OpportunityDetailView.as_view()),
 path('posts/',PostListCreateView.as_view()),path('posts/<int:pk>/like/',LikeView.as_view()),path('posts/<int:pk>/comments/',CommentView.as_view()),
 path('users/',MembersView.as_view()),path('connections/',ConnectionsView.as_view()),path('users/<str:username>/follow/',FollowView.as_view()),path('users/<str:username>/',ProfileByUsernameView.as_view()),path('news/',NewsView.as_view()),
 path('notifications/',NotificationsView.as_view()),path('search/',SearchView.as_view()),path('conversations/',ConversationView.as_view()),path('conversations/<int:pk>/messages/',MessagesView.as_view()),
]
