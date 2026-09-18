from flask import Blueprint,render_template,redirect,url_for,flash,request,jsonify,current_app
from flask_login import login_required,current_user
from app import db
from models.video import Video
from models.comment import Comment
from models.rating import Rating
from utils.gcs import upload_video_to_gcs,delete_blob_from_gcs
videos_bp=Blueprint("videos",__name__,url_prefix="/videos"); TERMS=["Term 1","Term 2","Term 3","Term 4"]; LEVELS=["Beginner","Elementary","Pre-Intermediate","Intermediate","Upper-Intermediate","Advanced"]; UNITS=[f"Unit {i}" for i in range(1,13)]
@videos_bp.route("/upload",methods=["GET","POST"])
@login_required
def upload():
    if request.method=="POST":
        f=request.files.get("video_file"); title=request.form.get("title","").strip(); term=request.form.get("term",""); level=request.form.get("level",""); unit=request.form.get("unit","")
        if not all([f,title,term,level,unit]): flash("Complete all required fields.","danger")
        elif "." not in f.filename or f.filename.rsplit(".",1)[1].lower() not in {"mp4","webm","mov","avi"}: flash("Unsupported video type.","danger")
        else:
            try:
                url=upload_video_to_gcs(f.stream,f.filename); v=Video(title=title,description=request.form.get("description",""),gcs_url=url,term=term,level=level,unit=unit,user_id=current_user.id); db.session.add(v); db.session.commit(); return redirect(url_for("videos.detail",video_id=v.id))
            except Exception as e: current_app.logger.exception(e); flash("Upload failed. Check Cloudinary settings.","danger")
    return render_template("videos/upload.html",terms=TERMS,levels=LEVELS,units=UNITS)
@videos_bp.route("/<int:video_id>")
def detail(video_id): return render_template("videos/detail.html",video=Video.query.get_or_404(video_id),comments=Comment.query.filter_by(video_id=video_id).order_by(Comment.created_at.desc()).all())
@videos_bp.route("/<int:video_id>/comment",methods=["POST"])
@login_required
def comment(video_id):
    c=(request.get_json(silent=True) or {}).get("content","").strip()
    if not c:return jsonify(error="Empty comment"),400
    x=Comment(content=c,video_id=video_id,user_id=current_user.id); db.session.add(x); db.session.commit(); return jsonify(content=x.content,username=current_user.username)
@videos_bp.route("/<int:video_id>/rate",methods=["POST"])
@login_required
def rate(video_id):
    s=int((request.get_json(silent=True) or {}).get("score",0))
    if s not in range(1,6):return jsonify(error="Score 1-5"),400
    r=Rating.query.filter_by(video_id=video_id,user_id=current_user.id).first()
    if r:r.score=s
    else:db.session.add(Rating(score=s,video_id=video_id,user_id=current_user.id))
    db.session.commit(); v=Video.query.get_or_404(video_id); return jsonify(avg_rating=v.avg_rating,rating_count=v.rating_count)
@videos_bp.route("/<int:video_id>/delete",methods=["POST"])
@login_required
def delete(video_id):
    v=Video.query.get_or_404(video_id)
    if v.user_id!=current_user.id:return redirect(url_for("videos.detail",video_id=video_id))
    delete_blob_from_gcs(v.gcs_url); db.session.delete(v); db.session.commit(); return redirect(url_for("main.browse"))
