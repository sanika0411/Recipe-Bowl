from flask import Flask, request, render_template,jsonify, redirect, url_for, flash, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
from gtts import gTTS
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# Read data from CSV file into a DataFrame
recipe_df = pd.read_csv('recipes.csv')

# Create a TfidfVectorizer to convert ingredients to a TF-IDF representation
vectorizer = TfidfVectorizer()
ingredients_matrix = vectorizer.fit_transform(recipe_df['ingredients'].apply(lambda x: ', '.join(x.split(', '))))

def recommend_recipe(available_ingredients, recipe, vectorizer):
    # Convert available ingredients to a TF-IDF representation
    input_vector = vectorizer.transform([' '.join(available_ingredients)])

    # Calculate cosine similarity between input and all recipes
    cosine_similarities = linear_kernel(input_vector, ingredients_matrix).flatten()

    # Get the index of the most similar recipe
    recommended_index = cosine_similarities.argmax()

    # Get the recommended recipe
    recommended_recipe = recipe.iloc[recommended_index]

    return recommended_recipe


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/recipe'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class SignUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(12), nullable=True, unique=True)
    password = db.Column(db.String(20), nullable=False)  # Store passwords as plain text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username or email already exists
        if SignUp.query.filter((SignUp.username == username) | (SignUp.email == email)).first():
            flash('Username or email already exists. Please choose a different one.', 'danger')
        else:
            # Save user data to the database (without hashing the password)
            new_user = SignUp(name=name, phone=phone, email=email, username=username, password=password)
            db.session.add(new_user)

            try:
                db.session.commit()
                flash('Registration successful!', 'success')
                return redirect(url_for('index'))  # Redirect to index after successful signup
            except Exception as e:
                db.session.rollback()
                flash('Error during registration. Please try again.', 'danger')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if the user is already logged in
    if 'user_id' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = SignUp.query.filter_by(username=username, password=password).first()

        if user:
            # Set the user information in the session
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Incorrect username or password
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if user_id:
        user = SignUp.query.get(user_id)
        if user:
            return render_template('dashboard.html', user=user)

    flash('User not found', 'danger')
    return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout', methods=['POST'])
def logout():
    # Clear the user information from the session
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/recommendation', methods=['GET'])
def get_recommendation():
    try:
        ingredients_input = request.args.get('ingredients', '')
        available_ingredients = ingredients_input.split(',')

        if not available_ingredients:
            return jsonify({'error': 'Please provide a list of ingredients.'}), 400

        recommended_recipe = recommend_recipe(available_ingredients, recipe_df, vectorizer)

        #Generate text for recommendation
        recommendation_text = f"The recommended recipe is {recommended_recipe['name']} with ingredients {recommended_recipe['ingredients']} and steps for this recipe is {recommended_recipe['steps']}."

        # Convert text to speech
        tts = gTTS(text=recommendation_text, lang='en')
        tts.save('recommendation.mp3')

        # Play the generated speech
        os.system('start recommendation.mp3')

        return render_template('recommendation.html', recommended_recipe=recommended_recipe)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

















# from flask import Flask, request, render_template, jsonify, redirect, url_for, flash, session
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import linear_kernel
# import pandas as pd
# from gtts import gTTS
# import os
# from flask_sqlalchemy import SQLAlchemy
# from flask_mail import Mail, Message
# import pyotp

# app = Flask(__name__)

# # Read data from CSV file into a DataFrame
# recipe_df = pd.read_csv('recipes.csv')

# # Create a TfidfVectorizer to convert ingredients to a TF-IDF representation
# vectorizer = TfidfVectorizer()
# ingredients_matrix = vectorizer.fit_transform(recipe_df['ingredients'].apply(lambda x: ', '.join(x.split(', '))))

# # Configure Flask-Mail
# app.config['MAIL_SERVER'] = 'smtp.example.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'your_email@example.com'
# app.config['MAIL_PASSWORD'] = 'your_email_password'
# app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'
# mail = Mail(app)

# # ... Existing code ...
# def recommend_recipe(available_ingredients, recipe, vectorizer):
#     # Convert available ingredients to a TF-IDF representation
#     input_vector = vectorizer.transform([' '.join(available_ingredients)])

#     # Calculate cosine similarity between input and all recipes
#     cosine_similarities = linear_kernel(input_vector, ingredients_matrix).flatten()

#     # Get the index of the most similar recipe
#     recommended_index = cosine_similarities.argmax()

#     # Get the recommended recipe
#     recommended_recipe = recipe.iloc[recommended_index]

#     return recommended_recipe

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/recipe'
# app.config['SECRET_KEY'] = 'your_secret_key'
# db = SQLAlchemy(app)

