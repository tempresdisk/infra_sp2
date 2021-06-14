import jwt
from django.conf import settings
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import CustomUser
from .permissions import HasAdminRole
from .serializers import UserSerializer


@api_view(['POST'])
def send_confirm_code(request):
    try:
        email = request.data['email']
    except KeyError:
        data = {'error': 'Invalid request'}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(CustomUser, email=email)
    token = jwt.encode({"email": email}, "secret", algorithm="HS256")
    email_body = (f'Hi {user.username}! Use this confirmation '
                  f'code to verify your account: {token}')
    send_mail(
        'Verify your account',
        email_body,
        settings.EMAIL_HOST_USER,
        (email,),
        fail_silently=False,
    )
    data = {'email': email}
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_access_token(request):
    try:
        email = request.data['email']
        confirm_code = request.data['confirmation_code']
    except KeyError:
        data = {'error': 'Invalid request'}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    try:
        payload = jwt.decode(confirm_code, "secret", algorithms=["HS256"])
        if (email != payload['email']):
            return Response({'error': 'Wrong confirm code for this email'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(CustomUser, email=payload['email'])
        if not user.is_verified:
            user.is_verified = True
            user.save()
        token = user.tokens()['access']
        return Response({'token': token}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
        return Response(
            {'error': 'Activation Expired'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except jwt.exceptions.DecodeError:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, HasAdminRole]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['username', ]
    search_fields = ['username', ]
    lookup_field = 'username'

    def perform_create(self, serializer):
        if self.request.data.get('role', False) == CustomUser.MODERATOR:
            serializer.save(is_staff=True)
        serializer.save()

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @me.mapping.patch
    def patch_profile(self, request, *args, **kwargs):
        serializer = UserSerializer(self.request.user,
                                    data=request.data,
                                    partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_200_OK)
