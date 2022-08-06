from unicodedata import category
from flask import Flask, flash, request, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_mail import Message
from flask_login import UserMixin, login_user,LoginManager,login_required,logout_user,current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired,FileAllowed
from wtforms import StringField, PasswordField, RadioField, SubmitField, DateField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError, Email, EqualTo
from flask_bcrypt import Bcrypt
from datetime import timedelta
from serpapi import GoogleSearch

import sys
import urllib.request
from urllib.error import HTTPError
import certifi
import ssl


import os
import sqlite3

      



list_of_subcategories = {
    "Real Effort Tasks": ["Stereotyped tasks", "Other"],
    "Risk Elicitation Tasks": ["Risk aversion", "Loss aversion", "Higher order risk preferences", "Probability weighting", "Experimentally validated survey", "Other"],
    "Time Preferences Elicitation Tasks": ["Discount rates", "Self-control tasks", "Experimentally validated survey", "Other"],
    "Cognitive Reflection Tasks": ["IQ", "Raven test", "Experimentally validated survey", "Other"],
    "Ambiguity": ["Other"],
    "Minimal group paradigm In-group Out-group": ["Other"],
    "Social Norm elicitation tasks": ["Coordination", "Belief elicitation", "Rule-following", "Other"],
    "Altruism": ["Dictator game", "Charitable giving tasks", "Other"],
    "Belief elicitation tasks": ["Point estimates", "Whole distributions", "Confidence intervals", "Beliefs updating", "Overconfidence", "Second-order beliefs", "Other"],
    "Creativity elicitation tasks": ["Other"],
    "Implicit associations tasks": ["Other"],
    "Lying task": ["Die / coin games", "Send-receiver games", "Other"],
    "Trust tasks": ["Trust game", "Participation game", "Lost-wallet game", "Betrayal aversion tasks", "Experimentally validated survey", "Other"],
    "Cooperation": ["Conditional cooperation", "Experimentally validated survey", "Other"],
    "Competitiveness": ["Tournament entry", "Tournament performance", "Contest game", "Experimentally validated survey", "Other"],
    "Gender revelation methods": ["Voices", "Pictures", "Names", "Other"],
    "Emotional intelligence": ["Eyes in the mind test", "Other"],
    "Strategic sophistication": ["K-level thinking", "Beauty contest", "Other"],
    "Ideological and Political Preferences": ["Other"],
    "Bargaining": ["Multilateral Bargaining", "Bilateral Bargaining", "Other"],
    "Sabotage": ["Other"],
    "Willingness to Pay": ["Other"],
    "Voting": ["Other"]
}



app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'dfde280ba2455791628bb0b13ce0c676'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=2)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
mail = Mail(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    affiliation = db.Column(db.String(30), nullable=False)
    personal_website = db.Column(db.String(150), nullable=False)



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    search = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(300), nullable=False)
    sub_category = db.Column(db.String(300), nullable=False)
    is_author = db.Column(db.String(10), nullable=False)
    experimental_type = db.Column(db.String(100), nullable=False)
    experimental_game = db.Column(db.String(100), nullable=False)
    literature = db.Column(db.String(100), nullable=False)
    customized_tag = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    data = db.Column(db.String(100), nullable=False)
    journal = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(100), nullable=False)
    number_of_citations = db.Column(db.Integer, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class RegisterForm(FlaskForm):
    first_name = StringField(validators=[InputRequired(), Length(min=3, max=20)], render_kw = {"placeholder": "First Name"})
    last_name = StringField(validators=[InputRequired(), Length(min=3,max=20)], render_kw  = {"placeholder": "Last Name"})
    email = StringField(validators=[InputRequired(), Email(), Length(min=7, max=100)], render_kw = {"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=60)], render_kw = {"placeholder": "Password"})
    # affiliation = RadioField('Affiliation', choices=[('Student', 'Student'), ('Teacher', 'Teacher'), ('Admin', 'Admin')], default='Student')
    affiliation = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw = {"placeholder": "Affiliation"})
    personal_website = StringField(validators=[InputRequired(), Length(min=4, max=150)], render_kw = {"placeholder": "Personal Website"})
    submit = SubmitField('Register')

    def validate_email(self, email):
        useremail = User.query.filter_by(email=email.data).first()
        if useremail:
            raise ValidationError('That email is used. Please choose a different one.')



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(min=9, max=100)], render_kw = {'placeholder': 'Email'})
    password = PasswordField(validators=[InputRequired(), Length(min=7, max=60)], render_kw = {"placeholder": "Password"})
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    first_name = StringField(validators=[Length(min=3, max=20)], render_kw = {"placeholder": "First Name"})
    last_name = StringField(validators=[Length(min=3,max=20)], render_kw  = {"placeholder": "Last Name"})
    affiliation = StringField(validators=[Length(min=4, max=30)], render_kw = {"placeholder": "Affiliation"})
    personal_website = StringField(validators=[Length(min=4, max=150)], render_kw = {"placeholder": "Personal Website"})
    submit = SubmitField('Update')



