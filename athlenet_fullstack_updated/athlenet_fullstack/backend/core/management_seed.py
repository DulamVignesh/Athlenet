from django.contrib.auth.models import User
from .models import Profile,CoachProfile,PlayerProfile,News,Opportunity
from datetime import date,timedelta

def seed():
    def user(username,email,role,first):
        u,created=User.objects.get_or_create(username=username,defaults={'email':email,'first_name':first})
        if created:u.set_password('Athlenet@123');u.save()
        p,_=Profile.objects.get_or_create(user=u,defaults={'role':role,'location':'Hyderabad','bio':f'{first} on Athlenet'})
        if role=='coach': CoachProfile.objects.get_or_create(profile=p,defaults={'sport':'Cricket','experience':8,'academy':'Athlenet Sports Academy','verified':True})
        if role=='player': PlayerProfile.objects.get_or_create(profile=p,defaults={'sport':'Athletics','level':'State','district':'Hyderabad','state':'Telangana','experience':5})
        return u
    c=user('demo_coach','coach@athlenet.local','coach','Ravi Coach'); user('demo_player','player@athlenet.local','player','Arjun Player'); user('demo_user','user@athlenet.local','user','Maya User')
    News.objects.get_or_create(title='Hyderabad Open Sports Trials',defaults={'summary':'Local athletes can watch this space for upcoming trials and camps.','location':'Hyderabad','sport':'Athletics','featured':True})
    News.objects.get_or_create(title='Telangana Sports Community Update',defaults={'summary':'Stay connected with verified opportunities and sports communities on Athlenet.','location':'Telangana','sport':'General'})
    coach=c.profile.coach_details
    Opportunity.objects.get_or_create(title='Hyderabad Cricket Selection Camp',defaults={'coach':coach,'description':'Open selection camp for emerging players. Bring ID and recent sports credentials.','sport':'Cricket','location':'Hyderabad','event_date':date.today()+timedelta(days=15),'last_date':date.today()+timedelta(days=10),'eligibility':'Age 16–24; district/state level preferred.','slots':30})
