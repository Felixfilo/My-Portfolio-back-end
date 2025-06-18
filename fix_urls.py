from app import app
from models import db, Project

with app.app_context():
    try:
        projects = Project.query.all()
        for project in projects:
            if project.image_url and project.image_url.endswith('?'):
                print(f"Fixing URL for {project.title}")
                print(f"  Before: {project.image_url}")
                project.image_url = project.image_url.rstrip('?')
                print(f"  After: {project.image_url}")
        
        db.session.commit()
        print("URLs fixed!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()