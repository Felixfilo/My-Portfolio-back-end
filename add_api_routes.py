"""
Add this file to your Flask backend and run it to add API routes for frontend integration.
This will modify your existing app.py to include the necessary API endpoints.
"""

import os
import sys

def add_api_routes_to_app():
    """Add API routes to existing app.py file"""
    
    # Read the current app.py file
    try:
        with open('app.py', 'r') as f:
            app_content = f.read()
    except FileNotFoundError:
        print("❌ app.py file not found. Make sure you're in the correct directory.")
        return False
    
    # Check if CORS is already imported
    if 'from flask_cors import CORS' not in app_content:
        # Add CORS import after Flask import
        app_content = app_content.replace(
            'from flask import Flask, render_template, request, redirect, url_for, flash, jsonify',
            'from flask import Flask, render_template, request, redirect, url_for, flash, jsonify\nfrom flask_cors import CORS'
        )
    
    # Check if CORS is already configured
    if 'CORS(app' not in app_content:
        # Add CORS configuration after app creation
        app_content = app_content.replace(
            'app = Flask(__name__)',
            '''app = Flask(__name__)

# Enable CORS for frontend integration
CORS(app, 
     origins=["*"],  # Allow all origins - restrict this in production
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])'''
        )
    
    # API routes to add
    api_routes = '''

# API Routes for Frontend Integration
@app.route('/api/projects', methods=['GET', 'OPTIONS'])
def api_get_projects():
    """API endpoint to get all projects with full data structure for frontend"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print("API: Fetching all projects...")
        projects = Project.query.order_by(Project.created_at.desc()).all()
        print(f"API: Found {len(projects)} projects")
        
        # Convert projects to the format expected by frontend
        projects_data = []
        for project in projects:
            project_dict = {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'github_url': project.github_url,
                'demo_url': project.demo_url,
                'image_url': project.image_url,
                'created_at': project.created_at.isoformat() + 'Z' if project.created_at else None,
                'updated_at': project.updated_at.isoformat() + 'Z' if project.updated_at else None,
                'technologies': [tech.name for tech in project.technologies] if project.technologies else [],
                'demo_images': [img.to_dict() for img in project.demo_images] if project.demo_images else [],
                'demo_videos': [vid.to_dict() for vid in project.demo_videos] if project.demo_videos else [],
                'total_demo_images': len(project.demo_images) if project.demo_images else 0,
                'total_demo_videos': len(project.demo_videos) if project.demo_videos else 0
            }
            projects_data.append(project_dict)
        
        print(f"API: Returning {len(projects_data)} projects")
        return jsonify(projects_data), 200
        
    except Exception as e:
        print(f"API Error fetching projects: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to fetch projects: {str(e)}'}), 500

@app.route('/api/projects/<int:project_id>', methods=['GET', 'OPTIONS'])
def api_get_project(project_id):
    """API endpoint to get a single project by ID for frontend"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        print(f"API: Fetching project {project_id}...")
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Convert to dict format expected by frontend
        project_dict = {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'github_url': project.github_url,
            'demo_url': project.demo_url,
            'image_url': project.image_url,
            'created_at': project.created_at.isoformat() + 'Z' if project.created_at else None,
            'updated_at': project.updated_at.isoformat() + 'Z' if project.updated_at else None,
            'technologies': [tech.name for tech in project.technologies] if project.technologies else [],
            'demo_images': [img.to_dict() for img in project.demo_images] if project.demo_images else [],
            'demo_videos': [vid.to_dict() for vid in project.demo_videos] if project.demo_videos else [],
            'total_demo_images': len(project.demo_images) if project.demo_images else 0,
            'total_demo_videos': len(project.demo_videos) if project.demo_videos else 0
        }
        
        print(f"API: Returning project {project.title}")
        return jsonify(project_dict), 200
        
    except Exception as e:
        print(f"API Error fetching project {project_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to fetch project: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check endpoint for frontend"""
    try:
        project_count = Project.query.count()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'total_projects': project_count,
            'database': 'connected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
'''
    
    # Check if API routes are already added
    if '@app.route(\'/api/projects\')' not in app_content and '@app.route("/api/projects")' not in app_content:
        # Find where to insert the API routes (before error handlers)
        if '# Error handlers' in app_content:
            app_content = app_content.replace('# Error handlers', api_routes + '\n# Error handlers')
        elif '@app.errorhandler(404)' in app_content:
            app_content = app_content.replace('@app.errorhandler(404)', api_routes + '\n@app.errorhandler(404)')
        else:
            # Add before the main block
            app_content = app_content.replace("if __name__ == '__main__':", api_routes + "\nif __name__ == '__main__':")
    
    # Write the updated content back to app.py
    try:
        # Create backup
        with open('app.py.backup', 'w') as f:
            f.write(open('app.py', 'r').read())
        print("✅ Created backup: app.py.backup")
        
        # Write updated file
        with open('app.py', 'w') as f:
            f.write(app_content)
        print("✅ Updated app.py with API routes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating app.py: {e}")
        return False

def install_flask_cors():
    """Install flask-cors if not already installed"""
    try:
        import flask_cors
        print("✅ flask-cors is already installed")
        return True
    except ImportError:
        print("📦 Installing flask-cors...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask-cors"])
            print("✅ flask-cors installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install flask-cors: {e}")
            return False

def main():
    """Main function to set up API integration"""
    print("🚀 Setting up API integration for your Flask backend...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ app.py not found. Please run this script in your backend directory.")
        return
    
    if not os.path.exists('models.py'):
        print("❌ models.py not found. Please run this script in your backend directory.")
        return
    
    # Install flask-cors
    if not install_flask_cors():
        print("❌ Failed to install flask-cors. Please install it manually:")
        print("   pip install flask-cors")
        return
    
    # Add API routes to app.py
    if not add_api_routes_to_app():
        print("❌ Failed to update app.py")
        return
    
    print("\n🎉 API integration setup complete!")
    print("=" * 60)
    print("✅ Added CORS support")
    print("✅ Added /api/projects endpoint")
    print("✅ Added /api/projects/<id> endpoint") 
    print("✅ Added /api/health endpoint")
    print("✅ Created backup file: app.py.backup")
    
    print("\n📋 Next steps:")
    print("1. Deploy your updated backend to Render")
    print("2. Your frontend should now be able to connect!")
    print("3. Test the API endpoints:")
    print(f"   - GET {os.getenv('RENDER_EXTERNAL_URL', 'https://your-backend-url.onrender.com')}/api/health")
    print(f"   - GET {os.getenv('RENDER_EXTERNAL_URL', 'https://your-backend-url.onrender.com')}/api/projects")
    
    print("\n🔧 If you need to revert changes:")
    print("   mv app.py.backup app.py")

if __name__ == "__main__":
    main()