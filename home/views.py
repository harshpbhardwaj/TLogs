from django.shortcuts import render, redirect
from datetime import datetime, timedelta
# from home.models import Login
from home.models import Tlogs, Tlog_body, Login, Tlog_comment
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.template.loader import render_to_string
from django.db.models import F, Count, Sum, Subquery, OuterRef
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from home.serializers import HexaSerializers, BodySerializers, CommentSerializers
import re
import json
from django.core.mail import EmailMessage, EmailMultiAlternatives
import string
import random
from django.http import HttpRequest
from django.utils.html import strip_tags
from hashlib import sha256
import requests

class HexaViewSet(viewsets.ModelViewSet):
    queryset=Tlogs.objects.all()
    serializer_class=HexaSerializers

    @action(detail=True,methods=['get'])
    def body(self, request, pk=None):
        try:
            t_id=Tlogs.objects.get(pk=pk)
            body=Tlog_body.objects.filter(tlog=t_id)
            body_serializer=BodySerializers(body,many=True,context={'request':request})
            return Response(body_serializer.data)
        except Exception as e:
            print(e)
            return Response({
                'message':str(e)
            })
    @action(detail=True,methods=['get'])
    def comments(self, request, pk=None):
        try:
            t_id=Tlogs.objects.get(pk=pk)
            comment=Tlog_comment.objects.filter(tlog=t_id)
            comment_serializer=CommentSerializers(comment,many=True,context={'request':request})
            return Response(comment_serializer.data)
        except Exception as e:
            print(e)
            return Response({
                'message':str(e)
            })
class BodyViewSet(viewsets.ModelViewSet):
    queryset=Tlog_body.objects.all()
    serializer_class=BodySerializers
class CommentViewSet(viewsets.ModelViewSet):
    queryset=Tlog_comment.objects.all()
    serializer_class=CommentSerializers

def encrypt_now(string):
    return sha256(string.encode('utf-8')).hexdigest()
def get_this_month():
    this_month = Tlogs.objects.filter(publish=1).filter( date__gte = datetime.now() - timedelta(days=28)).order_by('-views').values()[:2]
    return make_tlog_body(this_month)
