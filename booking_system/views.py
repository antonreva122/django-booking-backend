from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    """
    API Root - Lists all available endpoints
    """
    return Response({
        'users': {
            'register': reverse('register', request=request, format=format),
            'login': reverse('login', request=request, format=format),
            'logout': reverse('logout', request=request, format=format),
            'profile': reverse('profile', request=request, format=format),
            'profile_update': reverse('profile_update', request=request, format=format),
            'password_change': reverse('password_change', request=request, format=format),
            'password_reset_request': reverse('password_reset_request', request=request, format=format),
            'password_reset_confirm': reverse('password_reset_confirm', request=request, format=format),
            'token_refresh': reverse('token_refresh', request=request, format=format),
        },
        'bookings': {
            'bookings_list': request.build_absolute_uri('/api/bookings/list/'),
            'resources_list': request.build_absolute_uri('/api/bookings/resources/'),
            'availability_check': request.build_absolute_uri('/api/bookings/availability/'),
        },
        'admin': request.build_absolute_uri('/admin/'),
    })
