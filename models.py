from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    github_url = db.Column(db.String(200))
    demo_url = db.Column(db.String(200))
    image_url = db.Column(db.String(200))  # Main project thumbnail
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with technologies
    technologies = db.relationship('Technology', backref='project', lazy=True, cascade='all, delete-orphan')
    
    # Relationships with separate media tables
    demo_images = db.relationship('DemoImage', backref='project', lazy=True, cascade='all, delete-orphan', order_by='DemoImage.order_index')
    demo_videos = db.relationship('DemoVideo', backref='project', lazy=True, cascade='all, delete-orphan', order_by='DemoVideo.order_index')
    
    def __init__(self, title, description, github_url='', demo_url='', image_url=''):
        self.title = title
        self.description = description
        self.github_url = github_url
        self.demo_url = demo_url
        self.image_url = image_url
    
    def __repr__(self):
        return f'<Project {self.title}>'
    
    def to_dict(self):
        """Convert project to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'github_url': self.github_url,
            'demo_url': self.demo_url,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'technologies': [tech.name for tech in self.technologies],
            'demo_images': [img.to_dict() for img in self.demo_images],
            'demo_videos': [vid.to_dict() for vid in self.demo_videos],
            'total_demo_images': len(self.demo_images),
            'total_demo_videos': len(self.demo_videos)
        }
    
    def add_demo_image(self, image_url, image_name=None, caption=None, order_index=None):
        """Add a demo image to the project"""
        if order_index is None:
            max_order = db.session.query(db.func.max(DemoImage.order_index)).filter_by(project_id=self.id).scalar() or 0
            order_index = max_order + 1
        
        demo_image = DemoImage(
            project_id=self.id,
            image_url=image_url,
            image_name=image_name,
            caption=caption,
            order_index=order_index
        )
        db.session.add(demo_image)
        return demo_image
    
    def add_demo_video(self, video_url, video_name=None, caption=None, duration=None, order_index=None):
        """Add a demo video to the project"""
        if order_index is None:
            max_order = db.session.query(db.func.max(DemoVideo.order_index)).filter_by(project_id=self.id).scalar() or 0
            order_index = max_order + 1
        
        demo_video = DemoVideo(
            project_id=self.id,
            video_url=video_url,
            video_name=video_name,
            caption=caption,
            duration=duration,
            order_index=order_index
        )
        db.session.add(demo_video)
        return demo_video

class Technology(db.Model):
    __tablename__ = 'technologies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    
    def __init__(self, name, project_id):
        self.name = name
        self.project_id = project_id
    
    def __repr__(self):
        return f'<Technology {self.name}>'

class DemoImage(db.Model):
    __tablename__ = 'demo_images'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_name = db.Column(db.String(100))
    caption = db.Column(db.String(200))
    alt_text = db.Column(db.String(200))  # For accessibility
    order_index = db.Column(db.Integer, default=0)
    width = db.Column(db.Integer)  # Image width in pixels
    height = db.Column(db.Integer)  # Image height in pixels
    file_size = db.Column(db.Integer)  # File size in bytes
    is_featured = db.Column(db.Boolean, default=False)  # Mark as featured image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, project_id, image_url, image_name=None, caption=None, alt_text=None, 
                 order_index=0, width=None, height=None, file_size=None, is_featured=False):
        self.project_id = project_id
        self.image_url = image_url
        self.image_name = image_name
        self.caption = caption
        self.alt_text = alt_text or image_name
        self.order_index = order_index
        self.width = width
        self.height = height
        self.file_size = file_size
        self.is_featured = is_featured
    
    def __repr__(self):
        return f'<DemoImage {self.image_name or self.image_url}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'image_url': self.image_url,
            'image_name': self.image_name,
            'caption': self.caption,
            'alt_text': self.alt_text,
            'order_index': self.order_index,
            'width': self.width,
            'height': self.height,
            'file_size': self.file_size,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DemoVideo(db.Model):
    __tablename__ = 'demo_videos'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    video_url = db.Column(db.String(500), nullable=False)
    video_name = db.Column(db.String(100))
    caption = db.Column(db.String(200))
    thumbnail_url = db.Column(db.String(500))  # Video thumbnail/poster
    order_index = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer)  # Duration in seconds
    file_size = db.Column(db.Integer)  # File size in bytes
    video_format = db.Column(db.String(10))  # mp4, webm, etc.
    width = db.Column(db.Integer)  # Video width in pixels
    height = db.Column(db.Integer)  # Video height in pixels
    is_autoplay = db.Column(db.Boolean, default=False)
    is_muted = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, project_id, video_url, video_name=None, caption=None, thumbnail_url=None,
                 order_index=0, duration=None, file_size=None, video_format=None, 
                 width=None, height=None, is_autoplay=False, is_muted=True):
        self.project_id = project_id
        self.video_url = video_url
        self.video_name = video_name
        self.caption = caption
        self.thumbnail_url = thumbnail_url
        self.order_index = order_index
        self.duration = duration
        self.file_size = file_size
        self.video_format = video_format
        self.width = width
        self.height = height
        self.is_autoplay = is_autoplay
        self.is_muted = is_muted
    
    def __repr__(self):
        return f'<DemoVideo {self.video_name or self.video_url}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'video_url': self.video_url,
            'video_name': self.video_name,
            'caption': self.caption,
            'thumbnail_url': self.thumbnail_url,
            'order_index': self.order_index,
            'duration': self.duration,
            'file_size': self.file_size,
            'video_format': self.video_format,
            'width': self.width,
            'height': self.height,
            'is_autoplay': self.is_autoplay,
            'is_muted': self.is_muted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'duration_formatted': self.format_duration() if self.duration else None
        }
    
    def format_duration(self):
        """Format duration in seconds to MM:SS format"""
        if not self.duration:
            return None
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"
