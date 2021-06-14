from django.db.models import Avg
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import mixins, permissions, viewsets

from . import filters, models, serializers
from .permissions import IsAdminAuthorStaffOrReadOnly, IsAdminOrReadOnly


class ListCreateDelViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    queryset = models.Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('-pk')
    filterset_class = filters.TitleFilter
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.TitleReadSerializer
        return serializers.TitleWriteSerializer

    def perform_create(self, serializer):
        category = self.request.data.get('category')
        genre = self.request.data.getlist('genre')
        if category is not None:
            category = get_object_or_404(models.Category, slug=category)
        if len(genre) > 0:
            genre = get_list_or_404(models.Genre, slug__in=genre)
        serializer.save(category=category, genre=genre)

    def perform_update(self, serializer):
        category = self.request.data.get('category')
        genre = self.request.data.getlist('genre')
        if category is not None:
            category = get_object_or_404(models.Category, slug=category)
            serializer.instance.category = category
        if len(genre) > 0:
            genre = get_list_or_404(models.Genre, slug__in=genre)
            serializer.instance.genre.set(genre, clear=True)
        serializer.save()


class GenreViewSet(ListCreateDelViewSet):
    queryset = models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    lookup_field = 'slug'
    search_fields = ['=name']
    permission_classes = [IsAdminOrReadOnly]


class CategoryViewSet(ListCreateDelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    lookup_field = 'slug'
    search_fields = ['=name']
    permission_classes = [IsAdminOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReviewSerializer
    permission_classes = [IsAdminAuthorStaffOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        title = get_object_or_404(models.Title, id=self.kwargs['title_id'])
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    permission_classes = [IsAdminAuthorStaffOrReadOnly,
                          permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        review = get_object_or_404(
            models.Review,
            id=self.kwargs['review_id'],
            title_id=self.kwargs['title_id']
        )
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(models.Review, id=self.kwargs['review_id'])
        return review.comments.all()
