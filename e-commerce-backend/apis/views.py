from utils.response import get_error_response, get_success_response, get_method_error
from firebase_admin import storage
from django.views.decorators.csrf import csrf_exempt
from utils.decorator import validate_token
from accounts.models import User
from firebase_admin import firestore
from time import time


# Create your views here.
@csrf_exempt
@validate_token
def profile_upload(*args, **kwargs):
    req, user_id = args[0], kwargs["user_id"]
    if req.method == "POST":
        try:
            # Get image files from the req.FILES
            image = req.FILES.get("image")
            if image is None:
                return get_error_response("No image data found!")

            name = f"profiles/{user_id}--{str(int(time()*1000))}"
            # Firebase Storage bucket.
            bucket = storage.bucket()
            blob = bucket.blob(name)
            blob.upload_from_file(image, content_type=image.content_type)
            blob.make_public()
            user = User.objects.get(id=user_id)

            # delete previous image from storage.
            if user.profile_url:
                file_name = user.profile_url.split("/")
                _blob = bucket.blob(f"{file_name[-2]}/{file_name[-1]}")
                if _blob.exists():
                    _blob.delete()

            # update firestore users collection.
            client = firestore.client()
            document = client.collection("users").document(user.fb_doc_id)
            document.update({"profile": blob.public_url})
            user.profile_url = blob.public_url

            user.save()
            return get_success_response({"url": blob.public_url})

        except Exception as e:
            return get_error_response(str(e.args[0]))
    else:
        return get_method_error(req, "POST")
