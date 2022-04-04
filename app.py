import os
import sys
from flask import Flask, request, abort, json, jsonify, render_template, url_for, flash, redirect
from flask_cors import CORS
import traceback
from models import SpatialConstants, setup_db, SampleLocation,  User, Pet, db, db_drop_and_create_all, SQLAlchemy
from forms import NewLocationForm, RegistrationForm, LoginForm
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt


from flask_login import LoginManager
from flask_login import login_user, current_user, logout_user, login_required

# create the app
def create_app(test_config=None):
    app = Flask(__name__)
    #configure the app
    setup_db(app)
    CORS(app)
     
    """ uncomment at the first time running the app """
    db_drop_and_create_all()
    
    csrf = CSRFProtect(app)
    
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY
    csrf.init_app(app)
    bcrypt= Bcrypt(app)
    login_manager= LoginManager(app)
    login_manager.init_app(app)
    login_manager.login_view='login' 
    login_manager.login_message_category='info'
    
    @login_manager.user_loader
    def load_user(user_id):
       return User.query.get(int(user_id))
   
   
    #templates 
    #define the basic route and its corresponding request handler
    @app.route('/', methods=['GET'])
    #modify the main method to return the rendered template
    def home():
        return render_template(
            'index.html')
    
    #register page
    @app.route('/register', methods=['GET', 'POST'])
    def register ():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user= User(username=form.username.data,
            email=form.email.data, 
            password= hashed_password)
            #about_me=form.about_me.data, 
            #area=form.lookup_address.data, 
            #pet_lostorfound=form.pet_lostorfound.data,
            #geom=SpatialConstants.point_representation(
                #form.coord_latitude.data,form.coord_longitude.data)
                
            db.session.add(user)
            db.session.commit()
            flash(f'Account created for {form.username.data}. Pease log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title= 'Register', 
          form= form)
          #map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!'))
          
    #login page
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        form = LoginForm()
        if form.validate_on_submit():
            user= User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return  redirect(url_for('index'))
            else:    
               flash('Login Unsuccessful. Please check email and password.', 'danger')     
        return render_template('login.html', title= 'Log In', form= form)
    
          
    ''' #add method 'register' to render the register page once a request comes to /register  
    @app.route('/register')
    def register():
        return render_template(
            'register.html')    
    #create method registeR, add a route /api/register
    @app.route('/api/registeR', methods=['POST'])
    def registeR ():
        user_name = request.form['inputName']
        user_email = request.form['inputEmail']
        user_password = request.form['inputPassword']      
        # validate the received values
        if user_name and user_email and user_password:
            return json.dumps({'html':'<span>Please submit</span>'})
        else:
            return json.dumps({'html':'<span>Please enter the required fields</span>'}) '''
       
    @app.route("/map", methods=['GET'])
    @login_required
    #change def home to map
    def map ():
        return render_template(
            'map.html', 
            map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!')
        )    
        
    @app.route("/new-location", methods=['GET', 'POST'])
    def new_location():
         form = NewLocationForm()

         if form.validate_on_submit():            
             latitude = float(form.coord_latitude.data)
             longitude = float(form.coord_longitude.data)
             description = form.description.data

             location = SampleLocation(
                 description=description,
                 geom=SampleLocation.point_representation(latitude=latitude, longitude=longitude)
             )   
             location.insert()

             flash(f'New location created!', 'success')
             return redirect(url_for('home'))

         return render_template(
             'new-location.html',
             form=form,
             map_key=os.getenv('GOOGLE_MAPS_API_KEY', 'GOOGLE_MAPS_API_KEY_WAS_NOT_SET?!')
         ) 

    
    @app.route("/api/store_item")
    def store_item():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            description = request.args.get('description')

            location = SampleLocation(
                description=description,
                geom=SampleLocation.point_representation(latitude=latitude, longitude=longitude)
            )   
            location.insert()

            return jsonify(
                {
                    "success": True,
                    "location": location.to_dict()
                }
            ), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.route("/api/get_items_in_radius")
    def get_items_in_radius():
        try:
            latitude = float(request.args.get('lat'))
            longitude = float(request.args.get('lng'))
            radius = int(request.args.get('radius'))
            
            locations = SampleLocation.get_items_within_radius(latitude, longitude, radius)
            return jsonify(
                {
                    "success": True,
                    "results": locations
                }
            ), 200
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            app.logger.error(traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2))
            abort(500)

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "server error"
        }), 500

    return app

app = create_app()
#check if the executed file is the main program and run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(host='127.0.0.1',port=port,debug=True)