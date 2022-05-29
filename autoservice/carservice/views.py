from django.shortcuts import render
from django.http import HttpResponse
from .models import Service, Order, Car
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm


def index(request):
    num_services = Service.objects.all().count()
    num_orders = Order.objects.all().filter(status = 'b').count()
    num_cars = Car.objects.all().count()
    num_visits = request.session.get('num_visits', 1)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_services' : num_services,
        'num_orders' : num_orders,
        'num_cars' : num_cars,
        'num_visits' : num_visits,
    }
    return  render(request, 'autoservice/index.html', context)


@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Profilis atnaujintas")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'autoservice/profile.html', context)  


@csrf_protect
def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        error = False
        if not password or password != password2 :
            messages.error(request, 'Slaptaodziai nesutampa arba neivesti')
            error = True
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Vartotojas {username} jau egzistuoja')
            error = True
        if User.objects.filter(email=email).exists():
            messages.error(request, f'El pastas {email} jau egzistuoja')
            error = True
        if error:
            return redirect('register')
        else:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, f'Vartotojas {username} uzregistruotas')
            return redirect('index')
    return render(request, 'autoservice/register.html')


def cars(request):
    cars = Car.objects.all()
    context = {
        'cars' : cars
    }
    return render(request, 'autoservice/cars.html', context=context)

def services(request):
    services = Service.objects.all()
    context = {
        'services' : services
    }
    return render(request, 'autoservice/services.html', context=context)

def contacts(request):
    return render(request, 'autoservice/contacts.html')

def car(request, car_id):
    single_car=get_object_or_404(Car, pk=car_id)
    return render(request, 'autoservice/car.html', {'car': single_car})

class OrderListView(generic.ListView):
    model = Order
    context_object_name= 'orders'
    template_name = 'autoservice/orders.html'
    paginate_by = 2


def order(request, order_id):
    single_order=get_object_or_404(Order, pk=order_id)
    return render(request, 'autoservice/order.html', {'order': single_order} )

def search(request):
    query = request.GET.get('query')
    search_results = Car.objects.filter(Q(plate_nr__icontains=query) |
     Q(client__icontains=query) | 
     Q(vin_code__icontains=query) | 
     Q(car_model__model__icontains=query))
    return render(request, 'autoservice/search.html', {'cars': search_results, 'query': query})

class OrdersByUserListView(LoginRequiredMixin,generic.ListView):
    model = Order
    template_name ='autoservice/user_orders.html'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(owner=self.request.user).filter(~Q(status__exact='b')).order_by('due_back')
