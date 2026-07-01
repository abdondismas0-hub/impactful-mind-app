from django.template.defaultfilters import default
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_member = models.BooleanField(default=False, help_text="tiki hapa kama huyu ni mwanachamsa rasmi")

    def __str__(self):
        return f"profile ya {self.user.username}"

class course (models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='course_covers/')

    price_regular = models.DecimalField(max_digits=10, decimal_places=2, default=25000.00)
    price_number = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)

    video_url = models.URLField(max_length=500, blank=True, null=True, help_text="weka link ya google drive hapa")
    course_file = models.FileField(upload_to='course_materials/', blank=True, null=True, help_text="Upload PDF,ZIP au notes za kozi hapa (sio lazima)")

    def __str__(self):
        return self.title

class category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(category, on_delete=models.CASCADE, null=True, blank=True)
    author = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True)
    # Hapa tunaweka uwezo wa ku-upload PDF na Cover Image
    cover_image = models.ImageField(upload_to='book_covers/')
    pdf_file = models.FileField(upload_to='books_pdf/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    post_image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    published_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class AboutSection(models.Model):
    tittle = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='about_images/', blank=True, null=True, help_text="pakia picha ukurasa huu")

    def __str__(self):
        return self.tittle

    class Meta:
        verbose_name = "Kuhusu sisi"
        verbose_name_plural = "Kuhusu sisi"

    def __str__(self):
        return self.tittle
        
class Contactsettings(models.Model):
    email = models.EmailField(default="info@impactfulmind.com")
    phone = models.CharField(max_length=20, default="+255753279817")
    

    whatsapp_link = models.URLField(blank=True, null=True, help_text="Weka link ya WhatsApp hapa(mf.https://wa.me/255...)")
    twitter_link = models.URLField(blank=True, null=True, help_text="Weka link ya twitter hapa(mf.https://twitter.com/...)")
    facebook_link = models.URLField(blank=True, null=True, help_text="Weka link ya facebook hapa(mf.https://facebook.com/...)")
    instagram_link = models.URLField(blank=True, null=True, help_text="Weka link ya instagram hapa(mf.https://instagram.com/...)")

    class Meta:
        verbose_name = "Mipangilio yaMawasiliano"
        verbose_name_plural = "Mipangilio yaMawasiliano"
    
    def __str__(self):
        return "Mawasiliano na mitandao ya jamii"
        
class OrganizationSetting(models.Model):
    org_name = models.CharField(max_length=100,default="impactful mind")
    navbar_logo = models.ImageField(upload_to='org_static/logo/', blank=True, null=True,help_text="Weka logo yako itakayoonekana juu")
    hero_banner = models.ImageField(upload_to='org_static/banner/', blank=True, null=True,help_text="Bango la picha litakalo onekana kwenye ukurasa wa nyumbani")
    footer_logo = models.ImageField(upload_to='org_static/footer_logo/', blank=True, null=True,help_text="Weka logo yako itakayoonekana chini")
    
    class Meta:
        verbose_name = "Mipangilio ya Shirika"
        verbose_name_plural = "Mipangilio ya Shirika"
    
    def __str__(self):
        return self.org_name

class SlideShow(models.Model):
    picha = models.ImageField(upload_to='slideshow_images')
    kichwa_cha_habari = models.CharField(max_length=200, help_text="Mfano:Tunatoa Elimu Bora kwa Jamii")
    maelezo = models.TextField(blank=True, default="", help_text="Maelezo mafupi chini ya kichwa cha habari (sio lazima)")
    picha_ni_active = models.BooleanField(default=True, help_text="Angalia hapa ili ionekane ")
    order = models.PositiveIntegerField(default=0, help_text="Namba ya utaratibu (0 ndio ya kwanza)")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Maudhui ya Tovuti"

    def __str__(self):
        return "Maudhui Makuu ya tovuti" 


class SiteContentDetail(models.Model):
    kuhusu_sisi_maelezo = models.TextField(default="pakia maelezo yako ya kuhusu sisi ...", blank=True)
    our_vision = models.TextField(default="pakia Dira ...", blank=True)
    our_mission = models.TextField(default="pakia dhamira ...", blank=True)

    class Meta:
        verbose_name = "Maudhui ya Tovuti (Dira/Dhamira)"
        verbose_name_plural = "Maudhui ya Tovuti (Dira/Dhamira)"

    def __str__(self):
        return "Dira, Dhamira na Kuhusu sisi"

class CourseOrder(models.Model):
    STATUS_CHOICES = [
        ("pending", "inasubiri Uhakiki"),
        ("Approved", "Imekubaliwa"),
        ("Rejected","Imekataliwa")
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', help_text="Mwanafunzi anayenunua")
    course = models.ForeignKey('Course', on_delete=models.CASCADE, help_text="Kozi anayonunua")
    transaction_id = models.CharField(max_length=100, unique=True, help_text="Namba ya muamala  wa M-Pesa/Tigo Pesa")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    tarehe_ya_oda = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Oda za kazi"
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.status})" 

    