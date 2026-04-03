#!/usr/bin/env python3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.user import User


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=generate_password_hash("Admin123!"),
                is_admin=True,
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Created admin user: admin / Admin123!")
        else:
            print("✓ Admin user already exists")
        print("✓ Database ready")


if __name__ == "__main__":
    main()
