from django.contrib import admin

from conversion_tracking.models import Pixel

from .models import Answer, Category, Product, ProductPageRow, Question, QuestionChoice, Quiz, Referrer, Response, UserSession
from django.utils.safestring import mark_safe
# Register your models here.


class QuestionChoiceInline(admin.TabularInline):
    model = QuestionChoice
    extra = 3

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3
    ordering = ("question_number",)


class PixelInline(admin.TabularInline):
    model = Pixel
    extra = 1


class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline,]

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz',  'question_title', 'user_preference_type']
    inlines = [QuestionChoiceInline,]


class CategoryAdmin(admin.ModelAdmin):
    inlines = [PixelInline]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuestionChoice)


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class ResponseAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ['id', 'quiz', 'time_added', 'display_latest_ref', 'last_modified', 'email', 'steps_completed', 'completed', 'purchased', 'response_id', 'session', 'user']
    
    def display_latest_ref(self, obj):
        user_referrers = ""
        referrers = None
        
        if obj.user:
            
            referrers = Referrer.objects.filter(user_session__user=obj.user).order_by('time_created').reverse()

        elif obj.session:
            referrers = Referrer.objects.filter(user_session=obj.session).order_by('time_created').reverse()
        if referrers:
            for ref in referrers:
                user_referrers += f"{ref.referrer} - {ref.audience} - {ref.ad} - <br>{ref.time_created.date()} {ref.time_created.strftime('%I:%M%p')} <br><hr>"
        return mark_safe(user_referrers)

        
class ReferrerInline(admin.TabularInline):
    model = Referrer
    extra = 1

class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'time_created', 'user', 'user_agent', 'add_user_agent_to_exclusion_list', 'country_code', 'ip', 'email', 'latest_fbp']
    list_editable = ['add_user_agent_to_exclusion_list']
    inlines = [ReferrerInline]

class ProductRowInline(admin.TabularInline):
    model = ProductPageRow
    extra = 1

class ProductPageAdmin(admin.ModelAdmin):
    inlines = [ProductRowInline]


admin.site.register(Response, ResponseAdmin)
admin.site.register(Answer)

admin.site.register(Product, ProductPageAdmin)

admin.site.register(Category, CategoryAdmin)

admin.site.register(UserSession, UserSessionAdmin)