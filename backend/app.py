import os
from flask import Flask, render_template

# Configure to serve the frontend folder
frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(
    __name__,
    template_folder=frontend_folder,
    static_folder=frontend_folder,
    static_url_path=''
)

# TODO: MySQL Database Connection
# You can set up the DB connection here using mysql-connector-python or SQLAlchemy
# Example: DB config from environment variables (use dotenv in the future)

@app.route('/')
def home():
    """Serve the homepage."""
    return render_template('index.html')

if __name__ == '__main__':
    # Start the Flask development server on port 5000
    app.run(debug=True, port=5000)
