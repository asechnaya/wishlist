MyWishlist Project
A simple Django web application to manage personal wishlists, allowing users to add, view, edit, and delete their wishes, with public sharing capabilities.

Features
User Authentication: Secure registration and login for users.

Wish Management:

Add new wishes with a title, image (avatar), price, and a link to the shop.

View details of individual wishes, including the creation date.

Edit existing wishes.

Delete wishes.

Tagging System: Organize wishes with tags (global tags).

Wishlist Filtering: Filter wishes by tags on the main wishlist page.

Public Wishlists: Each user has a public page (/wisher/<username>/) where others can view their wishes and filter them by tags.

Public Wish Details: View individual wish details on a public page (/wisher/<username>/<wish_id>/).

Setup and Local Development
Follow these steps to get the project up and running on your local machine.

Prerequisites
Python 3.10+ (Python 3.11 is recommended)

pip (Python package installer)

1. Clone the Repository
First, clone the project from GitHub:

git clone https://github.com/asechnaya/wishlist.git
cd wishlist/mywishlist_project

2. Create and Activate a Virtual Environment
It's highly recommended to use a virtual environment to manage project dependencies.

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

3. Install Dependencies
Install all required Python packages using pip and the requirements.txt file:

pip install -r requirements.txt

4. Database Migrations
Apply the database migrations to set up your database tables. If you've previously run the project and encountered database issues, you might need to delete db.sqlite3 and the wishes/migrations/0*.py files before running these commands for a fresh start.

python manage.py makemigrations wishes
python manage.py migrate

5. Create a Superuser
Create an administrator account to access the Django admin panel and manage users/data.

python manage.py createsuperuser

Follow the prompts to set up your username, email, and password.

6. Run the Development Server
Start the Django development server:

python manage.py runserver

You can now access the application in your web browser at http://127.0.0.1:8000/.

Running Tests
To run the project's test suite:

# Ensure your virtual environment is active
export DJANGO_SETTINGS_MODULE=mywishlist_project.settings # On Windows: set DJANGO_SETTINGS_MODULE=mywishlist_project.settings
python manage.py test

Deployment
This project can be deployed to various hosting providers. A common setup involves:

Gunicorn: As a WSGI HTTP Server.

Nginx: As a reverse proxy and for serving static/media files.

PostgreSQL: As the production database.

Refer to the deployment guide for detailed steps on setting up a production environment.

Contributing
Feel
