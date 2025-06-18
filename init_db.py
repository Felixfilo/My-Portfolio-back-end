from app import app  # Import the app instance directly
from models import db, Project, Technology 
import os

def create_sample_data():
    """Create some sample data for testing"""
    
    with app.app_context():
        try:
            print(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Clear existing data
            db.drop_all()
            db.create_all()
            
            # Create sample projects
            project1 = Project(
                title="Portfolio Website",
                description="A responsive portfolio website built with Flask and Bootstrap. Features project showcase, contact form, and admin panel.",
                github_url="https://github.com/yourusername/portfolio",
                demo_url="https://yourportfolio.com",
                image_url="https://via.placeholder.com/400x300"
            )
            
            project2 = Project(
                title="E-commerce API",
                description="RESTful API for an e-commerce platform with user authentication, product management, and order processing.",
                github_url="https://github.com/yourusername/ecommerce-api",
                demo_url="",
                image_url="https://via.placeholder.com/400x300"
            )
            
            project3 = Project(
                title="Task Management App",
                description="A full-stack task management application with user authentication, real-time updates, and team collaboration features.",
                github_url="https://github.com/yourusername/task-manager",
                demo_url="https://taskmanager-demo.com",
                image_url="https://via.placeholder.com/400x300"
            )
            
            db.session.add(project1)
            db.session.add(project2)
            db.session.add(project3)
            db.session.flush()  # Get the project IDs
            
            # Add technologies for project1
            tech1_list = ["Python", "Flask", "SQLAlchemy", "Bootstrap", "HTML", "CSS"]
            for tech_name in tech1_list:
                tech = Technology(name=tech_name, project_id=project1.id)
                db.session.add(tech)
            
            # Add technologies for project2
            tech2_list = ["Python", "Flask", "SQLAlchemy", "JWT", "REST API"]
            for tech_name in tech2_list:
                tech = Technology(name=tech_name, project_id=project2.id)
                db.session.add(tech)

            # Add technologies for project3
            tech3_list = ["React", "Node.js", "MongoDB", "Socket.io", "Express"]
            for tech_name in tech3_list:
                tech = Technology(name=tech_name, project_id=project3.id)
                db.session.add(tech)

            db.session.commit()
            print("✅ Sample data created successfully!")
            print("✅ Created 3 projects with technologies")
            print(f"✅ Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample data: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_sample_data()