import datetime
from django.shortcuts import get_object_or_404, redirect, render
from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, OrderProduct
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from store.models import Product
# Create your views here.


def payments(request):
    return render(request, 'orders/payments.html')


def process_payment(request, order_number):
    current_user = request.user
    order = get_object_or_404(
        Order, order_number=order_number, user=current_user)

    total = order.order_total

    if order.status == 'Completed':
        return redirect('dashboard')

    if total <= current_user.TCM_wallet:
        current_user.TCM_wallet -= total
        current_user.save()

        order.is_ordered = True
        order.status = 'Completed'
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            # Reduce the quantity of the sold products

            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # Clear cart

        CartItem.objects.filter(user=request.user).delete()

        # Send order recieved email to customer

        mail_subject = 'Thank you for your order!'
        message = render_to_string('orders/order_received_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        try:
            order = Order.objects.get(
                order_number=order_number, is_ordered=True)
            ordered_products = OrderProduct.objects.filter(order_id=order.id)

            context = {
                'order': order,
                'ordered_products': ordered_products,
                'order_number': order.order_number,
                'total': total,
            }

            print(context)
            print(order_number)
            return render(request, 'orders/order_complete.html', context)

        except (Order.DoesNotExist):
            return redirect('home')

    else:
        messages.error(
            request, 'Insufficient TCM balance to complete the payment.')
        # Redirecionar de volta para a página de pagamento
        return redirect('orders:payments')


def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, redirect to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    # elif cart_count > cart_item.product.stock:
    #     messages.error(
    #         request, "Sorry, we don't have that quantity of that product in our stock.")
    #     return redirect('store')

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        # quantity is the number of that particular product on user's cart.
        quantity += cart_item.quantity

        # in case of we don't have enough stock to sell to the user desired quantity:
        if cart_item.quantity > cart_item.product.stock:
            messages.error(
                request, f"Sorry, we don't have enough quantity of that {cart_item.product.product_name} product in our stock at the moment. Current stock: {cart_item.product.stock}")
            return redirect('checkout')

        else:
            pass

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            if current_user.TCM_wallet >= total:
                # Store all the billing info inside of Order table
                data = Order()
                data.user = current_user
                data.first_name = form.cleaned_data['first_name']
                data.last_name = form.cleaned_data['last_name']
                data.phone = form.cleaned_data['phone']
                data.email = form.cleaned_data['email']
                data.address_line_1 = form.cleaned_data['address_line_1']
                data.address_line_2 = form.cleaned_data['address_line_2']
                data.country = form.cleaned_data['country']
                data.state = form.cleaned_data['state']
                data.city = form.cleaned_data['city']
                data.order_note = form.cleaned_data['order_note']
                data.order_total = total
                data.ip = request.META.get('REMOTE_ADDR')
                data.save()

                # Generate order number
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime('%Y%m%d')
                order_number = current_date + str(data.id)  # type: ignore
                data.order_number = order_number
                data.save()

                # current_user.TCM_wallet -= total
                # current_user.save()

                order = Order.objects.get(
                    user=current_user, is_ordered=False, order_number=order_number)
                context = {
                    'order': order,
                    'cart_items': cart_items,
                    'total': total,
                }

                return render(request, 'orders/payments.html', context)
            else:
                messages.error(
                    request, 'You have not enough TCM to make this purchase.')
                return redirect('checkout')

    else:
        return redirect('checkout')


# def order_complete(request):
#     order_number = request.GET.get('order_number')

#     try:
#         order = Order.objects.get(order_number=order_number, is_ordered=True)
#         ordered_products = OrderProduct.objects.filter(order_id=order.id)

#         context = {
#             'order': order,
#             'ordered_products': ordered_products,
#             'order_number': order.order_number,
#         }

#         print(context)
#         print(order_number)
#         return render(request, 'orders/order_complete.html', context)

#     except (Order.DoesNotExist):
#         return redirect('home')
