from flask import Blueprint,render_template,request,jsonify
from models.video import Video
from models.user import User
main_bp=Blueprint("main",__name__); TERMS=["Term 1","Term 2","Term 3","Term 4"]; LEVELS=["Beginner","Elementary","Pre-Intermediate","Intermediate","Upper-Intermediate","Advanced"]; UNITS=[f"Unit {i}" for i in range(1,13)]
@main_bp.route("/")
def index(): return render_template("main/index.html",latest=Video.query.order_by(Video.created_at.desc()).limit(8).all(),terms=TERMS,levels=LEVELS,units=UNITS)
@main_bp.route("/browse")
def browse():
    term=request.args.get("term",""); level=request.args.get("level",""); unit=request.args.get("unit",""); page=request.args.get("page",1,type=int); q=Video.query
    if term:q=q.filter_by(term=term)
    if level:q=q.filter_by(level=level)
    if unit:q=q.filter_by(unit=unit)
    p=q.order_by(Video.created_at.desc()).paginate(page=page,per_page=9,error_out=False)
    return render_template("main/browse.html",pagination=p,terms=TERMS,levels=LEVELS,units=UNITS,current_term=term,current_level=level,current_unit=unit,current_sort="newest")
@main_bp.route("/api/stats")
def api_stats(): return jsonify({"videos":Video.query.count(),"users":User.query.count()})
