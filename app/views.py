from app import app
 
@app.route('/')
def home():
    return "Flask says 'Hello world!'"

@app.route('/phonebook')
def index():
    return app.send_static_file('phonebook.html')