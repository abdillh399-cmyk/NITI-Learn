import os,uuid,cloudinary,cloudinary.uploader
from flask import current_app
def _configure(): cloudinary.config(cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],api_key=os.environ["CLOUDINARY_API_KEY"],api_secret=os.environ["CLOUDINARY_API_SECRET"],secure=True)
def upload_video_to_gcs(file_stream,original_filename):
    _configure(); r=cloudinary.uploader.upload_large(file_stream,resource_type="video",public_id=f"peerlearn/videos/{uuid.uuid4().hex}",overwrite=False,chunk_size=6*1024*1024); return r["secure_url"]
def delete_blob_from_gcs(public_url):
    try:
        _configure(); parts=public_url.split("/upload/");
        if len(parts)<2:return False
        path=parts[1]
        if path.startswith("v") and "/" in path:path=path.split("/",1)[1]
        cloudinary.uploader.destroy(os.path.splitext(path)[0],resource_type="video"); return True
    except Exception as e: current_app.logger.warning(f"Cloudinary delete failed: {e}"); return False
