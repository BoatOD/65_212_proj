from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import app, db
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
        AuthUser(email="flask@204212", name='สมชาย ทรงแบด',password=generate_password_hash('1234',method='sha256'), avatar_url='user.png'))
    db.session.add(
        Review(name='BoatOD', 
               message='LOL', 
               email='saoraza1234@gmail.com', 
               date='20/2/2566 16:56:47', 
               avatar_url='user.png',
               lat=18.806615,
               lng=98.952398,
               picname=''))
    db.session.add(
        problems(name='BoatOD', 
                 message='LOL', 
                 email='saoraza1234@gmail.com', 
                 date='20/2/2566 16:56:47', 
                 avatar_url='user.png',
                 lat=18.806615,
                 lng=98.952398,
                 picname=''))
    db.session.commit()

if __name__ == "__main__":
    cli()