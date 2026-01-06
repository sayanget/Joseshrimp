import os
from app import create_app, db
from app.models import User, Role, Permission

def seed_admin():
    print("=" * 50)
    print("   Seed Admin User Tool")
    print("=" * 50)
    
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("[ERROR] DATABASE_URL environment variable not set.")
        return

    # Adapt Render/Supabase URL format
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        os.environ['DATABASE_URL'] = db_url

    app = create_app('production')
    
    with app.app_context():
        print("Connected to database.")
        
        # 1. Create Permissions
        permissions = ['admin', 'sales', 'inventory', 'reports']
        for name in permissions:
            perm = Permission.query.filter_by(name=name).first()
            if not perm:
                perm = Permission(name=name, description=f'{name} permission')
                db.session.add(perm)
                print(f"Created permission: {name}")
        db.session.commit()
        
        # 2. Create Roles
        admin_role = Role.query.filter_by(name='Administrator').first()
        if not admin_role:
            admin_role = Role(name='Administrator', description='System Administrator')
            # Assign all permissions
            perms = Permission.query.all()
            admin_role.permissions = perms
            db.session.add(admin_role)
            print("Created role: Administrator")
        
        user_role = Role.query.filter_by(name='User').first()
        if not user_role:
            user_role = Role(name='User', description='Standard User')
            # Assign limited permissions
            perms = Permission.query.filter(Permission.name.in_(['sales', 'inventory'])).all()
            user_role.permissions = perms
            db.session.add(user_role)
            print("Created role: User")
            
        db.session.commit()
        
        # 3. Create Admin User
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', role=admin_role, active=True)
            admin_user.password = 'admin123' # Default password
            db.session.add(admin_user)
            print("Created user: admin (password: admin123)")
        else:
            print("User 'admin' already exists.")
            # Optional: reset password if needed
            # admin_user.password = 'admin123'
            # print("Reset password for 'admin' to 'admin123'")
            
        db.session.commit()
        print("Done.")

if __name__ == "__main__":
    seed_admin()
