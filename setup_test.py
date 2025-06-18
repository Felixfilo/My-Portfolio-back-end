from app import app
from models import db, Project, Technology, DemoImage, DemoVideo
from supabase_utils import test_supabase_connection
import os

def setup_and_test():
    """Setup database and test Supabase connection"""
    
    print("Testing Supabase connection...")
    if test_supabase_connection():
        print("✅ Supabase connection successful!")
    else:
        print("❌ Supabase connection failed!")
        return
    
    print("\nSetting up database...")
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Test database connection
            projects_count = Project.query.count()
            print(f"✅ Database connection successful! Found {projects_count} projects.")
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Make sure your Supabase bucket 'portfolio-media' is created and public")
    print("2. Update your .env file with correct SUPABASE_URL and SUPABASE_KEY")
    print("3. Run your Flask app: flask run")

if __name__ == "__main__":
    setup_and_test()