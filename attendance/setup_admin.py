"""
Quick setup script to create an admin user for the attendance system.
Run this with: python setup_admin.py
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance.settings')
django.setup()

from django.contrib.auth.models import User

def create_admin():
    """Create a default admin user if one doesn't exist."""
    username = 'admin'
    password = 'admin123'
    email = 'admin@example.com'
    
    if User.objects.filter(username=username).exists():
        print(f"✓ Admin user '{username}' already exists!")
        print(f"  Username: {username}")
        print(f"  Password: (use existing password)")
    else:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✓ Admin user created successfully!")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"\n⚠️  IMPORTANT: Change this password in production!")
    
    print(f"\n🌐 Login at: http://localhost:8000/")
    print(f"📊 Dashboard: http://localhost:8000/dashboard")
    print(f"🔧 Django Admin: http://localhost:8000/admin")

if __name__ == '__main__':
    create_admin()
