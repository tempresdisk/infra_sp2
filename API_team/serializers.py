from django.shortcuts import get_object_or_404

from rest_framework import serializers, validators

from . import models


class TitleToReviewDefault:
    requires_context = True

    def __call__(self, serializer_field):
        title_id = serializer_field.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(models.Title, id=title_id)
        return title


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id']
        model = models.Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id']
        model = models.Category


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(max_value=10, min_value=1)

    class Meta:
        fields = '__all__'
        model = models.Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, required=False, read_only=True)
    category = CategorySerializer(required=False)

    class Meta:
        fields = '__all__'
        model = models.Title


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=models.CustomUser.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        write_only=True,
        queryset=models.Title.objects.all(),
        default=TitleToReviewDefault()
    )

    class Meta:
        fields = '__all__'
        model = models.Review
        validators = [
            validators.UniqueTogetherValidator(
                queryset=models.Review.objects.all(),
                fields=['author', 'title'],
                message='Вы уже оставляли отзыв на это произведение'
            )
        ]
        extra_kwargs = {
            'score': {
                'error_messages': {
                    'min_value': ('Оценка должна быть числом '
                                  'в пределах от 1 до 10'),
                    'max_value': ('Оценка должна быть числом '
                                  'в пределах от 1 до 10'),
                }
            }
        }


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = models.Comment
