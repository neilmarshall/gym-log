import sys
from app import create_app, db
from app.models.user import User

try:
    username, new_password = sys.argv[1:3]
    if username and new_password:
        app = create_app()
        app_context = app.app_context()
        app_context.push()

        user = User.query.filter_by(username=username).first()
        if user:
            user.set_password(new_password)
            db.session.commit()
        else:
            print("username not recognised")
    else:
        raise ValueError()
except ValueError:
    print("program requires non-null [username] and [password] to be specified")

