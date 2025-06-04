from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import os
from models import db, Project, Technology
from config import config

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    return app

app = create_app()

# Routes
@app.route('/')
def home():
    """Display portfolio homepage with all projects"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('index.html', projects=projects)

@app.route('/api/projects')
def api_projects():
    """API endpoint to get all projects as JSON"""
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return jsonify([project.to_dict() for project in projects])

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    """Add a new project to the portfolio"""
    if request.method == 'POST':
        try:
            # Create new project
            project = Project(
                title=request.form['title'],
                description=request.form['description'],
                github_url=request.form.get('github_url', ''),
                demo_url=request.form.get('demo_url', ''),
                image_url=request.form.get('image_url', '')
            )
            
            db.session.add(project)
            db.session.flush()  # Get the project ID
            
            # Add technologies
            technologies_input = request.form.get('technologies', '')
            if technologies_input:
                tech_list = [tech.strip() for tech in technologies_input.split(',') if tech.strip()]
                for tech_name in tech_list:
                    technology = Technology(name=tech_name, project_id=project.id)
                    db.session.add(technology)
            
            db.session.commit()
            flash('Project added successfully!', 'success')
            return redirect(url_for('home'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding project: {str(e)}', 'error')
    
    return render_template('add_project.html')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Display detailed view of a specific project"""
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit an existing project"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        try:
            # Update project details
            project.title = request.form['title']
            project.description = request.form['description']
            project.github_url = request.form.get('github_url', '')
            project.demo_url = request.form.get('demo_url', '')
            project.image_url = request.form.get('image_url', '')
            project.updated_at = datetime.utcnow()
            
            # Update technologies
            # First, remove existing technologies
            Technology.query.filter_by(project_id=project.id).delete()
            
            # Add new technologies
            technologies_input = request.form.get('technologies', '')
            if technologies_input:
                tech_list = [tech.strip() for tech in technologies_input.split(',') if tech.strip()]
                for tech_name in tech_list:
                    technology = Technology(name=tech_name, project_id=project.id)
                    db.session.add(technology)
            
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('project_detail', project_id=project.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {str(e)}', 'error')
    
    # For GET request, prepare technologies string
    tech_string = ', '.join([tech.name for tech in project.technologies])
    return render_template('edit_project.html', project=project, tech_string=tech_string)

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    """Delete a project"""
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting project: {str(e)}', 'error')
    
    return redirect(url_for('home'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Database initialization
def init_db():
    """Initialize the database with tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    # Initialize database
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
