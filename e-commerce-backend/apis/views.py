from utils.response import get_error_response, get_success_response
from firebase_admin import storage
from django.views.decorators.csrf import csrf_exempt
from utils.decorator import validate_token
from accounts.models import User
from firebase_admin import firestore


# Create your views here.
@csrf_exempt
@validate_token
def profile_upload(*args, **kwargs):
    try:
        req = args[0]
        # Get image files from the req.FILES
        image = req.FILES.get("image")
        if image is None:
            return get_error_response("No image data found!")
        # Firebase Storage bucket
        bucket = storage.bucket()
        blob = bucket.blob(f"profiles/{image.name}")
        blob.upload_from_file(image, content_type=image.content_type)
        blob.make_public()
        user = User.objects.get(id=kwargs["user_id"])
        client = firestore.client()
        document = client.collection("users").document(user.fb_doc_id)
        document.update({"profile": blob.public_url})
        user.profile_url = blob.public_url
        user.save()
        return get_success_response({"url": blob.public_url})

    except Exception as e:
        return get_error_response(str(e.args[0]))
