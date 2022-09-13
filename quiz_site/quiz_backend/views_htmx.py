from uuid import uuid4
from django.http import HttpResponse
from django.shortcuts import render

from quiz_backend.models import Answer, Question, Quiz, Response, UserImageUpload
from .views import _session
import os



def image_upload(request, unique_id, response_id):
    print("Image upload")

    quiz = Quiz.objects.get(unique_id=unique_id)

    #Get the response or create
    session = _session(request)

    try: 
        response = Response.objects.get(quiz=quiz, response_id=response_id, session=session)
    except:
        response = Response.objects.create(quiz=quiz, response_id=response_id, session=session)
    
    #Get the answer for the question if not then create
    too_many_images=False

    for question_id in request.FILES:        
        if question_id.startswith('image_'):
            question_db_id = question_id.split('_')[-1]
            question = Question.objects.get(id=question_db_id)
            try:
                answer_obj = Answer.objects.get(response=response, question=question)
            except:
                answer_obj = Answer()
                answer_obj.question = question
                answer_obj.response = response
                answer_obj.save()

            images = request.FILES.getlist(question_id)



            for image in images:
                if image.size < 20000000 and image.size > 100:
                    file_name = image.name
                    file_ext = os.path.splitext(file_name)[1]
                    if file_ext == '.jpeg':
                        file_ext = '.jpg'


                    image.name = f"{uuid4()}{file_ext}"
                    if UserImageUpload.objects.filter(answer=answer_obj).count() < question.image_upload_number:
                        UserImageUpload.objects.create(image=image, answer=answer_obj)
                    else:
                        too_many_images=True

    user_images = UserImageUpload.objects.filter(answer=answer_obj)
    user_image_count = user_images.count()
    context = {
        'quiz': quiz,
        'question': question,
        'response_id': response_id,
        'user_images': user_images,
        'user_image_count': user_image_count,
        'too_many_images': too_many_images,


    }
    return render(request, 'quiz/htmx_image.html', context=context)




def delete_image(request, unique_id, response_id, user_image_id):
    session = _session(request)
    quiz = Quiz.objects.get(unique_id=unique_id)


    try: 
        response = Response.objects.get(quiz=quiz, response_id=response_id, session=session)
    except:
        return HttpResponse(500)

    user_image = UserImageUpload.objects.get(answer__response=response, id=user_image_id)
    user_image.delete()
    question = user_image.answer.question

    user_images = UserImageUpload.objects.filter(answer=user_image.answer)
    user_image_count = user_images.count()

    context = {
        'quiz': quiz,
        'question': question,
        'response_id': response_id,
        'user_images': user_images,
        'user_image_count': user_image_count,
    }
    return render(request, 'quiz/htmx_image.html', context=context)
