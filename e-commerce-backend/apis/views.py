from utils.response import get_error_response, get_success_response, get_method_error
from django.views.decorators.csrf import csrf_exempt
from utils.decorator import validate_token
from accounts.models import User


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
            name = f"profiles/{user_id}"
            user = User.objects.get(id=user_id)
            user.save()
            return get_success_response({"url": ""})

        except Exception as e:
            return get_error_response(str(e.args[0]))
    else:
        return get_method_error(req, "POST")
