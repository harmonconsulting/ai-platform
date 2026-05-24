from app.db.session import SessionLocal
from app.models.user import User


def seed():
    db = SessionLocal()

    user = db.query(User).filter(User.id == 1).first()

    if not user:
        user = User(
            id=1,
            email="dev@local",
            hashed_password="dev"  # placeholder for dev only
        )
        db.add(user)
        db.commit()

    db.close()


if __name__ == "__main__":
    seed()
