from django.shortcuts import render, redirect
from .models import Product, Order, OrderItem
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
import json
from django.contrib import messages


def home(request):
    testimonials = [
        {"text": "These areca plates are amazing! Great quality and eco-friendly.", "name": "Charan"},
        {"text": "Perfect for my event. Everyone loved them!", "name": "Nikhil"},
        {"text": "Will definitely order again. Love the eco-conscious packaging!", "name": "Kowshik"},
    ]
    return render(request, 'store/home.html', {'testimonials': testimonials})


def product_list(request):
    products = Product.objects.filter(available=True)
    cart = request.session.get('cart', {})

    # ✅ Clean the cart by removing products with quantity <= 0
    cleaned_cart = {k: v for k, v in cart.items() if int(v) > 0}
    request.session['cart'] = cleaned_cart  # update the session cart

    return render(request, 'store/product_list.html', {
        'products': products,
        'cart': cleaned_cart
    })


def add_to_cart(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 1))

        cart = request.session.get('cart', {})
        product_id_str = str(product_id)

        if product_id_str in cart:
            cart[product_id_str] += quantity
        else:
            cart[product_id_str] = quantity

        # ✅ Remove if accidentally added 0 or negative quantity
        if cart[product_id_str] <= 0:
            cart.pop(product_id_str, None)

        request.session['cart'] = cart
        request.session.modified = True
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def update_cart(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        quantity = int(data.get('quantity', 0))
        cart = request.session.get('cart', {})

        if quantity <= 0:
            cart.pop(str(product_id), None)
        else:
            cart[str(product_id)] = quantity

        request.session['cart'] = cart
        request.session.modified = True

        # ✅ Check only non-zero quantity items
        cleaned_cart = {k: v for k, v in cart.items() if int(v) > 0}
        is_cart_empty = len(cleaned_cart) == 0

        return JsonResponse({'success': True, 'cart_empty': is_cart_empty})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def view_cart(request):
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        product_id = str(request.POST.get('product_id'))
        action = request.POST.get('action')

        if action == 'update':
            try:
                quantity = int(request.POST.get('quantity'))
                if quantity > 0:
                    cart[product_id] = quantity
                else:
                    cart.pop(product_id, None)
            except (ValueError, TypeError):
                pass
        elif action == 'remove':
            cart.pop(product_id, None)

        request.session['cart'] = cart
        return redirect('view_cart')

    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        subtotal = product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
        total += subtotal

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


def place_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Cart is empty!")
        return redirect('view_cart')

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        items = []
        total = 0
        for product_id, qty in cart.items():
            product = Product.objects.get(id=product_id)
            total += product.price * qty
            items.append(f"{product.name} x {qty} = ₹{product.price * qty:.2f}")

        # Send confirmation email to user
        message_to_user = f"Hello {name},\n\nThank you for your order!\n\nItems:\n" + \
                          "\n".join(items) + f"\n\nTotal: ₹{total:.2f}\n\nYour order will be shipped to:\n{address}"
        send_mail(
            'Your Order Confirmation - Areca Shop',
            message_to_user,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        # Send notification email to admin/receiver
        message_to_admin = f"New order placed by {name} ({email}, {phone})\n\nItems:\n" + \
                           "\n".join(items) + f"\n\nTotal: ₹{total:.2f}\nShipping Address:\n{address}"
        send_mail(
            'New Order Received - Areca Shop',
            message_to_admin,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )

        # Clear cart after order
        request.session['cart'] = {}

        return redirect('order_success')

    return render(request, 'store/place_order.html')


def remove_from_cart(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        cart = request.session.get('cart', {})
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Item not found in cart'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def order_success(request):
    return render(request, 'store/order_success.html')
