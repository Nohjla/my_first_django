from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from . import logic
from django.core.files.storage import FileSystemStorage
from difflib import SequenceMatcher, HtmlDiff
import os
from pathlib import Path
from django.http import HttpResponse, Http404
from django.urls import reverse
from .utils import generate_signed_url, validate_signed_token, archive_and_delete_old_media_files
BASE_DIR = Path(__file__).resolve().parent.parent
import numpy as np
file_storage = FileSystemStorage(location='/var/data/uploads')

def archive_and_delete_view(request):
    # Archive and delete old files
    archive_path = archive_and_delete_old_media_files()

    # Return the archive as a downloadable file
    with open(archive_path, 'rb') as archive_file:
        response = HttpResponse(archive_file, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{archive_path.split("/")[-1]}"'
        return response

def text_difference(text1, text2):
    """
    Compare two texts and return their differences line by line.
    """
    html_diff = HtmlDiff()
    diff_table = html_diff.make_table(text1, text2, fromdesc='Original', todesc='Modified')
    # return "\n".join(diff)
    return {'diff_table': diff_table}


def thank_you(request):
    context = {
        "object": "thank-you",
        "query": "very-much"
    }
    return render(request, "thank_you.html", context=context)

@login_required
def generate_url_view(request):
    base_url = request.build_absolute_uri(reverse('base:validate_url'))
    user_id = request.user.id  # Or any identifier
    signed_url = generate_signed_url(base_url, str(user_id), expiration=60)
    return render(request, 'generate_link.html', {"data": signed_url})

def validate_url_view(request):
    token = request.GET.get('token')
    if not token:
        raise Http404("Token not provided.")
    try:
        context = {}
        if request.method == 'POST':
            upload_file = request.FILES['document']
            approved = logic.check_files('pending ' + upload_file.name)
            pending = logic.check_files('approved ' + upload_file.name)
            if approved == True or pending == True:
                return render(request, 'upload.html', {"sample": "File already exist"})
            fs = FileSystemStorage()
            name = fs.save('pending ' + upload_file.name, upload_file)
            context['url'] = fs.url(name)
            data = validate_signed_token(token, max_age=60)
            return redirect("base:thank_you")
            # return render(request, 'thank_you.html', {"sample":data})
        data = validate_signed_token(token, max_age=60)  # 5 minutes    
        return render(request, 'upload.html', {"data":data})
    except Exception as e:
        return render(request, 'expired.html', {"data":e})


def get_doc_details():
    files_path = os.path.join(BASE_DIR, 'media')
    details = []
    arr = np.array(logic.full_details_pending())
    arr2 = np.array(logic.full_details_approved())
    score_test = 0
    for search_text in arr:
        file_result = {}
        for text in arr2:
            if search_text['file'] != text['file']:
                matches = SequenceMatcher(None, text['content'], search_text['content']).ratio()
                if matches > score_test:
                    score_test = matches
                    text_compared = text['file']
        compared_result = text_difference(logic.full_text(files_path + '\\' + search_text['file']), logic.full_text(files_path + '\\' + text_compared))
        file_result['file_name'] = search_text['file']
        file_result['file_path'] = search_text['path']
        file_result['compared_file'] = text_compared
        file_result['compared_text'] = compared_result
        file_result['scores'] = round(score_test, 4)           
        details.append(file_result)         
    return details
    
def upload_file(request):
    context = {}
    if request.method == 'POST':
        file = request.FILES['file']
        file_path = file_storage.save(file.name, file)
    return render(request, 'upload.html', {'file_path': f'/media/uploads/{file.name}'})

def user_logout(request):
    logout(request)
    return render(request, 'registration/logout.html', {})

def authView(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form" :form})

@login_required
def home(request):
    context = {
        "object": "test",
        "query": "sample"
    }
    if request.method == "GET":
        query_dict = request.GET
        query = query_dict.get("q")
        arr = logic.get_research(query)
        context = {
            "object": arr,
            "query": query
        }
    
    return render(request, "testing.html", context=context)

def save_docx(file_name):
    original_string = file_name
    substring_to_remove = "pending "
    updated_string = original_string.replace(substring_to_remove, "approved ")
    files_path = os.path.join(BASE_DIR, 'media')
    old_path = files_path +  '\\' + file_name
    new_path = files_path + '\\' + updated_string
    os.rename(old_path, new_path)
        
def delete_file(file_name):
    files_path = os.path.join(BASE_DIR, 'media')
    full_path = files_path +  '\\' + file_name
    try:
        if os.path.exists(full_path):
            os.remove(full_path)
        else:
            return HttpResponse("File not found.")
    except Exception as e:
        return HttpResponse(f"Error deleting file: {str(e)}")


@login_required
def dashboard(request):
    if request.method == 'POST':
        button_value = request.POST.get('submit')
        if "save" in button_value:
            original_string = button_value
            substring_to_remove = "save "
            updated_string = original_string.replace(substring_to_remove, "")
            save_docx(updated_string)
        
        if "delete" in button_value:
            original_string = button_value
            substring_to_remove = "delete "
            updated_string = original_string.replace(substring_to_remove, "")
            delete_file(updated_string)
    arr = get_doc_details()
    return render(request, "sample.html", {'data': arr})

