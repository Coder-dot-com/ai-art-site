import datetime
from uuid import uuid4
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from quiz_backend.models import Answer, Question, QuestionChoice, Quiz, Response, UserSession

import stripe
from emails.models import UserEmail
from quiz_site.settings import STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY

from common.util.functions import event_id
from conversion_tracking.tasks import conversion_tracking
from django.contrib.auth import get_user_model, login
from django.contrib import messages

User = get_user_model()

stripe.api_key = STRIPE_SECRET_KEY
stripe_pub_key = STRIPE_PUBLIC_KEY


# Create your views here.


def _session(request):
    session_id = request.session.session_key
    if not session_id:

        request.session.save()
        session_id = request.session.session_key
    print("Session ID")
    print(session_id)
    
    if not session_id:
        session_id = uuid4()
    try:
        session = UserSession.objects.get(session_id=session_id)
    except UserSession.DoesNotExist:
        #Get refferer etc...

        session = UserSession.objects.create(session_id=session_id)
    except Exception as e:
        print("Error creating session")
        print(e)
    return session

def quiz(request, unique_id=None):

    # Use unique id to get quiz later on
    quiz = Quiz.objects.get(unique_id=unique_id)
    
    if request.user.is_authenticated and quiz.quiz_type == "setUserPreferences":
        messages.info(request, "Already logged in, to edit your preferences click edit below")
        return redirect('dashboard_preferences')


    elif not request.user.is_authenticated and quiz.quiz_type == 'updateUserPreferences':
        messages.info(request, "You must login to update preferences")
        return redirect('home')
        
    response_id = str(uuid4())
    
    #Conv tracking



    event_source_url = request.META.get('HTTP_REFERER')
    print("Source URL for product view")
    print(event_source_url)

    pv_event_unique_id = event_id()
    vc_event_unique_id = event_id()

    session = _session(request)

    
    try:
        # Need to fix this to ensure different ids
        conversion_tracking.delay(event_name="PageView", event_id=pv_event_unique_id, event_source_url=event_source_url, category_id=quiz.category.id, session_id=session.session_id)  
        conversion_tracking.delay(event_name="ViewContent", event_id=vc_event_unique_id, event_source_url=event_source_url, category_id=quiz.category.id, session_id=session.session_id)  
        print("tracking conversion")
    except Exception as e:
        print("failed conv tracking")

        print(e)

    


    context = {
        'quiz': quiz,
        'response_id': response_id,
        'vc_event_unique_id': vc_event_unique_id,
        'pv_event_unique_id': pv_event_unique_id,
    }
    return render(request, 'index_with_branch.html', context=context)


def submit_form(request, unique_id, response_id, ajax=None):
    user = None
    new_user = False
    if request.POST.get('website', False):
        print("Bot submitted form")
        return redirect('quiz', unique_id=unique_id)

    quiz = Quiz.objects.get(unique_id=unique_id)

    #Add session_id

    session = _session(request)
    #When add ajax submit first check for existing submission with response id
    try: 
        response = Response.objects.get(quiz=quiz, response_id=response_id, session=session)
    except:
        response = Response.objects.create(quiz=quiz, response_id=response_id, session=session)
    
    email = None

    for question_id in request.POST:
        #Set the response email
        if question_id.startswith('question_email_'):
            email = request.POST[question_id]
            response.email = email
            response.save()
            session.email = email
            session.save()


    for question_id in request.POST:         
        if question_id.startswith('question_'):
            question_db_id = question_id.split('_')[-1]

            question = Question.objects.get(id=question_db_id)

            question_choice = None

            answer = request.POST[question_id]

            try:
                answer_obj = Answer.objects.get(response=response, question=question)
            except:
                answer_obj = Answer()
                answer_obj.question = question
                answer_obj.response = response
                answer_obj.save()


            if question.question_type == "Multiple Choice":
                answers_list = request.POST.getlist(question_id)
                answer = ", ".join(answers_list)
                answer_obj.answer = answer
                answer_obj.question_choice.clear()
                answer_obj.save()
                for i in answers_list:
                    try:
                        question_choice = QuestionChoice.objects.get(question=question, option=i)
                        answer_obj.question_choice.add(question_choice)
                    except Exception as e:
                        print(e)
                        pass
            
            elif question.question_type == "password" and not ajax and not request.user.is_authenticated:
                password = request.POST[question_id]
                
                answer_obj.answer = "Password was added"
                answer_obj.save()

                #Create user using email and password
                username = uuid4()

                try:
                    user = User.objects.get(email=email)
                    messages.error(request, "An account already exists with this email please login")
                    return redirect('login_user')
                except:
                    pass



                try:
                    new_user = True
                    user = User.objects.create_user(username=username, email=email, password=password)
                except Exception as e:
                    print("registration error")
                    print(e)
                    user = None



            else:
                answer = request.POST[question_id]
                answer_obj.answer = answer
                answer_obj.save()

                try:
                    question_choice = QuestionChoice.objects.get(question=question, option=answer)
                    answer_obj.question_choice.add(question_choice)
                except Exception as e:
                    print(e)
                    pass


            answer_obj.save()



    #If statement to check if ajax or not before redirect

    answers_count = Answer.objects.filter(response=response).count()
    questions_count = Question.objects.filter(quiz=quiz).count()

    response.steps_completed = f"{answers_count}/{questions_count}" 
    response.save()



    # response.steps_completed = 

    if ajax:
        return HttpResponse(200)

    else:
        response.completed = True
        response.save()

    if user != None:

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

        #Associate response with user
        response.user = user
        response.save()
        #Here  create email object
        if new_user:
            email, x = UserEmail.objects.get_or_create(email=email)
            email.user= user
            email.promo_consent = True
            email.save()      
            return redirect(reverse('dashboard_home') + f"?nu=1")
        else:

            return redirect('dashboard_home')
    elif request.user.is_authenticated and quiz.quiz_type == 'updateUserPreferences':
        response.user = request.user
        response.save()
        messages.success(request, "Preferences saved!")
        return redirect('dashboard_preferences')
        
        












