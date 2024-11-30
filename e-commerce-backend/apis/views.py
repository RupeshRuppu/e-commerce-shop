from utils.response import get_error_response, get_success_response, get_method_error
from django.views.decorators.csrf import csrf_exempt
from utils.decorator import validate_token
from accounts.models import User
from cloudinary.uploader import upload


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
            result = upload(image, public_id=user_id, folder="user-profiles")
            user = User.objects.get(id=user_id)
            user.profile_url = result["secure_url"]
            user.save()
            return get_success_response({"url": result["secure_url"]})

        except Exception as e:
            return get_error_response(str(e.args[0]))
    else:
        return get_method_error(req, "POST")


# TODO : category comes from UI and upload under those folder.
# TODO : user_id(which admin/ops) member has uploaded this product?
@csrf_exempt
@validate_token
def product_upload(*args, **kwargs):
    req, user_id = args[0], kwargs["user_id"]
    if req.method == "POST":
        try:
            # Get image files from the req.FILES
            images = list(filter(lambda img: img, req.FILES.getlist("images")))
            category, result = req.POST.get("category"), []
            for image in images:
                response = upload(image, folder=f"e-commerce-products/{category}")
                result.append(response["secure_url"])
            return get_success_response({"uploaded_files": result})

        except Exception as e:
            return get_error_response(str(e.args[0]))
    else:
        return get_method_error(req, "POST")
