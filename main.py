from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz2:abc123@localhost:3306/blogz2'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'abc123'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/index', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'GET':
        return render_template('newpost.html')
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title == '':
            return render_template('newpost.html', message="You Must Enter A Title", title=title, body=body)
        if body == '':
            return render_template('newpost.html', message1="You Must Enter A Post Body", title=title, body=body)
        else:
            new_post = Blog(title,body,owner)
            db.session.add(new_post)
            db.session.commit()
            ids = new_post.id
            owner_id = new_post.owner_id
            single_post = Blog.query.get(ids)
            user_id = request.args.get('user')
            owner_info = User.query.filter_by(id = user_id).first()
            users_posts = Blog.query.filter_by(owner_id=user_id).all()
            author = User.query.filter_by(id = owner_id).first()
            return render_template('blog_post1.html',single_post=single_post,user_id=user_id,author=author,owner_id = owner_id)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/newpost')
        if user == None:
            flash('Username does not exist', 'error')         
        else:
            flash('Password Is Not Correct', 'error')
        
    return render_template('login.html')


@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']


        existing_user = User.query.filter_by(email=email).first()
        if email == "":
            flash('One or more fields are invalid', 'error')
            return redirect('/signup')
        if password == "":
            flash('One or more fields are invalid', 'error')
            return redirect('/signup')
        if verify == "":
            flash('One or more fields are invalid', 'error')
            return redirect('/signup')   

        if password != verify:
            flash('Password and Verify Password Does Not Match', 'error')
            return redirect('/signup')

        if len(email) < 3:
            flash('Email Address Is Less than 3 Characters Long')
            return redirect('/signup')

        if len(password) < 3 and len(verify) < 3:
            flash('Passwords are less than 3 characters Long')
            return redirect('/signup')

        if existing_user:
            flash('User Already Exists', 'error')
            return redirect('/signup')

        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    posts = Blog.query.all()   
    post_id = request.args.get('id')
    user_id = request.args.get('user')
    users_posts = Blog.query.filter_by(owner_id=user_id).all()
    author_id = User.query.filter_by(id = user_id).first()
    owner_info = User.query.filter_by(id = user_id).first()
    ####blog_info = db.session.query(User).join(Blog).all()



    if post_id:
        single_post = Blog.query.get(post_id)
        #author = User.query.filter_by(id = post_id).first()
        author = User.query.filter_by(id = single_post.owner_id).first()
        print (author)
        print ('xxxxxxx')
        return render_template('blog_post.html',single_post=single_post, author=author, post_id=post_id)

    if user_id:
        users_posts = Blog.query.filter_by(owner_id=user_id).all()
        author = User.query.filter_by(id = user_id).first()
        return render_template('singleuser.html', users_posts=users_posts, post_id=post_id, author=author)

    return render_template('blog.html', posts = posts, author_id = author_id)

if __name__ == '__main__':
    app.run()