from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from users.models import User

from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (IsAdminUser,)
    # filter_backends = (SearchFilter,)
    search_fields = ('username',)
    http_method_names = ('get', 'post',)
    lookup_field = 'id'
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        user = User.objects.get(request.user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
