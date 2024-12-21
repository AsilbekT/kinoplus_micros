from rest_framework.response import Response


def standardResponse(status, message, data=None):
    return Response({
        "status": status,
        "message": message,
        "data": data
    })
