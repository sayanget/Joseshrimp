from app import create_app
import os
from waitress import serve

# Create the application instance using the production configuration
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    # Waitress will default to 0.0.0.0:8080 if not specified
    # Render provides PORT in environment
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Waitress server on port {port}...")
    serve(app, host="0.0.0.0", port=port)
