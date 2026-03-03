from app.database import SessionLocal, engine
from app import models, auth
from sqlalchemy.orm import Session

def init_db():
    db = SessionLocal()
    try:
        # Check if admin exists
        user = db.query(models.User).filter(models.User.username == "admin").first()
        if not user:
            print("Creating admin user...")
            hashed_password = auth.get_password_hash("admin")
            db_user = models.User(
                username="admin", 
                hashed_password=hashed_password,
                role="admin"
            )
            db.add(db_user)
            db.commit()
            print("Admin user created (admin/admin).")
        else:
            print("Admin user already exists.")
            
        # Check if normal user exists
        user = db.query(models.User).filter(models.User.username == "user").first()
        if not user:
            print("Creating normal user...")
            hashed_password = auth.get_password_hash("user")
            db_user = models.User(
                username="user", 
                hashed_password=hashed_password,
                role="user"
            )
            db.add(db_user)
            db.commit()
            print("Normal user created (user/user).")
        else:
            print("Normal user already exists.")
            
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
