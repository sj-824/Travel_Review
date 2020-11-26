from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.base_user import BaseUserManager
# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username and password are required. Other fields are optional.
    """
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        #abstract = True # ここを削除しないといけないことを忘れない！！！！！！！！！！

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)



class AnimeModel(models.Model):
    CATEGORY_GENRE = [
        ('SF','SF'),('ギャグ','ギャグ'),('恋愛','恋愛'),('青春','青春'),('ホラー','ホラー'),('日常','日常'),('ミステリー','ミステリー'),('バトル','バトル'),
            ]
    CATEGORY_CORP = [
        ('京都アニメーション','京アニ'),('ufotable','ufotable'),('A-1 Pictures','A-1 Pictures'),('P.A.WORKS','P.A.WORKS'),('サンライズ','サンライズ'),('シャフト','シャフト')
            ]

    anime_title = models.CharField(max_length = 100)
    anime_title_abb = models.CharField(max_length = 100)
    anime_start = models.DateField(auto_now_add = False, null = True)
    anime_genre = models.CharField(max_length = 15, choices = CATEGORY_GENRE)
    anime_corp = models.CharField(max_length = 15, choices = CATEGORY_CORP)
    anime_img = models.ImageField(upload_to = '')

class ReviewModel(models.Model):
    user_title = models.CharField(max_length = 50)
    user_review = models.TextField()
    post_date = models.DateField(auto_now_add = True)
    user_name = models.ForeignKey(User,to_field = 'username', on_delete=models.CASCADE)
    user_Anime = models.ForeignKey(AnimeModel,on_delete=models.CASCADE)
    
    VALUE_CATEGORY = ((1,1),(2,2),(3,3),(4,4),(5,5))
    user_value1 = models.IntegerField(choices = VALUE_CATEGORY,null = True)
    user_value2 = models.IntegerField(choices = VALUE_CATEGORY,null = True)
    user_value3 = models.IntegerField(choices = VALUE_CATEGORY,null = True)
    user_value4 = models.IntegerField(choices = VALUE_CATEGORY,null = True)
    user_value5 = models.IntegerField(choices = VALUE_CATEGORY,null = True)
    user_value_ave = models.DecimalField(null = True,max_digits = 2, decimal_places = 1)
