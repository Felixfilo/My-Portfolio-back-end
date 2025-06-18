from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_migrate import Migrate
from models import db, Project, Technology, DemoImage, DemoVideo
from supabase_utils import upload_file_to_supabase, delete_file_from_supabase
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Supabase PostgreSQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 
    'postgresql://postgres.wzqxmztfntpzgulrxbsi:1Profileprofile2@aws-0-us-east-2.pooler.supabase.com:6543/postgres')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

# Routes
@app.route('/')
def home():
    """Display portfolio homepage with all projects"""
    try:
        print("Attempting to fetch projects...")
        projects = Project.query.order_by(Project.created_at.desc()).all()
        print(f"Successfully fetched {len(projects)} projects")
        
        # Debug each project
        for project in projects:
            print(f"Project {project.id}: {project.title}")
            print(f"  Image URL: {project.image_url}")
            
        return render_template('index.html', projects=projects)
    except Exception as e:
        print(f"Error fetching projects: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading projects. Please try again.', 'error')
        return render_template('index.html', projects=[])

@app.route('/api/projects')
def api_projects():
    """API endpoint to get all projects as JSON"""
    try:
        projects = Project.query.order_by(Project.created_at.desc()).all()
        return jsonify([project.to_dict() for project in projects])
    except Exception as e:
        print(f"Error fetching projects for API: {e}")
        return jsonify({'error': 'Failed to fetch projects'}), 500

@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    """Add a new project to the portfolio"""
    if request.method == 'POST':
        try:
            # Handle main project image upload
            image_url = ''
            if 'project_image' in request.files:
                file = request.files['project_image']
                if file and file.filename:
                    image_url = upload_file_to_supabase(file, 'project_images')
            
            # Create new project
            project = Project(
                title=request.form['title'],
                description=request.form['description'],
                github_url=request.form.get('github_url', ''),
                demo_url=request.form.get('demo_url', ''),
                image_url=image_url or request.form.get('image_url', '')
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
            
            # Handle demo media uploads
            demo_files = request.files.getlist('demo_files')
            demo_media_urls = request.form.getlist('demo_media_urls')
            demo_media_types = request.form.getlist('demo_media_types')
            demo_media_names = request.form.getlist('demo_media_names')
            
            # Process uploaded files
            for i, file in enumerate(demo_files):
                if file and file.filename:
                    media_url = upload_file_to_supabase(file, 'demo_media')
                    if media_url:
                        # Determine media type based on file extension
                        file_ext = file.filename.lower().split('.')[-1]
                        media_type = 'video' if file_ext in ['mp4', 'webm', 'mov'] else 'image'
                        
                        if media_type == 'image':
                            demo_image = DemoImage(
                                project_id=project.id,
                                image_url=media_url,
                                image_name=file.filename,
                                order_index=len(demo_media_urls) + i
                            )
                            db.session.add(demo_image)
                        else:
                            demo_video = DemoVideo(
                                project_id=project.id,
                                video_url=media_url,
                                video_name=file.filename,
                                order_index=len(demo_media_urls) + i
                            )
                            db.session.add(demo_video)
            
            # Process URL-based media
            for i, media_url in enumerate(demo_media_urls):
                if media_url.strip():
                    media_type = demo_media_types[i] if i < len(demo_media_types) else 'image'
                    media_name = demo_media_names[i] if i < len(demo_media_names) else None
                    
                    if media_type == 'image':
                        demo_image = DemoImage(
                            project_id=project.id,
                            image_url=media_url.strip(),
                            image_name=media_name,
                            order_index=i
                        )
                        db.session.add(demo_image)
                    else:
                        demo_video = DemoVideo(
                            project_id=project.id,
                            video_url=media_url.strip(),
                            video_name=media_name,
                            order_index=i
                        )
                        db.session.add(demo_video)
            
            db.session.commit()
            flash('Project added successfully!', 'success')
            return redirect(url_for('home'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding project: {e}")
            flash(f'Error adding project: {str(e)}', 'error')
    
    return render_template('add_project.html')

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    """Display detailed view of a specific project"""
    try:
        project = Project.query.get_or_404(project_id)
        return render_template('project_detail.html', project=project)
    except Exception as e:
        print(f"Error fetching project {project_id}: {e}")
        flash('Project not found.', 'error')
        return redirect(url_for('home'))

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    """Edit an existing project"""
    try:
        project = Project.query.get_or_404(project_id)
    except Exception as e:
        print(f"Error fetching project {project_id}: {e}")
        flash('Project not found.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        try:
            # Handle image upload if new image is provided
            if 'project_image' in request.files:
                file = request.files['project_image']
                if file and file.filename:
                    # Delete old image if it exists
                    if project.image_url:
                        delete_file_from_supabase(project.image_url)
                    # Upload new image
                    project.image_url = upload_file_to_supabase(file, 'project_images')
            
            # Update project details
            project.title = request.form['title']
            project.description = request.form['description']
            project.github_url = request.form.get('github_url', '')
            project.demo_url = request.form.get('demo_url', '')
            if not project.image_url:  # Only update if no new image was uploaded
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
            
            # Update demo media
            # Delete old demo files from storage and database
            old_images = DemoImage.query.filter_by(project_id=project.id).all()
            for image in old_images:
                if image.image_url and 'supabase' in image.image_url:
                    delete_file_from_supabase(image.image_url)
            
            old_videos = DemoVideo.query.filter_by(project_id=project.id).all()
            for video in old_videos:
                if video.video_url and 'supabase' in video.video_url:
                    delete_file_from_supabase(video.video_url)
            
            # Delete all old demo media records
            DemoImage.query.filter_by(project_id=project.id).delete()
            DemoVideo.query.filter_by(project_id=project.id).delete()
            
            # Handle new demo file uploads
            demo_files = request.files.getlist('demo_files')
            demo_media_urls = request.form.getlist('demo_media_urls')
            demo_media_types = request.form.getlist('demo_media_types')
            demo_media_names = request.form.getlist('demo_media_names')
            
            # Process uploaded files
            for i, file in enumerate(demo_files):
                if file and file.filename:
                    media_url = upload_file_to_supabase(file, 'demo_media')
                    if media_url:
                        # Determine media type based on file extension
                        file_ext = file.filename.lower().split('.')[-1]
                        media_type = 'video' if file_ext in ['mp4', 'webm', 'mov'] else 'image'
                        
                        if media_type == 'image':
                            demo_image = DemoImage(
                                project_id=project.id,
                                image_url=media_url,
                                image_name=file.filename,
                                order_index=len(demo_media_urls) + i
                            )
                            db.session.add(demo_image)
                        else:
                            demo_video = DemoVideo(
                                project_id=project.id,
                                video_url=media_url,
                                video_name=file.filename,
                                order_index=len(demo_media_urls) + i
                            )
                            db.session.add(demo_video)
            
            # Process URL-based media
            for i, media_url in enumerate(demo_media_urls):
                if media_url.strip():
                    media_type = demo_media_types[i] if i < len(demo_media_types) else 'image'
                    media_name = demo_media_names[i] if i < len(demo_media_names) else None
                    
                    if media_type == 'image':
                        demo_image = DemoImage(
                            project_id=project.id,
                            image_url=media_url.strip(),
                            image_name=media_name,
                            order_index=i
                        )
                        db.session.add(demo_image)
                    else:
                        demo_video = DemoVideo(
                            project_id=project.id,
                            video_url=media_url.strip(),
                            video_name=media_name,
                            order_index=i
                        )
                        db.session.add(demo_video)
            
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('project_detail', project_id=project.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating project: {e}")
            flash(f'Error updating project: {str(e)}', 'error')
    
    # For GET request, prepare data for form
    try:
        tech_string = ', '.join([tech.name for tech in project.technologies])
        return render_template('edit_project.html', project=project, tech_string=tech_string)
    except Exception as e:
        print(f"Error preparing edit form: {e}")
        flash('Error loading project for editing.', 'error')
        return redirect(url_for('home'))

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    """Delete a project"""
    try:
        project = Project.query.get_or_404(project_id)
        
        # Delete associated files from Supabase
        if project.image_url:
            delete_file_from_supabase(project.image_url)
        
        # Delete demo images
        for demo_image in project.demo_images:
            if demo_image.image_url and 'supabase' in demo_image.image_url:
                delete_file_from_supabase(demo_image.image_url)
        
        # Delete demo videos
        for demo_video in project.demo_videos:
            if demo_video.video_url and 'supabase' in demo_video.video_url:
                delete_file_from_supabase(demo_video.video_url)
        
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting project: {e}")
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

if __name__ == '__main__':
    # Create tables
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
