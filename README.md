# Set up GEW-LTI in Ubuntu server

1. Make sure python 2.7  and virtualenv are installed. 

To check if they're installed:
* $ python -V
* $ virtualenv —version
* if virtualenv is not installed:
* install pip then pip install virtualenv

2. Create virtual environment and activate it
* $ virtualenv env
* $ source env/bin/activate

3. Get code and install packages
* $ git clone https://github.com/paula628/gew-test.git
* $ cd gew-test
* $ pip install -r requirements.txt

4. Set up mysql database
* $ pip install mysql-python
* then update settings file, for example:
* DATABASES = 
 {
	     'default': {<br/>
	    	'ENGINE': 'django.db.backends.mysql', #this is standard <br/>
	    	'NAME': ‘escpdigital$default’, #replace this with your database name <br/>
	    	'USER': ‘escpdigital’, #replace with your db user name <br/>
	    	'PASSWORD': 'escpescp', #replace with your db password <br/>
	    	'HOST' : ‘escpdigital.mysql.pythonanywhere-services.com’, #replace with your host name <br/>
	    }

	}

5. Create superuser:
* $ python manage.py createsuperuser

6. Run migration files:
* $ python manage.py migrate

7. Set up consumer key and shared secret in django admin using the superuser credentials:
* login to: www.server-url.com/admin
* Go to consumers -> add consumer
* key: escpdigitalescpdigital #key and secret could be anything you want
* secret: secret

8. Add the server’s url in « ALLOWED_HOSTS » in the settings file located in wheelproj.settings 

9. Set up blackboard LTI:
* Go to  Course Content -> Tools -> Basic LTI tool 
* Sélect the By URL tab and fill in the following:

	* name: GEW Questionnaire
	* launch url: www.new-server-url.com/base/login
	* consumer key: escpdigitalescpdigital
	* shared secret: secret
	* user_id, username, email —> required by tool
	* date and time restrictions —> enter the désired display after or until date 

*  there are additional settings to allow a connection to an external URL that can only be entered by the LMS admin user