def tandc(request, unique_id):
    quiz = Quiz.objects.get(unique_id=unique_id)

    context = {
        'quiz': quiz,
    }
    return render(request, 'quiz/pages/tandc.html', context=context)


def privpolicy(request, unique_id):
    quiz = Quiz.objects.get(unique_id=unique_id)

    context = {
        'quiz': quiz,
    }

    return render(request, 'quiz/pages/privpolicy.html', context=context)

def deliveryinfo(request, unique_id):

    quiz = Quiz.objects.get(unique_id=unique_id)

    context = {
        'quiz': quiz,
    }
    return render(request, 'quiz/pages/deliveryinfo.html', context=context)


def refundpolicy(request, unique_id):
    quiz = Quiz.objects.get(unique_id=unique_id)

    context = {
        'quiz': quiz,
    }
    return render(request, 'quiz/pages/refundpolicy.html', context=context)


def checkout(request, unique_id, response_id):
    quiz = Quiz.objects.get(unique_id=unique_id)
    session = _session(request)
    payment_intent_id = None
    try:
        response = Response.objects.get(response_id=response_id, session=session)
    except Exception as e:
        print(e)
        return redirect('quiz', unique_id=unique_id)

    if quiz.product.sale_price:
        price_usd = quiz.product.sale_price

    else:
        price_usd = quiz.product.price
    
    
    non_sale_price_converted = session.convert_amount_to_session_currency(quiz.product.price)
    sale_price_converted = session.convert_amount_to_session_currency(quiz.product.sale_price)
    
    
    #Create stripe customer if product subscription

    customer = stripe.Customer.create(
    email=response.email,
    )
    print('customer', customer)
    customer_id = customer.id
    print(customer_id)

    price = session.convert_amount_to_session_currency(price_usd)
        
    currency = session.currency

    if quiz.product.product_type == "subscription":
        price_id = quiz.product.stripe_price_id

        try:
            # Create the subscription. Note we're expanding the Subscription's
            # latest invoice and that invoice's payment_intent
            # so we can pass it to the front end to confirm the payment
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{
                    'price': price_id,
                }],
                trial_period_days= quiz.product.days_free_trial,
                # trial_end=1652631902,
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
            )
            payment_intent_id = subscription.id

            if quiz.product.days_free_trial:
                setup_intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=["card"],
                usage = 'off_session'
  
                )

                client_secret = setup_intent.client_secret
            else:

                client_secret = subscription.latest_invoice.payment_intent.client_secret

            # print(dict(subscriptionId=subscription.id, clientSecret=subscription.latest_invoice.payment_intent.client_secret))

        except Exception as e:
            print(e)

        



        # Create payment intent
    else:
    


        intent = stripe.PaymentIntent.create(
            amount = int(price*100),
            currency = currency,
            payment_method_types = [
                "card",
            ],
            )

        client_secret = intent.client_secret
        payment_intent_id = intent.id



    #Create the order object here and order num
    yr = int(datetime.date.today().strftime('%Y'))
    dt = int(datetime.date.today().strftime('%d'))
    mt = int(datetime.date.today().strftime('%m'))
    d = datetime.date(yr,mt,dt)
    current_date = d.strftime("%Y%m%d")
    order = Order()
    


    order.product = quiz.product
    order.response = response
    order.quiz = quiz
    order.email = response.email
    order.order_total = price
    order.currency = currency
    order.order_total_usd = price_usd
    if payment_intent_id:
        order.payment_intent_id = payment_intent_id

    order.save()

    order.order_number = current_date + str(order.id)

    order.save()


    


    return_url = request.build_absolute_uri(reverse('success', kwargs={"payment_intent_id": payment_intent_id,
    }))

    #Conv tracking


    event_source_url = request.META.get('HTTP_REFERER')
    print("Source URL for product view")
    print(event_source_url)

    event_unique_id = event_id()
    session = _session(request)

    try:
        conversion_tracking.delay(event_name="InitiateCheckout", event_id=event_unique_id, event_source_url=event_source_url, category_id=quiz.category.id, session_id=session.session_id)
        print("tracking conversion")
    
    except Exception as e:
        print("failed conv tracking")
        print(e)

    print("pubkey", stripe_pub_key)

    context = {
        'quiz': quiz,
        'response': response,
        'client_secret': client_secret,
        'stripe_pub_key': stripe_pub_key,
        'return_url': return_url,
        'event_id': event_unique_id,
        
    }

    context['non_sale_price_converted'] =  non_sale_price_converted

    if sale_price_converted:
        context['sale_price_converted'] =  sale_price_converted

    return render(request, 'quiz/pages/checkout.html', context=context)



