from rest_framework.response import Response
from rest_framework import status


def validation_error_response(serializer):
    errors = serializer.errors

    # Get the first field with an error
    field = next(iter(errors))
    error = errors[field][0]

    # Handle "This field is required."
    if error == "This field is required.":
        message = f"{field.replace('_', ' ').title()} field is required."

    else:
        message = str(error)

    return Response(
        {
            "status": False,
            "message": message,
        },
        status=status.HTTP_200_OK,
    )