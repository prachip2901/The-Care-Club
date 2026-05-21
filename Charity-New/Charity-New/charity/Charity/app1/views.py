from django.shortcuts import redirect, render
from .models import *
from .utils import generate_pass
import razorpay
from django.http import HttpResponseBadRequest
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate
from django.conf import settings
from django.db.models import Count, Sum
from django.utils import timezone
from io import BytesIO

# Create your views here.

def dashboard(request):
    if request.session.has_key('name'):
        data = Donation.objects.select_related('user', 'category').order_by('-created_on', '-id')
        totals = data.aggregate(
            total_amount=Sum('Amount'),
            unique_donors=Count('user', distinct=True),
        )
        now = timezone.now()
        monthly_donations = data.filter(created_on__year=now.year, created_on__month=now.month).count()
        recent_donations = data[:3]
        recent_activities = data[:10]
        context = {
            'recent_donations': recent_donations,
            'recent_activities': recent_activities,
            'total_donations': data.count(),
            'total_amount': totals.get('total_amount') or 0,
            'unique_donors': totals.get('unique_donors') or 0,
            'monthly_donations': monthly_donations,
        }
        return render(request, 'admin/dashboard.html', context)
    return redirect('adminlogin')

def member_donations(request):
    if request.session.has_key('name'):
        data = Donation.objects.select_related('user', 'category').order_by('-id')
        return render(request, 'admin/member_donations.html', {'data': data})
    return redirect('adminlogin')

def members(request):
    if request.session.has_key('name'):
        models=Registeration.objects.filter(is_verified=False)
        return render(request,'admin/members.html',{'model':models})
    return redirect('adminlogin')

def approvemember(request,id):
    if request.session.has_key('name'):
        model=Registeration.objects.get(id=id)
        model.is_verified=True
        x=generate_pass()
        model.password=x
        model.save()
        if model.email:
            send_mail(
                'Membership Approved - Charity',
                (
                    f"Hi {model.name or 'Member'},\n\n"
                    "Your membership request has been approved.\n\n"
                    "Login credentials:\n"
                    f"Phone Number: {model.mobile}\n"
                    f"Password: {model.password}\n\n"
                    "Member Login URL: http://127.0.0.1:8000/login/\n\n"
                    "Thank you for joining Charity."
                ),
                settings.EMAIL_HOST_USER,
                [model.email],
                fail_silently=False,
            )
        return redirect('members')        
    return redirect('adminlogin')
     
def rejectmember(request,id):
    if request.session.has_key('name'):
        model=Registeration.objects.get(id=id)
        send_mail(
                        'Membership Not approval ',
                        f"Your memberhip is not approved",
                        'subhashdantani98@gmail.com',  # TODO: Update this with your mail id
                        [model.email],  # TODO: Update this with the recipients mail id
                        fail_silently=False,
                    )
        model.delete()
        return redirect('members')        
    return redirect('adminlogin')

def allmembers(request):
    if request.session.has_key('name'):
        model=Registeration.objects.filter(is_verified=True)
        return render(request,'admin/memnbers.html',{'model':model})
    return redirect('adminlogin')
    
def deletemember(request,id):
    if request.session.has_key('name'):
        if request.POST:
            model1=Registeration.objects.get(id=id)
            model1.delete()
            return redirect('allmembers')
    return redirect('adminlogin')
    

def sendmail(request,id):
    if request.session.has_key('name'):
        if request.POST:
            model1=Registeration.objects.get(id=id)
            msg=request.POST.get('message')
            send_mail(
                            'Message from Charity ',
                            f"Your message from Charity is\n{msg}",
                            'subhashdantani98@gmail.com',  # TODO: Update this with your mail id
                            [model1.email],  # TODO: Update this with the recipients mail id
                            fail_silently=False,
                        )
            return redirect('allmembers')
        return render(request,'admin/sendmail.html')   
    return redirect('adminlogin')

def alldata(request):
    if request.session.has_key('email'):
        data=Donation.objects.all().order_by('-id')
        return render(request,'user/alldata.html',{'data':data})
    return redirect('login')

def category(request):
    if request.session.has_key('name'):
        mod=CategoryType.objects.all()
        if request.method=='POST':
            model=CategoryType()
            model.name=request.POST['name']
            model.image=request.FILES['image']
            model.description=request.POST['description']
            model.save()
            return redirect('cat')
        return render(request,'admin/category.html',{"mod":mod})
    return redirect('adminlogin')
    

def userindex(request):
    if 'm' in request.session:
        m=request.session['m']
        del request.session['m']
    else:
        m=""
    mod=CategoryType.objects.all()  
    if request.session.has_key('email'): 
        model1=Registeration.objects.get(email=request.session['email'])
        date1=date.today()
        return render(request,'user/index.html',{'mod':mod,'model1':model1,'date':date1})
    else:
        if request.method=='POST':
            model=Registeration()
            model.name=request.POST.get('name')
            model.email=request.POST.get('email')
            model.mobile=request.POST.get('mobile')
            model.save()
            request.session['m']="Request Sent ,wait for admin approval"
            return redirect('userindex')
        date1=date.today()
        return render(request,'user/index.html',{'mod':mod,'date':date1,'m':m})
    
class SuccessView(TemplateView):
    template_name = 'user/success_s.html'


# payment end 
def logout(request):
    if request.session.has_key('email'):
        del request.session['email']
        return redirect('userindex')
    return render(request,'user/index.html')

def adminlogin(request):
    if request.POST:
        name = request.POST.get('name', '').strip()
        password = request.POST.get('password', '')

        # Primary auth path: Django superusers created via `manage.py createsuperuser`.
        user = authenticate(request, username=name, password=password)
        if user and user.is_superuser:
            request.session['name'] = name
            return redirect('dashboard')

        # Backward compatibility for old records in app1.Superuser table.
        model = Superuser.objects.filter(name=name, password=password).first()
        if model:
            request.session['name'] = name
            return redirect('dashboard')

        return render(request, "admin/adminlo.html", {'m': "Invalid username or password"})
    return render(request, "admin/adminlo.html")

