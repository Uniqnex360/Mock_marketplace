from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.authentication.models import MarketplaceCredential

class Command(BaseCommand):
    help = 'Creates initial superuser and test credentials'

    def handle(self, *args, **kwargs):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser created: admin/admin123'))

        # Create test user
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()

            # Create test credentials for Amazon
            amazon_cred = MarketplaceCredential.objects.create(
                user=test_user,
                marketplace='AMAZON_AE'
            )
            amazon_cred.generate_credentials()

            # Create test credentials for Noon
            noon_cred = MarketplaceCredential.objects.create(
                user=test_user,
                marketplace='NOON_AE'
            )
            noon_cred.generate_credentials()

            self.stdout.write(self.style.SUCCESS(f'Test user created: testuser/testpass123'))
            self.stdout.write(f'Amazon Client ID: {amazon_cred.client_id}')
            self.stdout.write(f'Amazon Client Secret: {amazon_cred.client_secret}')
            self.stdout.write(f'Noon Client ID: {noon_cred.client_id}')
            self.stdout.write(f'Noon Client Secret: {noon_cred.client_secret}')