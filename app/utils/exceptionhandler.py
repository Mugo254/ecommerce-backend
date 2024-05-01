import json
from xml.dom import ValidationErr
from httplib2 import Response
from rest_framework import response, status
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):

    handlers = {
        'ValidationError': _handle_validation_error,
        'Http404': _handle_not_found,
        'PermissionDenied': _handle_generic_error,
        'NotAuthenticated': _handle_authentication_error,
        'NotFound': _handle_not_found,
    }

    response = exception_handler(exc, context)

    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        # print("Waaah")
        return handlers[exception_class](exc, context, response)
    return response

    # print("Waaah"+str(exc))
    # exc_list = str(exc).split("DETAIL: ")

    # return Response({"error":exc_list[-1]},status=403)


def _handle_authentication_error(exc, context, response):

    # print(exc)

    response.data = {
        'error_type': "NotAuthenticated",
        'error': str(exc),
        'status_code': response.status_code
    }

    return response


def _handle_not_found(exc, context, response):

    response.data = {
        'error_type': "NotFound",
        'error': "Object not found",
        'status_code': response.status_code
    }

    return response


def _handle_validation_error(exc, context, response):
    n = 0
    finalError = ""
    for x in exc.detail:
        if n == 0:
            errMsg = str(exc.detail[x]).split("string=")[1].split(",")[0]
            if "this field" in errMsg.lower():
                x = x.replace("_", " ")
                finalError = errMsg.lower().replace("this field", x)
                finalError = finalError.capitalize()
                finalError = finalError.replace("'", "")

            else:
                finalError = errMsg
                finalError = finalError.capitalize()
                finalError = finalError.replace("'", "")

        n = n+1

    # print(finalError.capitalize())

    response.data = {
        'error_type': "ValidationError",
        'error': finalError.capitalize(),
        'status_code': response.status_code
    }

    return response


def _handle_generic_error(exc, context, response):
    # print(exc)

    response.data = {
        'error': str(exc),
        'status_code': response.status_code
    }

    return response
