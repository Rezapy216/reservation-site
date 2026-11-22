from django.core.management import BaseCommand
from faker import Faker

from accounts.models import User


class Command(BaseCommand):
    help = 'create and insert fake users'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.fake = Faker()
        
    def handle(self, *args, **kwargs):
        
        for i in range(1, 9):
            self.phone = f'0911111111{i}'

            user = User.objects.create_user(
                phone=self.phone,
                password='test12345',
                email=self.fake.email(),
                name = self.fake.name()
            )
            
            self.phone = f'091231231{i}9'

            user = User.objects.create_user(
                phone=self.phone,
                password='test12345',
                email=self.fake.email(),
                name = self.fake.name()
            )
            print(user)