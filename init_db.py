from app import create_app, db, bcrypt
from app.models import Role, Permission, User

app = create_app()

def init_db():
    with app.app_context():
        # Create all tables if not exist
        db.create_all()
        
        # Create permissions
        permissions = {
            'view_sales': 'Access to Sales module',
            'view_inventory': 'Access to Inventory module',
            'view_reports': 'Access to Reports module',
            'admin': 'Full administrative access'
        }
        
        perm_objects = {}
        for name, desc in permissions.items():
            perm = Permission.query.filter_by(name=name).first()
            if not perm:
                perm = Permission(name=name, description=desc)
                db.session.add(perm)
                print(f"Created permission: {name}")
            else:
                print(f"Permission exists: {name}")
            perm_objects[name] = perm
            
        # Create roles
        roles = {
            'Admin': ['view_sales', 'view_inventory', 'view_reports', 'admin'],
            'Sales': ['view_sales', 'view_inventory']
        }
        
        role_objects = {}
        for name, perms in roles.items():
            role = Role.query.filter_by(name=name).first()
            if not role:
                role = Role(name=name)
                db.session.add(role)
                print(f"Created role: {name}")
            else:
                print(f"Role exists: {name}")
            
            # Update permissions
            # Need to commit first to ensure role and permissions have IDs if they are new
            # But here we are in same session.
            # However, role.permissions = [...] works on objects.
            
            current_perms = []
            for p_name in perms:
                if p_name in perm_objects:
                    current_perms.append(perm_objects[p_name])
            role.permissions = current_perms
            role_objects[name] = role
            
        db.session.commit()
        
        # Create users
        users = [
            ('admin', '123456', 'Admin'),
            ('sales', '123456', 'Sales')
        ]
        
        for username, password, role_name in users:
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username, active=True)
                user.password = password
                user.role = role_objects[role_name]
                db.session.add(user)
                print(f"Created user: {username}")
            else:
                print(f"User exists: {username}")
        
        db.session.commit()
        print("Database initialized with default roles and users.")

if __name__ == '__main__':
    init_db()
