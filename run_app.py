import os
import sys
import time
from src.server import app, db

# Set environment variables
os.environ['APP_SETTINGS'] = 'src.server.config.ProductionConfig_MySQL'

def init_db(max_retries=5, retry_delay=5):
    retries = 0
    while retries < max_retries:
        try:
            print(f"Attempting to initialize database (attempt {retries + 1}/{max_retries})")
            with app.app_context():
                db.create_all()
                print("Database tables created successfully!")
                return True
        except Exception as e:
            print(f"Error creating database tables: {e}")
            if retries < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            retries += 1
    
    print("Failed to initialize database after maximum retries")
    return False

if __name__ == '__main__':
    # Initialize database with retries
    if not init_db():
        print("Could not initialize database. Please check your database configuration.")
        sys.exit(1)
    
    # Run the application with host set to 0.0.0.0 to allow external access
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True,
        threaded=True
    ) 