from django.core import validators
from django.db import models

from account.models import CustomUser
from .validators import year_validator


class Title(models.Model):
    name = models.CharField(
        verbose_name='Имя произведения',
        max_length=100,
    )
    year = models.SmallIntegerField(
        verbose_name='Год создания',
        blank=True,
        null=True,
        validators=[year_validator],
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        max_length=500,
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        to='Genre',
        verbose_name='Жанр',
        blank=True,
        related_name='titles',
    )
    category = models.ForeignKey(
        to='Category',
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
    )

    class Meta:
        ordering = ['-pk']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='titles_name_category_uniquetogether',
            )
        ]

    def __str__(self):
        return f'{self.category}: {self.name}'


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Наименование жанра',
        max_length=30,
        unique=True,
    )
    slug = models.SlugField(
        max_length=30,
        unique=True,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        verbose_name='Наименование категории',
        max_length=30,
        unique=True,
    )
    slug = models.SlugField(
        max_length=30,
        unique=True,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Название произведения',
        related_name='reviews'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор отзыва'
    )
    score = models.PositiveIntegerField(
        validators=[
            validators.MinValueValidator(1, message='Число в пределах 1-10'),
            validators.MaxValueValidator(10, message='Число в пределах 1-10')
        ]
    )
    pub_date = models.DateTimeField('дата создания отзыва', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='review'
            )
        ]

    def __str__(self):
        return (f'Отзыв {self.author.username} o '
                f'{self.title.category}: {self.title.name}')


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Комментируемое ревью',
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст комментария к отзыву')
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments'
    )
    pub_date = models.DateTimeField('дата создания комментария',
                                    auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return (f'Комментарий {self.author.username} к отзыву '
                f'{self.review.author.username} о '
                f'{self.review.title.category}: {self.review.title.name}')