def id_generator(size=50, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def get_top_users():
    # First, create a subquery to calculate the sum of views for each email
    email_counts = Tlogs.objects.filter(publish=1).values('email').annotate(email_count=Count('email')).order_by('-email_count')
    # Then, annotate the main queryset with the rank of each email based on the sum of views
    top_3_emails = list(email_counts.values_list('email', flat=True)[:3])
    top_users = []
    for email in top_3_emails:
        top_users.append(list(Login.objects.filter( email=email ).values()[:1])[0])
    return top_users
    
def add_to_footer(context):
    a = {
            "top_users": get_top_users(),
            "monthly_top": get_this_month()
        }
    context.update(a)
    return context
def get_news(request):
    url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'sources': 'techcrunch',
        'apiKey': 'ef43d1a4318b4b35a6bca82965e8cd48'
    }
    response = requests.get( url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data
    return False

# Create your views here.
def index(request):
    if request.method == "GET":
        # data = Tlogs.objects.filter(publish=1).order_by('-id').values()[:6]
        data = Tlogs.objects.filter(publish=1).order_by('-id').values()[:6]
        my_data = make_tlog_body(data)
        trending = Tlogs.objects.filter(publish=1).filter( date__gte = datetime.now() - timedelta(days=10)).order_by('-views').values()[:3]
        trending_tlogs = make_tlog_body(trending)
        this_week = Tlogs.objects.filter(publish=1).filter( date__gte = datetime.now() - timedelta(days=7)).order_by('-views').values()[:2]
        weekly_top = make_tlog_body(this_week)

        



        tlog_count = Tlogs.objects.filter(publish=1).all().count()
        users_count = Login.objects.all().count()
        
        context = {
            'tlogs': my_data,
            'tlog_count': tlog_count,
            'users_count': users_count,
            'trending_tlogs': trending_tlogs,
            'weekly_top':weekly_top,
            'news': get_news(request)
        }
        context = add_to_footer(context)
        return render(request, 'index.html', context)
    if request.method == "POST":
        email = request.POST.get('email')
        password = encrypt_now(request.POST.get('password'))
        if request.POST.get('type') == "signup":
            phone = request.POST.get('phone')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            if not User.objects.filter(email=email).exists():
                if (request.POST.get('password') == request.POST.get('cpassword')):
                    city = request.POST.get('city')
                    state = request.POST.get('state')
                    country = request.POST.get('country')
                    terms = request.POST.get('terms')
                    verification_key = email+id_generator()
                    verification_key_datetime = datetime.now()
                    base_url = request.build_absolute_uri('/')
                    body = "Hello "+ fname +',<br>Click on the link to verify your email address.<br>' + base_url +"maildomainverify/" + verification_key + " <br>Feel free to contact."
                    loginz = Login(email=email, phone=phone, password=password, verified=0, verification_key=verification_key, verification_key_datetime=verification_key_datetime, city=city, state=state, country=country, terms=terms, date=datetime.now())
                    loginz.save()
                    

                    # Assuming you have your HTML template file saved in 'templates/email_template.html'
                    html_content = render_to_string('email_verification_template.html', {'fname': fname, 'base_url': base_url, 'verification_key': verification_key})

                    # Create an instance of EmailMultiAlternatives to send both HTML and plain text versions of the email
                    mkemail = EmailMultiAlternatives('Verify Your Email', strip_tags(html_content), 'tlogs@harx.online', [email])
                    mkemail.attach_alternative(html_content, 'text/html')
                    mkemail.send()


                    user = User.objects.create_user(username=email, email=email, password=password)
                    user.first_name = fname
                    user.last_name = lname
                    user.save()
                    messages.success(request, 'Congrats! '+fname+' '+lname+', You are a registered user now.')
                else:
                    messages.danger(request, 'Incorrect Password!')
            else:
                messages.warning(request, 'Try login again!')
        else:
            print('lol')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
            else:
                messages.warning(request, 'Incorrect Email or Password!', extra_tags = email)
    return redirect('/')
    # return JsonResponse({'data':context})

def maildomainverify(request, id):
    verification_key = id
    update = Login.objects.filter(verification_key = verification_key).update(verified="1")
    messages.success(request, 'Congrats! Your email is verified now.')
    return redirect('/')

def reset_password_mail(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            login_obj = Login.objects.filter(email=email).values()[:1][0]
        except Login.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
            return redirect('/')
        
        verification_key = email + id_generator()
        verification_key_datetime = datetime.now()
        base_url = request.build_absolute_uri('/')
        
        Login.objects.filter(email=email).update(verification_key = verification_key, verification_key_datetime = verification_key_datetime, verified = 2)
        
        # Send reset password email
        html_content = render_to_string('email_password_reset.html', {'fname': login_obj['fname'], 'base_url': base_url, 'reset_key': verification_key})
        email = EmailMultiAlternatives('Reset your password', strip_tags(html_content), 'tlogs@harx.online', [email])
        email.attach_alternative(html_content, 'text/html')
        email.send()
        
        messages.success(request, 'Please check your email and follow the instructions to reset your password.')
        return redirect('/')
    else:
        messages.error(request, "Can't reset now! Please try after sometime.")
        return redirect('/')

def reset_password(request, id):
    if id != 'set-password':
        try:
            verification_key = id
            obj = Login.objects.filter(verification_key=verification_key).values()[:1][0]
            current_time = datetime.now()
            time_difference = current_time - obj['verification_key_datetime']
            
            # Check if the verification key is expired
            if time_difference > timedelta(hours=2):
                messages.error(request, 'Link Expired!')
                return redirect('/')
            # Check if the verification key is pending verification
            if obj['verified'] == '2':
                Login.objects.filter(verification_key=verification_key).update(verified = 3)
                messages.success(request, 'Please set a new password!')
                context = {"verification_key": verification_key}
                return render(request, 'new-password.html', context)
            else:
                messages.error(request, 'Invalid Link!')
                return redirect('/')
        except Login.DoesNotExist:
            messages.error(request, 'Invalid Link!')
            return redirect('/')
    else:
        verification_key = request.POST.get("verification_key")
        password = encrypt_now(request.POST.get("password"))
        try:
            obj = Login.objects.filter(verification_key=verification_key).values()[:1][0]
            current_time = datetime.now()
            time_difference = current_time - obj['verification_key_datetime']
            # Check if the verification key is expired
            if time_difference > timedelta(hours=2):
                messages.error(request, 'Link Expired!')
                return redirect('/')
            # Check if the verification key is in the correct state
            if obj['verified'] == '3':
                # Hash the password before saving
                Login.objects.filter(verification_key=verification_key).update(password = password)
                user = User.objects.get(username=obj['email'], email=obj['email'])
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)
                Login.objects.filter(verification_key=verification_key).update(verified = 1)
                messages.success(request, 'Password has been changed! Please try logging in.')
            else:
                messages.error(request, 'Invalid Link!')
        except Login.DoesNotExist:
            messages.error(request, 'Invalid Link!')
    return redirect('/')




def sign_out(request):
    logout(request)
    messages.info(request, 'User signed out!')
    return redirect('/')

def about(request):
    base_url = request.build_absolute_uri('/')
    print(base_url+"maildomainverify")
    return redirect('/')
    # return render(request, 'pages/basic-grid.html')


def contact(request):
    email = EmailMessage('Subject', 'Body', 'tlogs@harx.online', ['harshpratap652@gmail.com'])
    email.send()
    return redirect('/')
    # return render(request, 'pages/basic-grid.html')

    
def profile(request):
    username = None
    if request.user.is_authenticated:
        username = request.user.username
        data = Login.objects.filter(email = username).values()[:1][0]
        t_data = Tlogs.objects.filter(email = username).order_by('-id').values()
        my_tlogs = make_tlog_body(t_data)
        context = {
            "profile" : data,
            "tlogs" : my_tlogs
        }
        context = add_to_footer(context)
        return render(request, 'profile.html', context)    
def profiles(request, id):
    username = None
    if request.user.is_authenticated:
        username = id
        data = Login.objects.filter(email = username).values()[:1][0]
        t_data = Tlogs.objects.filter(publish=1).filter(email = username).order_by('-id').values()
        my_tlogs = make_tlog_body(t_data)
        context = {
            "profile" : data,
            "tlogs" : my_tlogs
        }
        context = add_to_footer(context)
        return render(request, 'profile.html', context)
    messages.warning(request, 'Login first')
    return redirect('/')
        

def view(request, id):
    username = None
    can_view = True
    # can_view = request.user.is_authenticated
    if can_view:
        if request.user.is_authenticated:
            email = request.user.username
            t_data = Tlogs.objects.filter(id = id).values()[0]
            t_body = Tlog_body.objects.filter(tlog_id = id).values()
            t_comment = Tlog_comment.objects.filter(tlog_id = id).values()
        else:
            t_data = Tlogs.objects.filter(publish=1).filter(id = id).values()
            if len(t_data) == 0:
                messages.warning(request, "Can't access!")
                return redirect('/')
            else:
                t_data = t_data[0]
            t_body = Tlog_body.objects.filter(tlog_id = id).values()
            t_comment = Tlog_comment.objects.filter(tlog_id = id).values()
        Tlogs.objects.filter(publish=1).filter(id = id).update(views=F("views") + 1)
        tl_body = []
        pattern = r'\*\*(.*?)\*\*'
        j = 0
        for x in t_body:
            text_bold = re.sub(pattern, r'<b>\1</b>', x["body"])
            pattern_heading = r'(?m)^##(.*?)$'
            body_head = re.sub(pattern_heading, r'<br><h3>\1</h3>', text_bold)
            result = body_head.replace('\n', '<br>')
            rst = result.replace("</h3><br><br>", "</h3>").replace("</h3><br>", "</h3>").replace("<br><br><h3>", "<h3>")
            img_position = "r"
            if x['image'] != '':
                if j > 0:
                    if t_body[j-1]['image'] != '':
                        img_position = ""
                if (j+1) < len(t_body):
                    if t_body[j+1]['image'] != '':
                        img_position = ""
            tl_body.append({
                'id':x['id'],
                'tlog_id':x['tlog_id'],
                "body":rst,
                'image':x['image'],
                'img_position':img_position,
                'email':x['email'],
                'title':x['title'],
                'date':x['date']
                })
            j = j+1
        context = {
            "t_id" : id,
            "tlog" : t_data,
            "tlog_body" : tl_body,
            "tlog_comment" : t_comment
        }
        context = add_to_footer(context)
        return render(request, 'view.html', context)
        # return JsonResponse(context)

def post(request):
    username = None
    can_view = True
    # can_view = request.user.is_authenticated:
    context = {
        "a":"a"
    }
    if can_view:
        return render(request, 'edit_view.html', context)
        # return JsonResponse(context)


# function
def make_tlog_body(data):
    my_data = []
    for x in data:
        b_data = Tlog_body.objects.filter(tlog_id=x['id']).exclude(body__isnull=True).exclude(body__exact='').order_by('id').values()[:1]
        body = ''
        if b_data:
            body = b_data[0]['body']
        b_image = Tlog_body.objects.filter(tlog_id=x['id']).exclude(image__isnull=True).exclude(image__exact='').order_by('id').values()[:1]
        image = ''
        if b_image:
            image = b_image[0]['image']
        body1 = body.splitlines()
        body2 = []
        for i in body1:
            if i.startswith('##'):
                j = "<h2>" + i + "</h2>"
                body2.append(j)
            else:
                body2.append(i)
        body3 = " ".join(body2)
        my_data.append(
            {
                't_id': x['id'],
                'title': x['title'],
                'email': x['email'],
                'views': x['views'],
                'date': x['date'],
                'body': " ".join(body3.split(".")[0:1]),
                # 'body' : " ".join(body2),
                'image': image,
                'publish': x['publish']
            }
        )
    return my_data



# form posts
def add_new_comment(request):
    if (request.user.is_authenticated)*(request.method == "POST"):
        email = request.user.username
        #create new tlog
        if 'comment' in request.POST:
            comment = request.POST.get("comment")
            t_id = request.POST.get("tlog_id")
            Tlog_com = Tlog_comment(tlog_id=t_id, comment=comment, email=email, date=datetime.now())
            Tlog_com.save()
            page = 'view/' + str(t_id)
            return redirect(page)
        else:
            return redirect('/')
    else:
        messages.warning(request, 'Login First!')
        return redirect('/')

# ajax links
def add_new_tlog(request):
    if (request.user.is_authenticated)*(request.method == "POST"):
        email = request.user.username
        #create new tlog
        if 'title' in request.POST:
            title = request.POST.get("title")
            Tlog = Tlogs(email=email, title=title, date=datetime.now())
            Tlog.save()
            t_id = Tlog.id
            html = title
            return JsonResponse({'t_id':t_id, 'mystring':html})

        #add new para to tlog_body
        elif 'new_body_text' in request.POST:
            t_id = request.POST.get("t_id")
            title = request.POST.get("body_title")
            body = request.POST.get("new_body_text")
            image = ''
            Tlog_data = Tlog_body(tlog_id=t_id, body=body, image=image, email=email, title=title, date=datetime.now())
            Tlog_data.save()
            tbody_id = Tlog_data.id
            html ='<p class="lead" id="para_'+str(tbody_id)+'" onclick="body_edit('+str(tbody_id)+');" style="font-size:16px;">'+body+'</p><textarea class="form-control" id="para_edit_'+str(tbody_id)+'" onblur="body_save('+str(tbody_id)+');" style="display:none;" rows="7" name="para_edit_'+str(tbody_id)+'"></textarea>'
            return JsonResponse({'t_id':t_id,'tbody_id':tbody_id,'mystring':html})

        #add new image to tlog_body
        elif len(request.FILES) != 0:
            t_id = request.POST.get("t_id")
            title = request.POST.get("body_title")
            body = ''
            myfile = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            image = fs.url(filename)
            Tlog_data = Tlog_body(tlog_id=t_id, body=body, image=image, email=email, title=title, date=datetime.now())
            Tlog_data.save()
            timage_id = Tlog_data.id
            html = '<img src="'+image+'" style="max-height: 200px;" alt="">'
            return JsonResponse({'t_id':t_id,'timage_id':timage_id,'mystring':html})

        #update title in tlog
        elif 'new_title' in request.POST:
            new_title = request.POST.get("new_title")
            t_id = request.POST.get("t_id")
            u_title = Tlogs.objects.get(id=t_id)
            u_title.title = new_title
            u_title.save()
            html = new_title
            return JsonResponse({'t_id':t_id,'mystring':html})

        #update para in tlog_body
        elif 'para_edit_text' in request.POST:
            data = request.POST.get("para_edit_text")
            t_id = request.POST.get("t_id")
            b_id = request.POST.get("b_id")
            u_body = Tlog_body.objects.get(id=b_id)
            u_body.body = data
            u_body.save()
            html = data
            return JsonResponse({'t_id':t_id,'mystring':html})

def delete_tlog(request):
    if (request.user.is_authenticated)*(request.method == "POST"):
        email = request.user.username
        if request.POST.get("confirmation"):
            t_id = request.POST.get("tlog_id")
            done = Tlogs.objects.get(id=t_id, email=email).delete()
            return JsonResponse({'deleted':done})
            
def manage_tlog_privacy(request):
    if (request.user.is_authenticated)*(request.method == "POST"):
        email = request.user.username
        id = request.POST.get("tlog_id")
        publish = request.POST.get("publish")
        update = Tlogs.objects.filter(id=id, email=email).update(publish=publish)
        print(update)
        if update:
            return JsonResponse({'status':1,'update':update})
            
def edit_tlog(request, id):
    if request.user.is_authenticated:
        email = request.user.username
        t_data = Tlogs.objects.filter(id = id, email= email).values()[0]
        t_body = Tlog_body.objects.filter(tlog_id = id, email= email).values()
        body = []
        j = 0
        for i in t_body:
            img_position = "r"
            if i['image'] != '':
                if j > 0:
                    if t_body[j-1]['image'] != '':
                        img_position = ""
                if (j+1) < len(t_body):
                    if t_body[j+1]['image'] != '':
                        img_position = ""
            body.append({
                'b_id':i['id'],
                'body':i['body'],
                'image':i['image'],
                'img_position':img_position
            })
            j = j + 1
        tlog_data = {
            "t_id" : id,
            "tlog" : t_data['title'],
            "tlog_body" : body
        }
        context = {
            'tlog_data': tlog_data
        }
        context = add_to_footer(context)
        # return JsonResponse(context)
        return render(request, 'edit_tlog.html', context)

def save_edited_tlog(request):
    if (request.user.is_authenticated)*(request.method == "POST"):
        email = request.user.username
        id = request.POST.get("tlog_id")
        title = request.POST.get('title')
        t_data = Tlogs.objects.filter(id = id, email= email).values()[0]
        t_body = Tlog_body.objects.filter(tlog_id = id, email= email).values()
        for i in t_body:
            if i['body'] != "":
                input_name = 'body['+str(i["id"])+']'
                body = request.POST.get(input_name)
                update = Tlog_body.objects.filter(id = i['id']).update(body=body)
        update = Tlogs.objects.filter(id=t_data['id'], email=email).update(title=title)
    return redirect('/profile')

def save_user_fullname(request):
    if (request.user.is_authenticated)*(request.method == 'POST'):
        email = request.user.username
        data = json.loads(request.body)
        update = Login.objects.filter(email=email).update(**data)
        response_data = {'message': 'User data updated successfully'}
        if not update:
            return False
        return JsonResponse(response_data, status=201)
    return False
    
def list_users(request):
    data = list(Login.objects.values().order_by('email'))
    users = list(Login.objects.values('id', 'email').order_by('email'))
    emails = []
    ids = {}
    i = 0
    j = 0
    for user in users:
        if i == 0:
            emails.append({'email':user['email'], 'id':[user['id']]})
            j = j + 1
        else:
            if user['email'] != users[i-1]['email']:
                emails.append({'email':user['email'], 'id':[user['id']]})
                j = j + 1
            else:
                emails[j-1]['id'].append(user['id'])
        i = i + 1
    # for user in emails:
    #     i = 0
    #     for id in user['id']:
    #         if i != 0:
    #             Login.objects.get(id=id).delete()
    #             print(id)
    #             print('deleted')
    #         i = i + 1

    return JsonResponse({'status':1,'emails':emails, 'users':data})