# class SignUp(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), nullable=False)
#     phone = db.Column(db.String(12), nullable=False)
#     email = db.Column(db.String(50), nullable=False, unique=True)
#     username = db.Column(db.String(12), nullable=True, unique=True)
#     password = db.Column(db.String(20), nullable=False)  # Store passwords as plain text

# @app.route('/')
# def index():
#     return render_template('index.html')

# # Define the User, Recipe, and LikedRecipes models here (as shown in the previous response)

# # ... Existing code ...

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         phone = request.form.get('phone')
#         email = request.form.get('email')
#         username = request.form.get('username')
#         password = request.form.get('password')

#         # Check if the username or email already exists
#         if SignUp.query.filter((SignUp.username == username) | (SignUp.email == email)).first():
#             flash('Username or email already exists. Please choose a different one.', 'danger')
#         else:
#             # Generate OTP
#             otp = pyotp.TOTP(pyotp.random_base32())
#             otp_code = otp.now()

#             # Send OTP to the user's email
#             send_otp_email(email, otp_code)

#             # Store the OTP code in the session for verification
#             session['otp_code'] = otp_code

#             # Render a page to enter the OTP
#             return render_template('otp_verification.html')

#     return render_template('signup.html')

# def send_otp_email(email, otp_code):
#     subject = 'Your OTP for Signup'
#     body = f'Your OTP for signup is: {otp_code}'
#     message = Message(subject, recipients=[email], body=body)
#     mail.send(message)

# @app.route('/verify_otp', methods=['POST'])
# def verify_otp():
#     if request.method == 'POST':
#         user_entered_otp = request.form.get('otp')

#         # Retrieve the stored OTP from the session
#         stored_otp = session.get('otp_code')

#         # Compare user-entered OTP with the stored OTP
#         if user_entered_otp == stored_otp:
#             # OTP is correct, proceed with user registration
#             # Clear the session entry for OTP
#             session.pop('otp_code', None)

#             # Save user data to the database (without hashing the password)
#             new_user = SignUp(name=name, phone=phone, email=email, username=username, password=password)
#             db.session.add(new_user)

#             try:
#                 db.session.commit()
#                 flash('Registration successful!', 'success')
#                 return redirect(url_for('index'))  # Redirect to index after successful signup
#             except Exception as e:
#                 db.session.rollback()
#                 flash('Error during registration. Please try again.', 'danger')
#         else:
#             flash('Invalid OTP. Please try again.', 'danger')

#     return redirect(url_for('signup'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Check if the user is already logged in
#     if 'user_id' in session:
#         flash('You are already logged in.', 'info')
#         return redirect(url_for('dashboard'))

#     if request.method == 'POST':
#         username = request.form.get('username')
#         password = request.form.get('password')

#         user = SignUp.query.filter_by(username=username, password=password).first()

#         if user:
#             # Set the user information in the session
#             session['user_id'] = user.id
#             flash('Login successful!', 'success')
#             return redirect(url_for('dashboard'))
#         else:
#             # Incorrect username or password
#             flash('Invalid username or password. Please try again.', 'danger')

#     return render_template('login.html')

# @app.route('/dashboard')
# def dashboard():
#     # Dynamic user retrieval based on Flask-Login or session management
#     # This example assumes the user is stored in the session
#     user_id = session.get('user_id')
#     if user_id:
#         user = SignUp.query.get(user_id)
#         if user:
#             return render_template('dashboard.html', user=user)

#     flash('User not found', 'danger')
#     return redirect(url_for('login'))

# @app.route('/about')
# def about():
#     return render_template('about.html')


# @app.route('/logout', methods=['POST'])
# def logout():
#     # Clear the user information from the session
#     session.pop('user_id', None)
#     flash('You have been logged out.', 'info')
#     return redirect(url_for('index'))


# @app.route('/recommendation', methods=['GET'])
# def get_recommendation():
#     try:
#         ingredients_input = request.args.get('ingredients', '')
#         available_ingredients = ingredients_input.split(',')

#         if not available_ingredients:
#             return jsonify({'error': 'Please provide a list of ingredients.'}), 400

#         recommended_recipe = recommend_recipe(available_ingredients, recipe_df, vectorizer)

#         # #Generate text for recommendation
#         # recommendation_text = f"The recommended recipe is {recommended_recipe['name']} with ingredients {recommended_recipe['ingredients']} and steps for this recipe is {recommended_recipe['steps']}."

#         # # Convert text to speech
#         # tts = gTTS(text=recommendation_text, lang='en')
#         # tts.save('recommendation.mp3')

#         # # Play the generated speech
#         # os.system('start recommendation.mp3')

#         return render_template('recommendation.html', recommended_recipe=recommended_recipe)

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# # ... Existing code ...

# if __name__ == "__main__":
#     app.run(debug=True)