class PostForm(FlaskForm):
    doi = StringField(validators=[InputRequired()], render_kw = {"placeholder": "DOI"})
    category = StringField(render_kw = {'placeholder': 'Category'})
    sub_category = StringField(render_kw = {'placeholder': 'Sub category'})
    # is_author = StringField()
    # experiment_type = StringField(render_kw = {'placeholder': 'Experiment Type'})
    # experimental_game = StringField(render_kw = {'placeholder': 'Experimental Game'})
    # literature = StringField(render_kw = {'placeholder': 'Literature'})
    customized_tag = StringField(render_kw = {'placeholder': 'Customized tag'})
    instructions = StringField(validators=[InputRequired()], render_kw = {'placeholder': 'Instructions'})
    code = StringField(render_kw = {'placeholder': 'Code'})
    data = StringField(render_kw = {'placeholder': 'Data'})
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    search = StringField()
    submit = SubmitField('Search')


@app.route('/')
def home():
    return render_template('home.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
    return render_template('login.html', form=form)



@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    # session.pop('current_user', None)
    return redirect(url_for('home'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        # check if email exists in database
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('That email is used. Please choose a different one.')
            return redirect(url_for('register'))
        else:
            new_user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data, password=hashed_password, affiliation=form.affiliation.data, personal_website=form.personal_website.data)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login')) # redirect to login page
    return render_template('register.html', form=form)



@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.affiliation = form.affiliation.data
        current_user.personal_website = form.personal_website.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.affiliation.data = current_user.affiliation
        form.personal_website.data = current_user.personal_website
    return render_template('profile.html', form=form)


@app.route('/contribute', methods=['GET', 'POST'])
@login_required
def contribute():
    form = PostForm()
    subcategory_list = []
    category_list = []
    if form.validate_on_submit():
        try:
            print(request.form['ad_pack_id'])
            category_list.append('Real Effort Tasks')
            subcategory_list.append(request.form['ad_pack_id'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_one'])
            category_list.append('Risk Elicitation Tasks')
            subcategory_list.append(request.form['ad_pack_id_one'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_two'])
            category_list.append('Time Preferences Elicitation Tasks')
            subcategory_list.append(request.form['ad_pack_id_two'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_three'])
            category_list.append('Cognitive Reflection Tasks')
            subcategory_list.append(request.form['ad_pack_id_three'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_four'])
            category_list.append('Ambiguity')
            subcategory_list.append(request.form['ad_pack_id_four'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_five'])
            category_list.append('Minimal group paradigm In-group Out-group')
            subcategory_list.append(request.form['ad_pack_id_five'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_six'])
            category_list.append('Social Norm elicitation tasks')
            subcategory_list.append(request.form['ad_pack_id_six'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_seven'])
            category_list.append('Altruism')
            subcategory_list.append(request.form['ad_pack_id_seven'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_eight'])
            category_list.append('Social Norm elicitation tasks')
            subcategory_list.append(request.form['ad_pack_id_eight'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_nine'])
            category_list.append('Creativity elicitation tasks')
            subcategory_list.append(request.form['ad_pack_id_nine'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_ten'])
            category_list.append('Implicit associations tasks')
            subcategory_list.append(request.form['ad_pack_id_ten'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_eleven'])
            category_list.append('Lying task')
            subcategory_list.append(request.form['ad_pack_id_eleven'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_12'])
            category_list.append('Trust tasks')
            subcategory_list.append(request.form['ad_pack_id_12'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_13'])
            category_list.append('Cooperation')
            subcategory_list.append(request.form['ad_pack_id_13'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_14'])
            category_list.append('Competitiveness')
            subcategory_list.append(request.form['ad_pack_id_14'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_15'])
            category_list.append('Gender revelation methods')
            subcategory_list.append(request.form['ad_pack_id_15'])
        except:
            pass

        try:
            print(request.form["ad_pack_16"])
            category_list.append('Emotional intelligence')
            subcategory_list.append(request.form['ad_pack_id_16'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_17'])
            category_list.append('Strategic sophistication')
            subcategory_list.append(request.form['ad_pack_id_17'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_18'])
            category_list.append('Ideological and Political Preferences')
            subcategory_list.append(request.form['ad_pack_id_18'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_19'])
            category_list.append('Bargaining')
            subcategory_list.append(request.form['ad_pack_id_19'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_20'])
            category_list.append('Sabotage')
            subcategory_list.append(request.form['ad_pack_id_20'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_21'])
            category_list.append('Willingness to Pay')
            subcategory_list.append(request.form['ad_pack_id_21'])
        except:
            pass

        try:
            print(request.form['ad_pack_id_22'])
            category_list.append('Voting')
            subcategory_list.append(request.form['ad_pack_id_22'])
        except:
            pass

        categories_string = ','.join(category_list)
        subcategories_string = ','.join(subcategory_list)
        # print(categories_string)
        # print(subcategories_string)


        #get info from doi

        BASE_URL = 'https://doi.org/'
        doi = form.doi.data

        # doi = '10.48550/arXiv.1706.03762'
        # doi = 'https://doi.org/10.14456/tresp.2016.8'

        # check if string doi has substring 'https://doi.org/'
        if doi.startswith('https://doi.org/'):
            url = doi
        else:# if not, add it
            url = BASE_URL + doi



        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/x-bibtex')

        bibDictionary = {}
        paper_title = ''
        paper_authors = ''
        published_journal = ''
        published_year = ''

        try:
            with urllib.request.urlopen(req, context=ssl.create_default_context(cafile=certifi.where())) as f:
                bibtex = f.read().decode()
                bibList = bibtex.split('\n')
                for line in bibList:
                    if 'title' in line:
                        bibDictionary['title'] = line.split('=')[1].strip()
                        bibDictionary['title'] = bibDictionary['title'].replace('{', '').replace('}', '')
                        bibDictionary['title'] = bibDictionary['title'].rstrip(',')
                        bibDictionary['title'] = bibDictionary['title'].rstrip(' ').lstrip(' ')
                        paper_title = bibDictionary['title']
                    elif 'author' in line:
                        bibDictionary['author'] = line.split('=')[1].strip()
                        bibDictionary['author'] = bibDictionary['author'].replace('{', '').replace('}', '')
                        bibDictionary['author'] = bibDictionary['author'].rstrip(',')
                        bibDictionary['author'] = bibDictionary['author'].rstrip(' ').lstrip(' ')
                        paper_authors = bibDictionary['author']
                    elif 'journal' in line:
                        bibDictionary['journal'] = line.split('=')[1].strip()
                        bibDictionary['journal'] = bibDictionary['journal'].replace('{', '').replace('}', '')
                        bibDictionary['journal'] = bibDictionary['journal'].rstrip(',')
                        bibDictionary['journal'] = bibDictionary['journal'].rstrip(' ').lstrip(' ')
                        published_journal = bibDictionary['journal']
                    elif 'year' in line:
                        bibDictionary['year'] = line.split('=')[1].strip()
                        bibDictionary['year'] = bibDictionary['year'].replace('{', '').replace('}', '')
                        bibDictionary['year'] = bibDictionary['year'].rstrip(',')
                        bibDictionary['year'] = bibDictionary['year'].rstrip(' ').lstrip(' ')
                        published_year = bibDictionary['year']
        
        except:
            print('DOI not found.')

        citations = 0
        
        # get number of citations
        if paper_title != '':
            params = {
                "api_key": "3227310ff609141326c949e18f3985019c56ebe55a83a35fb97dbeceb4e115df",
                "engine": "google_scholar",
                "q": paper_title,
                "hl": "en"
            }

            citations = 0
            try:
                search = GoogleSearch(params)
                google_results = search.get_dict()
                citations = google_results['organic_results'][0]['inline_links']['cited_by']['total']
            except:
                citations = 0
        
        is_author = 'no'
        is_author = request.form['you_author']



        check_if_exists = Post.query.filter_by(doi=doi).first()
        if check_if_exists is not None:
            print('DOI already exists.')
            return redirect(url_for('profile'))
        else:
            print('DOI does not exist.')
            # Create a new post        
            new_post = Post(title=paper_title, doi=form.doi.data, author=paper_authors, search=paper_title + ' ' + paper_authors + ' ' + published_year + ' ' + form.customized_tag.data,
                category=categories_string, sub_category=subcategories_string, is_author=is_author, experimental_type=request.form['ex_type'], 
                experimental_game=request.form['game_type'], literature=request.form['literature'],
                customized_tag=form.customized_tag.data, instructions=form.instructions.data, code=form.code.data, data=form.data.data,
                number_of_citations=citations, journal=published_journal, year=published_year, user_id = current_user.id)
            db.session.add(new_post)
            db.session.commit()
            print('post added')
            flash('Your post has been created!', 'success')
            return redirect(url_for('home'))
        
    print(form.errors)
    return render_template('contribute.html', form=form)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    print(form.errors)
    if form.validate_on_submit() and request.method == 'POST':
        search = form.search.data
        print(search)
        posts = Post.query.filter(Post.search.contains(search)).order_by(Post.number_of_citations.desc()).all()
        if search != '':
            return render_template('search_results.html', posts=posts)
    return render_template('search.html', form=form)



# route to display posts by category
@app.route('/category/<category>')
def category(category):
    if category == "all":
        posts = Post.query.order_by(Post.number_of_citations.desc()).all()
        return render_template('all_posts.html', posts=posts)
    else:
        print(category)
        # posts = Post.query.filter_by(category=category).all()
        return render_template('subcategories.html', category=category, subcategory_list=list_of_subcategories[category])
        # order posts by number of citations


#route to display posts by subcategory
@app.route('/subcategory/<subcategory>')
def subcategory(subcategory):
    print(subcategory)
    # posts that contain subcategory in their subcategory list
    posts = Post.query.filter(Post.sub_category.contains(subcategory)).order_by(Post.number_of_citations.desc()).all()
    return render_template('posts.html', posts=posts, subcategory=subcategory)


# route display a post by id
@app.route('/post/<id>')
def post(id):
    post = Post.query.filter_by(id=id).first()
    return render_template('post_details.html', post=post)

        
 
if __name__ == '__main__':
    app.run(debug=True)
