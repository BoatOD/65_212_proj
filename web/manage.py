from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import app, db
from app.models.authuser import AuthUser
from app.models.authuser import AuthUser
from app.models.review import Review
from app.models.problems import problems

cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

@cli.command("seed_db")
def seed_db():
    db.session.add(
        AuthUser(email="Boat@gmail.com", name='LทพZA-007',password=generate_password_hash('12',method='sha256'), avatar_url='user.png'))
    db.session.add(
        Review(name='LทพZA-007', 
               message='บรรยากาศดีมากครัช', 
               email='Boat@gmail.com', 
               date='20/2/2566 16:56:47', 
               avatar_url='user.png',
               lat=18.8061652,
               lng=98.951333,
               picname='angk.jpeg'))
    db.session.add(
        problems(name='LทพZA-007', 
                 message='ทางเดินหน้าตึกวิทย์ 30ปี แย่มั๊ก', 
                 email='Boat@gmail.com', 
                 date='20/2/2566 16:56:47', 
                 avatar_url='user.png',
                 lat=18.8013133,
                 lng=98.9523268,
                 picname='StartNotify.jpg'))
    db.session.commit()

if __name__ == "__main__":
    cli()