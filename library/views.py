from django import forms
from django.db.models import Q
from django.template.defaultfilters import title
from django.template import context
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from .models import Book,category,course as CourseModel,profile,OrganizationSetting
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import AboutSection,Contactsettings
import time
import uuid
from django.contrib import messages
from .models import SlideShow, SiteContentDetail, CourseOrder
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

class CustomRegisterForm(UserCreationForm):
    first_name = forms.CharField(required=True, label="jina la kwanza")
    last_name = forms.CharField(required=True, label="jina la mwisho")
    email = forms.EmailField(required=True, label="Barua pepe (Email)")

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields["username"].label = "Jina la Mtumiaji (username)"


def course_detail(request, course_id):
    course_obj = get_object_or_404(CourseModel, id=course_id)
    user_profile = getattr(request.user, 'profile', None)

    if request.user.is_authenticated and user_profile and user_profile.is_member:
        final_price = course_obj.price_number
        status = "mwanachama"
    else:
        final_price = course_obj.price_regular
        status = "mgeni"

    # Check if user has paid and been approved
    has_access = False
    order_status = None
    if request.user.is_authenticated:
        order = CourseOrder.objects.filter(
            student=request.user, course=course_obj
        ).order_by('-tarehe_ya_oda').first()
        if order:
            order_status = order.status
            has_access = (order.status == "Approved")

    context = {
        'course': course_obj,
        'final_price': final_price,
        'status': status,
        'has_access': has_access,
        'order_status': order_status,
    }

    return render(request, 'course_detail.html', context)


@login_required(login_url='login')
def course_viewer(request, course_id):
    """Full-page reader/player — only accessible if user has an Approved order."""
    course_obj = get_object_or_404(CourseModel, id=course_id)

    has_access = CourseOrder.objects.filter(
        student=request.user, course=course_obj, status="Approved"
    ).exists()

    if not has_access:
        messages.error(request, "Huhitajiwi kufungua kozi hii. Tafadhali lipia kwanza na subiri uhakiki.")
        return redirect('course_detail', course_id=course_id)

    return render(request, 'course_viewer.html', {'course': course_obj})




def home(request):
    return render(request, 'home.html')


