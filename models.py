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
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with technologies
    technologies = db.relationship('Technology', backref='project', lazy=True, cascade='all, delete-orphan')
    
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
            'technologies': [tech.name for tech in self.technologies] #type:ignore
        }

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
