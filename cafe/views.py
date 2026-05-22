from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib.auth.models import User
import razorpay
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

def menu_view(request):

    items = MenuItem.objects.all()
    search = request.GET.get('search')
    categories = Category.objects.all()
    item_types = ItemType.objects.all()

    selected_category = request.GET.get('category')
    selected_type = request.GET.get('type')
    
    if search:
        items=items.filter(name__icontains=search)

    if selected_category:
        items = items.filter(category__id=selected_category)

    if selected_type:
        items = items.filter(item_type__id=selected_type)

    return render(request, 'menu.html', {
        'items': items,
        'categories': categories,
        'item_types': item_types,
        'selected_category': selected_category,
        'selected_type': selected_type
    })
    
def add_to_cart(request, variant_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            'login_required':True
        })
    variant = get_object_or_404(Variant, id=variant_id)

    cart = request.session.get('cart', {})

    key = f"{variant.menu_item.id}_{variant.id}"

    if key in cart:
        cart[key]['quantity'] += 1
    else:
        cart[key] = {
            'name': variant.menu_item.name,
            'variant': variant.name,
            'price': float(variant.price),
            'quantity': 1
        }

    request.session['cart'] = cart
    cart_count = len(cart)   
    return JsonResponse({
        'success':True,
        'cart_count':cart_count
    })
    return redirect('menu')

@login_required
def cart_view(request):
    cart = request.session.get('cart', {})
    
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    sgst = round(subtotal * 0.025, 2)
    cgst = round(subtotal * 0.025, 2)
    total = round(subtotal + sgst + cgst, 2)
    
    return render(request, 'cart.html', {
        'cart': cart,
        'subtotal': subtotal,
        'sgst': sgst,
        'cgst': cgst,
        'total': total
    })

def increase_quantity(request, key):
    cart = request.session.get('cart', {})

    if key in cart:
        cart[key]['quantity'] += 1

    request.session['cart'] = cart
    return redirect('cart')

def decrease_quantity(request, key):
    cart = request.session.get('cart', {})

    if key in cart:
        cart[key]['quantity'] -= 1

        if cart[key]['quantity'] <= 0:
            del cart[key]

    request.session['cart'] = cart
    return redirect('cart')

def remove_item(request, key):
    cart = request.session.get('cart', {})

    if key in cart:
        del cart[key]

    request.session['cart'] = cart
    return redirect('cart')

@login_required
def place_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    customer = request.user

    order = Order.objects.create(
        customer=customer,
        total_amount=0
    )

    total = 0

    for key, item in cart.items():
        menu_item_id, variant_id = key.split('_')
        variant = get_object_or_404(Variant, id=variant_id)
        
        price = item['price']
        quantity = item['quantity']

        OrderItem.objects.create(
            order=order,
            item=variant.menu_item,
            variant=variant,
            quantity=quantity,
            price=price
        )

        total += price * quantity

    sgst = total * Decimal(0.025)
    cgst = total * Decimal(0.025)
    final_total = total + sgst + cgst

    order.total_amount = final_total
    order.save()

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        "amount": int(final_total * 100),  
        "currency": "INR",
        "payment_capture": "1"
    })

    return render(request, "payment.html", {
        "order": order,
        "payment": payment,
        "key": settings.RAZORPAY_KEY_ID
    })

@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')

    return render(request, 'order_history.html', {
        'orders': orders
    })

@login_required
def order_success(request):
    return render(request, 'success.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('signup')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Account created successfully")

        return redirect('login')

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('menu')
        else:
            messages.error(request, "Invalid username or password")
            return render(request, 'login.html')    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('login')

def payment_success(request):
    payment_id = request.GET.get('payment_id')

    order = Order.objects.last()

    Payment.objects.create(
        order=order,
        payment_method="Razorpay",
        status="Success",
        transaction_id=payment_id
    )

    request.session['cart'] = {}

    return render(request, 'success.html')
