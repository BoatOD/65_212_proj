from flask.cli import FlaskGroup


from app import app, db
from app.models.contact import Contact
from app.models.BlogEntry import BlogEntry


cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()




@cli.command("seed_db")
def seed_db():
    db.session.add(
        Contact(firstname='สมชาย', lastname='ทรงแบด', phone='081-111-1111'))
    db.session.add(
        BlogEntry(name='Tanachoh Vattanashusagul', message='LOL', email='saoraza1234@gmail.com', date='20/2/2566 16:56:47'))
    db.session.commit()




if __name__ == "__main__":
    cli()