def login(request):
    if request.POST:
        try:
            no=request.POST['email']
            password=request.POST['password']
            model=Registeration.objects.get(mobile=no,password=password)
            if model:
                request.session['email']=model.email
                return redirect(('userindex'))
            else:
                return render(request, "user/login.html",{'m':"type invalid number and details"})
        except:
            return render(request, "user/login.html",{'m':"type invalid number and details"})
    return render(request, "user/login.html")

def adminlogout(request):
    if request.session.has_key('name'):
        del request.session['name']
        return redirect('adminlogin')
    return render(request,'user/index.html')

def donationcategory(request,id):
    if request.session.has_key('email'): 
        model1=Registeration.objects.get(email=request.session['email'])
        data=CategoryType.objects.get(id=id)
        if request.POST:
            cat=request.POST['category']
            cat1=CategoryType.objects.get(id=cat)
            request.session['username']=model1.pk
            request.session['cat1']=cat1.pk
            request.session['donateAmount']=request.POST['amount']
            return redirect('/razorpayView/') 
        return render(request,'user/donation.html',{'model1':model1,'data':data})

RAZOR_KEY_ID = 'rzp_test_vmxBmKwQ2RVxWn'
RAZOR_KEY_SECRET = '9QSbTgOiZ7vAOS29YN4tfpA0'
client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))


def generate_donation_receipt_pdf(donation, payment_id, order_id):
    """Build a simple professional donation receipt PDF and return raw bytes."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header block
    pdf.setFillColorRGB(0.13, 0.23, 0.32)
    pdf.rect(0, height - 110, width, 110, stroke=0, fill=1)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(48, height - 60, "HOPEBRIDGE")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(48, height - 82, "Donation Receipt")

    # Receipt title area
    y = height - 150
    pdf.setFillColor(colors.HexColor("#1f3b53"))
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(48, y, "Payment Confirmation")

    y -= 24
    pdf.setFillColor(colors.HexColor("#4a6074"))
    pdf.setFont("Helvetica", 10)
    pdf.drawString(48, y, "Thank you for your generous support. Your contribution has been recorded.")

    # Detail card
    y -= 28
    card_top = y
    card_height = 270
    pdf.setFillColor(colors.HexColor("#f6f9fc"))
    pdf.roundRect(44, card_top - card_height, width - 88, card_height, 12, stroke=0, fill=1)
    pdf.setStrokeColor(colors.HexColor("#d6e3ef"))
    pdf.roundRect(44, card_top - card_height, width - 88, card_height, 12, stroke=1, fill=0)

    details = [
        ("Receipt Date", timezone.localtime(donation.created_on).strftime("%d %b %Y, %I:%M %p")),
        ("Donor Name", donation.user.name or "N/A"),
        ("Donor Email", donation.user.email or "N/A"),
        ("Category", donation.category.name),
        ("Donation Amount", f"INR {donation.Amount}"),
        ("Payment ID", payment_id or "N/A"),
        ("Order ID", order_id or "N/A"),
        ("Receipt Number", f"HB-{donation.id:06d}"),
    ]

    text_y = card_top - 34
    for label, value in details:
        pdf.setFillColor(colors.HexColor("#5b7287"))
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(62, text_y, f"{label}:")
        pdf.setFillColor(colors.HexColor("#1f3b53"))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(180, text_y, str(value))
        text_y -= 28

    # Footer note
    pdf.setFillColor(colors.HexColor("#6d8298"))
    pdf.setFont("Helvetica", 9)
    pdf.drawString(48, 66, "This is a system-generated receipt from HopeBridge.")
    pdf.drawString(48, 50, "For support, contact: support@hopebridge.local")

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()

def razorpayView(request):
    currency = 'INR'
    amount = int(request.session['donateAmount'])*100
    # Create a Razorpay Order
    razorpay_order = client.order.create(dict(amount=amount,currency=currency,payment_capture='0'))
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'http://127.0.0.1:8000/paymenthandler/'    
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url    
    return render(request,'user/razorpayDemo.html',context=context)

@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = client.utility.verify_payment_signature(
                params_dict)
            
            amount = int(request.session['donateAmount'])*100  # Rs. 200
            # capture the payemt
            client.payment.capture(payment_id, amount)
            #Order Save Code
            model1=Registeration.objects.get(id=request.session['username'])
            cat1=CategoryType.objects.get(id=request.session['cat1'])
            Model = Donation()
            Model.user = model1
            Model.category = cat1
            Model.Amount = request.session['donateAmount']
            Model.save()

            receipt_pdf = generate_donation_receipt_pdf(Model, payment_id, razorpay_order_id)
            email_subject = 'Donation Payment Successful - HopeBridge'
            email_body = (
                f"Hi {model1.name or 'Member'},\n\n"
                "Thank you for your donation. Your payment was successful.\n"
                "Please find your donation receipt attached as a PDF.\n\n"
                "Regards,\n"
                "HopeBridge Team"
            )
            email = EmailMessage(
                subject=email_subject,
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[model1.email],
            )
            email.attach(f"hopebridge_receipt_{Model.id}.pdf", receipt_pdf, "application/pdf")
            email.send(fail_silently=False)

            del request.session['username']
            del request.session['cat1']
            del request.session['donateAmount']
            # render success page on successful caputre of payment
            return redirect('/success/')
        except:
            print("Hello")
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
        print("Hello123")
       # if other than POST request is made.
        return HttpResponseBadRequest()

