from django.views.decorators.csrf import csrf_exempt
from utils.response import (
    get_error_response,
    get_success_response,
    get_method_error,
    parse_body,
)
from accounts.models import User, Tokens
from django.core.exceptions import ObjectDoesNotExist
from utils.jwt import generate_tokens
from django.db.models import Q
from jwt import decode
from jwt.exceptions import ExpiredSignatureError
from django.conf import settings


@csrf_exempt
def register(req):
    if req.method == "POST":
        try:
            body = parse_body(req.body)
            username, password = body.get("username"), body.get("password")
            # check if a user already exists with these credentials.
            try:
                User.objects.get(
                    Q(username__iexact=username) | Q(email__iexact=username)
                )
                return get_error_response("USER ALREADY EXISTS")
            except ObjectDoesNotExist:
                user = User(**body, email=username)
                user.set_password(password)

                # generate tokens
                payload = generate_tokens(user)
                token = Tokens(
                    created_at=payload["created_at"],
                    expires_at=payload["expires_at"],
                    token=payload["token"],
                    refresh_token=payload["rtoken"],
                    user=user,
                )

                user.save()
                token.save()
                return get_success_response(
                    {
                        "access_token": payload["token"],
                        "refresh_token": payload["rtoken"],
                    }
                )

        except Exception as ex:
            return get_error_response(ex.args)
    else:
        return get_method_error(req, "POST")


@csrf_exempt
def login(req):
    if req.method == "POST":
        try:
            body = parse_body(req.body)
            username, password = body.get("username"), body.get("password")

            # check if a user exists.
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )

            # validate his password.
            check = user.check_password(password)
            if not check:
                return get_error_response("INVALID PASSWORD")

            payload = generate_tokens(user)
            token = Tokens(
                created_at=payload["created_at"],
                expires_at=payload["expires_at"],
                token=payload["token"],
                refresh_token=payload["rtoken"],
                user=user,
            )
            token.save()
            return get_success_response(
                {
                    "access_token": payload["token"],
                    "refresh_token": payload["rtoken"],
                }
            )

        except ObjectDoesNotExist:
            return get_error_response("USER NOT EXISTS")

        except Exception as ex:
            return get_error_response(ex.args)
    else:
        return get_method_error(req, "POST")


@csrf_exempt
def refresh_token(req):
    if req.method == "POST":
        try:
            body = parse_body(req.body)
            refresh_token = body.get("refresh_token")

            if refresh_token is None:
                return get_error_response("NO REFRESH TOKEN PROVIDED IN BODY")

            # check the refresh_token is black-listed
            rf_token = Tokens.objects.filter(
                refresh_token__iexact=refresh_token
            ).first()

            if rf_token is None:
                return get_error_response("NOT A VALID REFRESH TOKEN")

            if rf_token and rf_token.is_black_listed:
                return get_error_response("TOKEN BLACKLISTED")

            # validate token.
            payload = decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])

            rf_token.is_black_listed = True
            user = User.objects.get(id=payload["id"])
            payload = generate_tokens(user)
            token = Tokens(
                created_at=payload["created_at"],
                expires_at=payload["expires_at"],
                token=payload["token"],
                refresh_token=payload["rtoken"],
                user=user,
            )
            rf_token.save()
            token.save()
            return get_success_response(
                {
                    "access_token": payload["token"],
                    "refresh_token": payload["rtoken"],
                }
            )

        except ObjectDoesNotExist:
            return get_error_response("NOT A VALID REFRESH TOKEN")

        except ExpiredSignatureError:
            return get_error_response("NOT A VALID REFRESH TOKEN")

        except Exception as ex:
            return get_error_response(ex.args)
    else:
        return get_method_error(req, "POST")
