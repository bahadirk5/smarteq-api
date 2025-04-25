from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import Department, Role, User

class Command(BaseCommand):
    help = 'Seeds initial departments, roles and users data for Smarteq project'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating initial data...'))
        
        # Create departments
        departments = {
            'management': Department.objects.create(
                name="Yönetim",
                description="Şirket yönetimi ve stratejik karar alma"
            ),
            'software': Department.objects.create(
                name="Yazılım Geliştirme",
                description="Yazılım çözümleri geliştirme ve bakım"
            ),
            'hardware': Department.objects.create(
                name="Donanım Operasyonları",
                description="Cihaz üretimi ve donanım operasyonları"
            ),
            'technical': Department.objects.create(
                name="Teknik Operasyonlar",
                description="Teknik destek ve arıza çözümü"
            ),
            'dealer': Department.objects.create(
                name="Bayi Ağı Yönetimi",
                description="Bayi ilişkileri ve kurum yönetimi"
            ),
        }
        
        self.stdout.write(self.style.SUCCESS('Created departments'))
        
        # Create roles
        roles = {
            'system_admin': Role.objects.create(
                name="Sistem Yöneticisi",
                description="Tüm sisteme tam erişim",
                department=departments['management']
            ),
            'software_expert': Role.objects.create(
                name="Yazılım Uzmanı",
                description="Yazılım geliştirme ve bakım",
                department=departments['software']
            ),
            'hardware_expert': Role.objects.create(
                name="Donanım Uzmanı",
                description="Cihaz üretimi ve donanım operasyonları",
                department=departments['hardware']
            ),
            'tech_support': Role.objects.create(
                name="Teknik Destek Uzmanı",
                description="Teknik destek ve arıza çözümü",
                department=departments['technical']
            ),
            'senior_tech': Role.objects.create(
                name="Kıdemli Teknik Uzman",
                description="İleri seviye teknik operasyonlar",
                department=departments['technical']
            ),
            'dealer_rep': Role.objects.create(
                name="Bayi Temsilcisi",
                description="Bayi ilişkileri yönetimi",
                department=departments['dealer']
            ),
            'institution_manager': Role.objects.create(
                name="Kurum Yöneticisi",
                description="Kurum cihazlarının yönetimi",
                department=departments['dealer']
            ),
            'senior_institution_manager': Role.objects.create(
                name="Kıdemli Kurum Yöneticisi",
                description="Gelişmiş kurum yönetimi ve raporlama",
                department=departments['dealer']
            ),
            'institution_auth': Role.objects.create(
                name="Kurum Yetkilisi",
                description="Sınırlı erişimle kurum cihazlarını izleme",
                department=departments['dealer']
            ),
        }
        
        self.stdout.write(self.style.SUCCESS('Created roles'))
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@smarteq.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                department=departments['management'],
                role=roles['system_admin']
            )
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / admin123'))
        
        # Create example users for each role
        example_users = [
            {
                'username': 'software1',
                'email': 'software@smarteq.com',
                'password': 'software123',
                'first_name': 'Ahmet',
                'last_name': 'Yazılım',
                'department': departments['software'],
                'role': roles['software_expert']
            },
            {
                'username': 'hardware1',
                'email': 'hardware@smarteq.com',
                'password': 'hardware123',
                'first_name': 'Mehmet',
                'last_name': 'Donanım',
                'department': departments['hardware'],
                'role': roles['hardware_expert']
            },
            {
                'username': 'techsupport1',
                'email': 'techsupport@smarteq.com',
                'password': 'techsupport123',
                'first_name': 'Zehra',
                'last_name': 'Destek',
                'department': departments['technical'],
                'role': roles['tech_support']
            },
            {
                'username': 'senior_tech1',
                'email': 'seniortech@smarteq.com',
                'password': 'seniortech123',
                'first_name': 'Ali',
                'last_name': 'Kıdemli',
                'department': departments['technical'],
                'role': roles['senior_tech']
            },
            {
                'username': 'dealer1',
                'email': 'dealer@smarteq.com',
                'password': 'dealer123',
                'first_name': 'Fatma',
                'last_name': 'Bayi',
                'department': departments['dealer'],
                'role': roles['dealer_rep']
            },
            {
                'username': 'institution1',
                'email': 'institution@smarteq.com',
                'password': 'institution123',
                'first_name': 'Mustafa',
                'last_name': 'Kurum',
                'department': departments['dealer'],
                'role': roles['institution_manager']
            },
            {
                'username': 'senior_institution1',
                'email': 'seniorinstitution@smarteq.com',
                'password': 'seniorinstitution123',
                'first_name': 'Ayşe',
                'last_name': 'Kıdemli',
                'department': departments['dealer'],
                'role': roles['senior_institution_manager']
            }
        ]
        
        for user_data in example_users:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    department=user_data['department'],
                    role=user_data['role']
                )
        
        self.stdout.write(self.style.SUCCESS('Created example users'))
        self.stdout.write(self.style.SUCCESS('Seed data creation completed successfully!'))