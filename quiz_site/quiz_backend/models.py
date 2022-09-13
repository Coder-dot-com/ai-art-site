from hashlib import blake2b
from uuid import uuid4
from django.db import models
from django.forms import CharField
from django.urls import reverse
from tinymce.models import HTMLField

from multicurrency.models import Currency
from django.contrib.auth import get_user_model

from accounts.models import UserPreferenceType

User = get_user_model()

# Create your models here.

class UserSession(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=250, blank=True, unique=True)
    time_created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True, null=True)
    latest_fb_clid = models.CharField(max_length=500, blank=True, null=True)
    latest_fbp = models.CharField(max_length=500, blank=True, null=True)
    latest_t_clid = models.CharField(max_length=500, blank=True, null=True)
    ip = models.CharField(blank=True, max_length=2000, null=True)
    user_agent = models.CharField(blank=True, max_length=2000, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    country_code = models.CharField(max_length=250, blank=True, null=True)
    add_user_agent_to_exclusion_list = models.BooleanField(default=False)

    def convert_amount_to_session_currency(self, amount_in_usd):
        amount_in_usd = float(amount_in_usd)
        #Return the rounded amount same as on frontend
        return round(round(amount_in_usd * self.currency.one_usd_to_currency_rate), 2)


    def __str__(self) -> str:
        return self.session_id
    
    


class Referrer(models.Model):
    user_session = models.ForeignKey(UserSession, null=True, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    referrer = models.CharField(max_length=250, blank=True, null=True)
    audience = models.CharField(max_length=250, blank=True, null=True)
    ad = models.CharField(max_length=250, blank=True, null=True)


class Category(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    enable_pixels = models.BooleanField(default=True)
    analytics_base = models.TextField(max_length=5000, blank=True)
    analytics_content_view = models.TextField(max_length=5000, blank=True)
    analytics_lead = models.TextField(max_length=5000, blank=True)    
    # analytics_init_checkout = models.TextField(max_length=5000, blank=True)
    analytics_purchase = models.TextField(max_length=5000, blank=True)



    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


    def __str__(self):
        return self.category_name


product_types = [
    ("subscription", "subscription"),
    ("once_only", "once_only"),
]

class Product(models.Model):

    product_name = models.CharField(max_length=200, unique=True)
    product_type = models.CharField(max_length=300, default="once_only", choices=product_types)
    stripe_price_id = models.CharField(max_length=300, blank=True, null=True)
    days_free_trial = models.IntegerField(null=True, blank=True)
    payment_description = HTMLField(max_length=1000, null=True, blank=True)
    sales_page_title = models.CharField(max_length=300)

    sales_page_copy_before_media = HTMLField(max_length=10000, blank=True)
    video_link = models.CharField(max_length=300, null=True, blank=True)
    video_title = HTMLField(max_length=300, null=True, blank=True)

    whats_included_title = HTMLField(max_length=750, blank=True)
    sales_page_cta = models.CharField(max_length=200, null=True, blank=True)
    cta_banner = models.CharField(max_length=200, null=True, blank=True)
    content_banner = HTMLField(max_length=5000, null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    sale_price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    main_image = models.ImageField(upload_to='photos/products', null=True, blank=True)
    created_date =  models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    num_sold = models.IntegerField(default=0)



    def __str__(self) -> str:
        return self.product_name

    
    def get_prod_page_rows(self):
        return ProductPageRow.objects.filter().order_by("position")

page_types = [
    ("image_left", "image_left"),
    ("image_right", "image_right"),
    ("video_left", "video_left"),
    ("video_right", "video_right"),
    ("story_box", "story_box"),


]



class ProductPageRow(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    position = models.IntegerField()
    page_type = models.CharField(max_length=1000, choices=page_types)
    row_image = models.ImageField(null=True, blank=True, upload_to="photos/products")
    row_video = models.FileField(null=True, blank=True, upload_to="media/products")
    video_thumbnail = models.ImageField(null=True, blank=True, upload_to="photos/products")

    media_title = models.CharField(max_length=500, null=True, blank=True)
    cta_text = models.CharField(max_length=500, null=True, blank=True)
    row_text = HTMLField(max_length=5000, null=True, blank=True)


quiz_type_choices = [
    ("setUserPreferences", "setUserPreferences"),
    ("feedback", "feedback"),
    ("updateUserPreferences", "updateUserPreferences"),

]

class Quiz(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quiz_type = models.CharField(default="setUserPreferences", max_length=300, choices=quiz_type_choices)
    name = models.CharField(max_length=300, unique=True)
    display_name = models.CharField(max_length=300)
    title = models.CharField(max_length=400)
    tagline = models.CharField(max_length=400, blank=True, null=True)
    second_tagline = models.CharField(max_length=400, blank=True, null=True)
    
    unique_id = models.CharField(max_length=400, unique=True, null=True, blank=True)
    banner_image = models.ImageField(null=True, blank=True)
    quiz_logo = models.ImageField(null=True, blank=True)



    ending_title = models.CharField(max_length=400,  null=True, blank=True)
    ending_content = HTMLField(max_length=7000, null=True, blank=True)
    ending_checkbox = models.BooleanField(default=False)
    ending_checkbox_text = models.CharField(max_length=700, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def get_questions(self):
        return Question.objects.filter(quiz=self).order_by('question_number')

    #Need to auto generate unique id and link on save

    def save(self, *args, **kwargs):

        if not self.unique_id:
            self.unique_id = str(uuid4())
            

        super(Quiz, self).save(*args, **kwargs)

    
    def get_absolute_url(self):
        return reverse('quiz', args=[self.unique_id])

    


question_types = [
    ("Single Choice", "Single Choice"),
    ("Multiple Choice", "Multiple Choice"),
    ("Sales Page", "Sales Page"),
    ("Text Input", "Text Input"),
    ("Image Input", "Image Input"),
    ("Email Input", "Email Input"),
    ("password", "password"),


]

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    #-question is then foreign keyed optionally to userpreference name
    user_preference_type = models.ForeignKey(UserPreferenceType, null=True, blank=True, on_delete=models.SET_NULL)
    question_type = models.CharField(max_length=300, choices=question_types)
    text_before_title = HTMLField(max_length=10000, null=True, blank=True)

    question_title = models.CharField(max_length=400)
    question_number = models.IntegerField()
    skippable = models.BooleanField(default=False)
    page_content = HTMLField(max_length=10000, null=True, blank=True)
    # question_video_link = models.CharField(max_length=1000, null=True, blank=True)
    image = models.ImageField(upload_to='quiz/images', null=True, blank=True)
    input_placeholder = models.CharField(max_length=300, null=True, blank=True)
    image_upload_number = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.quiz} | {self.question_title}"

    
    def get_question_choices(self):
        return QuestionChoice.objects.filter(question=self)


class QuestionChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.CharField(max_length=200)
    whats_included_text = models.CharField(max_length=500, null=True, blank=True)
    add_to_whats_included = models.BooleanField(default=False)
    prompt_text = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self) -> str:
        return self.option
    





class Response(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True)
    time_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    response_id = models.CharField(max_length=500, unique=True)
    session = models.ForeignKey(UserSession, on_delete=models.SET_NULL, null=True)
    steps_completed = models.CharField(max_length=500, null=True, blank=True)
    completed = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)

    email = models.EmailField(max_length=1000, null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def whats_included(self):
        return Answer.objects.filter(response=self, question_choice__add_to_whats_included=True).values_list('question_choice__whats_included_text', flat=True)
    




class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)
    question_choice = models.ManyToManyField(QuestionChoice, blank=True)
    time_added = models.DateTimeField(auto_now_add=True)
    answer = models.CharField(max_length=5000)

    def get_user_images(self):
        return UserImageUpload.objects.filter(answer=self)


class UserImageUpload(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="user_uploads/")













