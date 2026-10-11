from django.core.management.base import BaseCommand
from core.management_seed import seed
class Command(BaseCommand):
    help='Create demo Athlenet data'
    def handle(self,*args,**kwargs): seed(); self.stdout.write(self.style.SUCCESS('Demo data created. Password for demo users: Athlenet@123'))
