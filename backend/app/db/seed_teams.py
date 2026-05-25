from app.db.session import SessionLocal
from app.models.team import Team
from app.models.user import User
from app.core.auth.security import hash_password


TEAMS = {
    "sellf.ai": [
        "nick@sellf.ai",
        "nate@sellf.ai",
    ],
    "maguire-eminentdomain": [
        "Raymer@maguire-eminentdomain.com",
        "Rashid@maguire-eminentdomain.com",
        "Susan@maguire-eminentdomain.com",
        "Chrissie@maguire-eminentdomain.com",
    ],
}


def seed():
    db = SessionLocal()

    for slug, emails in TEAMS.items():
        team = db.query(Team).filter(Team.slug == slug).first()

        if not team:
            team = Team(
                name=slug,
                slug=slug
            )
            db.add(team)
            db.commit()
            db.refresh(team)

        for email in emails:
            normalized_email = email.lower()

            user = db.query(User).filter(
                User.email == normalized_email
            ).first()

            if not user:
                user = User(
                    email=normalized_email,
                    hashed_password=hash_password("ChangeMe123!"),
                    team_id=team.id
                )
                db.add(user)
            else:
                user.team_id = team.id

            db.commit()

    db.close()


if __name__ == "__main__":
    seed()
