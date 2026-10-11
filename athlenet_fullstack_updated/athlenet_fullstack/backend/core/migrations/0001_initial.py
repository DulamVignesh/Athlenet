from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

SPORTS = [('Cricket','Cricket'),('Football','Football'),('Athletics','Athletics'),('Basketball','Basketball'),('Kabaddi','Kabaddi'),('Badminton','Badminton'),('Volleyball','Volleyball'),('Tennis','Tennis'),('Other','Other')]
ROLES = [('user','General User'),('player','Player'),('coach','Coach')]

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='Profile',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('role',models.CharField(choices=ROLES,default='user',max_length=20)),
            ('phone',models.CharField(blank=True,max_length=20)),
            ('location',models.CharField(blank=True,max_length=120)),
            ('bio',models.TextField(blank=True)),
            ('photo',models.ImageField(blank=True,null=True,upload_to='profiles/')),
            ('created_at',models.DateTimeField(auto_now_add=True)),
            ('user',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='profile',to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='News',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('title',models.CharField(max_length=220)),('summary',models.TextField()),('content',models.TextField(blank=True)),
            ('location',models.CharField(blank=True,max_length=120)),('sport',models.CharField(blank=True,max_length=50)),
            ('source_url',models.URLField(blank=True)),('image',models.ImageField(blank=True,null=True,upload_to='news/')),
            ('published_at',models.DateTimeField(auto_now_add=True)),('featured',models.BooleanField(default=False)),('active',models.BooleanField(default=True)),
        ]),
        migrations.CreateModel(name='CoachProfile',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('age',models.PositiveIntegerField(blank=True,null=True)),('gender',models.CharField(blank=True,max_length=30)),
            ('sport',models.CharField(blank=True,choices=SPORTS,max_length=50)),('experience',models.PositiveIntegerField(default=0)),
            ('academy',models.CharField(blank=True,max_length=150)),('certificate',models.FileField(blank=True,null=True,upload_to='certificates/')),
            ('government_recognition',models.CharField(blank=True,max_length=150)),('verified',models.BooleanField(default=False)),
            ('profile',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='coach_details',to='core.profile')),
        ]),
        migrations.CreateModel(name='PlayerProfile',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('age',models.PositiveIntegerField(blank=True,null=True)),('sport',models.CharField(blank=True,choices=SPORTS,max_length=50)),
            ('level',models.CharField(blank=True,max_length=30)),('district',models.CharField(blank=True,max_length=80)),('state',models.CharField(blank=True,max_length=80)),
            ('experience',models.PositiveIntegerField(default=0)),('ranking',models.CharField(blank=True,max_length=80)),('statistics',models.TextField(blank=True)),
            ('profile',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='player_details',to='core.profile')),
        ]),
        migrations.CreateModel(name='Achievement',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('title',models.CharField(max_length=160)),('description',models.TextField(blank=True)),('year',models.PositiveIntegerField(blank=True,null=True)),
            ('proof',models.FileField(blank=True,null=True,upload_to='achievements/')),('created_at',models.DateTimeField(auto_now_add=True)),
            ('player',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='achievements',to='core.playerprofile')),
        ]),
        migrations.CreateModel(name='Opportunity',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('title',models.CharField(max_length=180)),('description',models.TextField()),('sport',models.CharField(choices=SPORTS,max_length=50)),
            ('location',models.CharField(max_length=150)),('event_date',models.DateField()),('last_date',models.DateField()),('eligibility',models.TextField(blank=True)),
            ('slots',models.PositiveIntegerField(default=20)),('created_at',models.DateTimeField(auto_now_add=True)),('active',models.BooleanField(default=True)),
            ('coach',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='opportunities',to='core.coachprofile')),
        ]),
        migrations.CreateModel(name='Post',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),
            ('content',models.TextField()),('image',models.ImageField(blank=True,null=True,upload_to='posts/')),
            ('post_type',models.CharField(choices=[('achievement','Achievement'),('camp','Training Camp'),('trial','Trial'),('recruitment','Recruitment'),('discussion','Discussion'),('awareness','Awareness')],default='discussion',max_length=30)),
            ('created_at',models.DateTimeField(auto_now_add=True)),('updated_at',models.DateTimeField(auto_now=True)),
            ('author',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='posts',to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Comment',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('text',models.TextField()),('created_at',models.DateTimeField(auto_now_add=True)),
            ('post',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='comments',to='core.post')),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Like',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),
            ('post',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='likes',to='core.post')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ],options={'unique_together':{('post','user')}}),
        migrations.CreateModel(name='Follow',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),
            ('follower',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='following',to=settings.AUTH_USER_MODEL)),
            ('following',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='followers',to=settings.AUTH_USER_MODEL)),
        ],options={'unique_together':{('follower','following')}}),
        migrations.CreateModel(name='Conversation',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('updated_at',models.DateTimeField(auto_now=True)),
            ('user1',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='conversations_started',to=settings.AUTH_USER_MODEL)),
            ('user2',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='conversations_received',to=settings.AUTH_USER_MODEL)),
        ],options={'unique_together':{('user1','user2')}}),
        migrations.CreateModel(name='Message',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('text',models.TextField()),('created_at',models.DateTimeField(auto_now_add=True)),('read',models.BooleanField(default=False)),
            ('conversation',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='messages',to='core.conversation')),
            ('sender',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Notification',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('message',models.CharField(max_length=255)),('link',models.CharField(blank=True,max_length=255)),('read',models.BooleanField(default=False)),('created_at',models.DateTimeField(auto_now_add=True)),
            ('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='notifications',to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='OpportunityApplication',fields=[
            ('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('message',models.TextField(blank=True)),('status',models.CharField(choices=[('pending','Pending'),('accepted','Accepted'),('rejected','Rejected')],default='pending',max_length=20)),('applied_at',models.DateTimeField(auto_now_add=True)),
            ('opportunity',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='applications',to='core.opportunity')),
            ('player',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='applications',to='core.playerprofile')),
        ],options={'unique_together':{('opportunity','player')}}),
    ]
