from django.urls import path
from .views import *
urlpatterns = [
    path('dashboard/',dashboard,name='dashboard'),
    path('member-donations/',member_donations,name='member_donations'),
    path('cat/',category,name='cat'),
    path('members/',members,name='members'),
    path('allmembers/',allmembers,name='allmembers'),
    path('',userindex,name='userindex'),
    path('logout/',logout,name='logout'),
    path('adminlogout/',adminlogout,name='adminlogout'),
    path('adminlogin/',adminlogin,name='adminlogin'),
    path('login/',login,name='login'),
    path('alldata/',alldata,name='alldata'),
    path('delete/<int:id>/',deletemember,name='delete'),
    path('sendmail/<int:id>/',sendmail,name='sendmail'),
    path('approvedmember/<int:id>/',approvemember,name='approvemember'),
    path('rejectmember/<int:id>/',rejectmember,name='rejectmember'),
    path('category-donation/<int:id>/',donationcategory,name='donationcategory'),
    # payment
    path('razorpayView/',razorpayView,name='razorpayView'),
    path('paymenthandler/',paymenthandler,name='paymenthandler'),
    path('success/', SuccessView.as_view(),name='success'),
]