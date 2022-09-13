from datetime import datetime, timedelta
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from accounts.models import Profile
from dashboard.forms import AccountDetailsForm, ChangePasswordForm

from subscriptions.models import SubscriptionChoices, UserPaymentStatus, UserSubscriptions
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
import stripe
from quiz_site.settings import STRIPE_SECRET_KEY
from quiz_backend.views import _session
from quiz_backend.models import Answer, Quiz, Response
from django.db.models import Q

stripe.api_key = STRIPE_SECRET_KEY



UserModel = get_user_model()

# Create your views here.

@login_required
def dashboard_home(request):
    context = {}
    
    if request.user.date_joined.replace(tzinfo=None) > datetime.now().replace(tzinfo=None) - timedelta(minutes=1) and request.GET.get('nu'):
            context['new_user'] = True
            # lead_event_id = event_id()
            # context['lead_event_id'] = lead_event_id
            # print("lead")
            # conversion_tracking.delay(event_name="Lead", event_id=lead_event_id, event_source_url=event_source_url, category_id=quiz.category.id, session_id=session.session_id)  

    return render(request, "dashboard/index.html", context=context)


@login_required
def subscription_page_dashboard(request):
    context = {}

    return render(request, 'dashboard/subscription_page.html', context=context)


@login_required
def account_details_dashboard(request):
    user = request.user
    profile_obj = Profile.objects.get(user=user)

    form = AccountDetailsForm(request.POST or None)

    user = UserModel.objects.get(pk=request.user.id)

    if form.is_valid():
            email = form.cleaned_data.get('email')

            if email:
                user.email = email
                user.save()
            
            messages.success(request, "Success, details updated!")
            profile_obj.save()

            return redirect('account_details_dashboard')

            
    
    context = {
        'form': form,
    }

    return render(request, 'dashboard/account_details_dashboard.html', context=context)


@login_required
def change_password_dashboard(request):
    user = request.user

    form = ChangePasswordForm(request.POST or None)

    
    user = UserModel.objects.get(pk=request.user.id)

    if form.is_valid():
            current_password = form.cleaned_data.get('current_password')
            new_password = form.cleaned_data.get('new_password')
             
            if authenticate(request=None, username=user.username ,password=current_password):
                #change password to new password
                user.set_password(new_password)
                user.save()

                old_session = _session(request)
                login(request, user)
                new_session = _session(request)

                #swap the session ids
                if not new_session.ip:
                    new_id = new_session.session_id
                    new_session.delete()
                    old_session.session_id = new_id
                
                old_session.user = user
                old_session.save()

                
                messages.success(request, "Success, password updated!")
            else:
                print("incorrct pass")
                messages.error(request, "Incorrect password")
     
    
    context = {
        'form': form,
    }

    return render(request, 'dashboard/change_password_dashboard.html', context=context)


@login_required
def billing_history(request):
    user = request.user
    context = {}

    user_payment_status = UserPaymentStatus.objects.get(user=user)
    user_subscriptions =  UserSubscriptions.objects.filter(user_payment_status=user_payment_status).order_by('date_subscribed').reverse()

    invoices_data = []
    for subscription in user_subscriptions:
        subscription_id = subscription.subscription_id
        #Get all invoices associated with this and add to list
    
        subscription_invoices = stripe.Invoice.list(limit=100, subscription=subscription_id)
        print(subscription_invoices['data'][0]) #Last 0 is invoice number so check len if > 100
        #test this
        
        invoices = (subscription_invoices['data'])

        for invoice in invoices:
            unix_time = invoice['created']
            created = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d')
            if not invoice['amount_paid'] == 0:

                invoice_data = {

                    'amount_due': invoice['amount_paid']/100,
                    'currency': invoice['currency'],
                    'created': created,
                    'status': invoice['status'],
                    'link': invoice['hosted_invoice_url'],
                }
                invoices_data.append(invoice_data)


    context['invoices_data'] = invoices_data
        #if returned objects over limit then for loop with starting after to get others

    return render(request, 'dashboard/billing_history.html', context=context)


@login_required
def dashboard_preferences(request):
    user = request.user
    current_user_response = Response.objects.filter(
        Q(quiz__quiz_type="setUserPreferences") | Q(quiz__quiz_type="updateUserPreferences"),
        completed=True, user=request.user).latest('last_modified')
    
    current_user_preferences = Answer.objects.all().exclude(question__user_preference_type__isnull=True).filter(
        response=current_user_response)
            
    
    #Get quiz  by updatepreferences quiz type, using this type add edit link on page
    #  to quiz page
    try:
        update_preferences_quiz = Quiz.objects.filter(quiz_type="updateUserPreferences")[0]
    except:
        update_preferences_quiz = Quiz.objects.filter(quiz_type="setUserPreferences")[0]

    context = {
        'current_user_preferences': current_user_preferences,
        'update_preferences_quiz': update_preferences_quiz,
    }

    return render(request, 'dashboard/preferences.html', context=context)