def maktaba(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    if query:
        vitabu_vyote = Book.objects.filter(Q(title__icontains=query))
    elif category_id:
        vitabu_vyote = Book.objects.filter(category_id=category_id)
    else:
        vitabu_vyote = Book.objects.all().order_by('-created_at')

    makundi_yote = category.objects.all()

    context = {'vitabu':vitabu_vyote,
                'books':vitabu_vyote,
                'makundi':makundi_yote,
                'query':query,
                 }
    return render(request,'maktaba.html',context)


def online_courses(request):
    kozi_zote = CourseModel.objects.all()


    context = {'courses':kozi_zote,
            }

    return render(request,'online_courses.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomRegisterForm()

    context = {'form': form}
    return render(request, 'signup.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()

    context = {'form': form}
    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required(login_url='login')
def dashboard_view(request):
    user_profile, created = profile.objects.get_or_create(user=request.user)
    # Show only approved courses on the dashboard
    approved_orders = CourseOrder.objects.filter(
        student=request.user, status="Approved"
    ).select_related('course')
    # Also include pending orders so user can track them
    pending_orders = CourseOrder.objects.filter(
        student=request.user, status="pending"
    ).select_related('course')

    context = {
        'profile': user_profile,
        'approved_orders': approved_orders,
        'pending_orders': pending_orders,
    }
    return render(request, 'dashboard.html', context)

def maktaba_view(request):
    books = Book.objects.all()

    context = {'bozoks': books}
    return render(request, 'maktaba.html', context)

def online_courses_views(request):

    Courses = CourseModel.objects.all()

    context = {'courses':Courses,
            }
    
    return render(request,'online_courses.html', context)
    

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
        return render(request, 'register.html', {'form': form})

def kuhusu_sisi_view(request):
    return render(request,'kuhusu_sisi.html')

def mawasiliano_view(request):
    return render(request,'mawasiliano.html')

def gundua_zaidi_view(request):
    return render(request,'gundua_zaidi.html')

def kuhusu_sisi_view(request):
    about_data = AboutSection.objects.first()
    return render(request,'kuhusu_sisi.html', {'about':about_data})

def mawasiliano_view(request):
    contact_data = Contactsettings.objects.first()
    return render(request,'mawasiliano.html', {'contact':contact_data})

def gundua_zaidi_view(request):
    about_data = AboutSection.objects.first()
    contact_data = Contactsettings.objects.first()
    return render(request,'gundua_zaidi.html', {'about':about_data, 'contact':contact_data})


@login_required(login_url='login')
def checkout(request, course_id):
    course = get_object_or_404(CourseModel, id=course_id)

    # Check if user already has an approved order for this course
    existing_approved = CourseOrder.objects.filter(
        student=request.user, course=course, status="Approved"
    ).exists()
    if existing_approved:
        return redirect('course_detail', course_id=course.id)

    # Check if user already submitted a pending order
    existing_pending = CourseOrder.objects.filter(
        student=request.user, course=course, status="pending"
    ).first()

    # Determine price
    user_profile = getattr(request.user, 'profile', None)
    if user_profile and user_profile.is_member:
        final_price = course.price_number
        hadhi = "Mwanachama"
    else:
        final_price = course.price_regular
        hadhi = "Mgeni"

    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id', '').strip().upper()

        if not transaction_id:
            messages.error(request, "Tafadhali weka Namba ya Muamala.")
        elif CourseOrder.objects.filter(transaction_id=transaction_id).exists():
            messages.error(request, "Namba hii ya muamala imeshatumika tayari. Hakikisha umeandika namba sahihi.")
        else:
            CourseOrder.objects.create(
                student=request.user,
                course=course,
                transaction_id=transaction_id,
                status="pending",
            )
            messages.success(
                request,
                f"Asante! Oda yako ya '{course.title}' imepokelewa na inangoja uhakiki. "
                f"Muamala Namba: {transaction_id}. Utapata ufikiaji baada ya uhakiki."
            )
            return redirect('course_detail', course_id=course.id)

    return render(request, 'checkout.html', {
        'course': course,
        'final_price': final_price,
        'hadhi': hadhi,
        'existing_pending': existing_pending,
    })


def home_view(request):
    slideshow_images = SlideShow.objects.filter(picha_ni_active=True)
    site_content = SiteContentDetail.objects.first()
    org_data = OrganizationSetting.objects.first()
    if not site_content:
        site_content = {
            "kuhusu_sisi_maelezo": "pakia maelezo yako ya kuhusu sisi ...",
            "our_vision": "pakia Dira ...",
            "our_mission": "pakia dhamira ..."
        }

    courses = CourseModel.objects.all()

    context = {
        'slideshow_images': slideshow_images,
        'site_content': site_content,
        'courses': courses,
        'org_data': org_data,
    }
    return render(request, 'home.html', context)
    
@login_required(login_url='login')
def process_payment(request, course_id):
    course = get_object_or_404(CourseModel, id=course_id)
    
    # 1. Amua Bei Kulingana na Hadhi
    # (Hii ni mfano tu, weka logic yako ya mwanachama/mgeni hapa)
    if request.user.groups.filter(name='Mwanachama').exists():
        final_price = course.price_number
        hadhi = "Mwanachama"
    else:
        final_price = course.price_regular
        hadhi = "Mgeni"

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')

        # --- HAPA NDIO UTAWEKA MOCK API (API YA KUIGIZA) ---
        
        # Simulizi ya kusubiri mtandao (Dakika 2)
        time.sleep(2)
        
        # Kujifanya umepata namba ya muamala kutoka Selcom/AzamPay
        fake_transaction_id = str(uuid.uuid4()).split('-')[0].upper()
        
        # Kujifanya mtandao umekubali
        mock_response = {
            "status": "success",
            "transaction_id": fake_transaction_id,
            "message": "Malipo yamekubaliwa na mtandao"
        }
        
        # --- LOGIC YA KUHIFADHI (MOCK) ---
        if mock_response["status"] == "success":
            # Save the order using correct CourseOrder fields
            CourseOrder.objects.create(
                student=request.user,
                course=course,
                transaction_id=fake_transaction_id,
                status="pending",
            )
            
            # Mpeleke kwenye ukurasa unaotakiwa
            messages.success(request, f"Malipo yamefanikiwa! ID: {fake_transaction_id}.Karibu kwenye kozi.")
            return redirect('home') 
        else:
            messages.error(request, "Kulipia kuna shida.")
            # --- MWISHO WA MOCK API ---

    return render(request, 'checkout.html', {
        'course': course,
        'final_price': final_price,
        'hadhi': hadhi
    })


def verify_payment(request):
    """
    Hii ndio njia mpya ya uhakiki
    """
    transaction_id = request.POST.get('transaction_id')
    
    if not transaction_id:
        return JsonResponse({'status': 'error', 'message': 'Hakuna Namba ya Muamala'})

    # Tafuta shughuli husika
    order = get_object_or_404(CourseOrder, transaction_id=transaction_id, student=request.user)
    
    # Simulizi ya kuwasiliana na Selcom (Dakika 2)
    time.sleep(2)
    
    # 1. Fikiria unafanya POST kwa API ya kweli ya Selcom hapa
    # 2. Unaangalia kama imerudisha "Success"
    # Kwa sasa, tutaweka tu "Success" kwa mfano (Mocked Response)
    
    # Hii ni hatua muhimu sana kwa ajili ya kazi yako
    response = {"status": "success"}  # Badilisha hii baadaye kulingana na API ya kweli

    if response["status"] == "success":
        # Badilisha hadhi ya order kuwa Approved
        order.status = "Approved"
        order.save()
        
        # Mfungulia milango ya darasani mara moja
        messages.success(request, "Imefanikiwa! Sasa unaweza kuingia darasani.")
        
        return JsonResponse({
            'status': 'success',
            'redirect_url': reversed('course_detail', args=[order.course.id])
        })
    else:
        messages.error(request, "Bado tunafanya uhakiki...")
        return JsonResponse({'status': 'error', 'message': 'Bado tunafanya uhakiki...'}, status=400)
