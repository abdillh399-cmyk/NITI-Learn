from datetime import datetime
from app import db
class Video(db.Model):
    __tablename__="videos"
    id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(150),nullable=False); description=db.Column(db.Text,default=""); gcs_url=db.Column(db.String(512),nullable=False); thumbnail_url=db.Column(db.String(512),default=""); duration=db.Column(db.Integer,default=0)
    term=db.Column(db.String(50),nullable=False); level=db.Column(db.String(50),nullable=False); unit=db.Column(db.String(50),nullable=False); user_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False); created_at=db.Column(db.DateTime,default=datetime.utcnow)
    comments=db.relationship("Comment",backref="video",lazy=True,cascade="all, delete-orphan"); ratings=db.relationship("Rating",backref="video",lazy=True,cascade="all, delete-orphan")
    @property
    def avg_rating(self): return round(sum(r.score for r in self.ratings)/len(self.ratings),1) if self.ratings else 0
    @property
    def rating_count(self): return len(self.ratings)
