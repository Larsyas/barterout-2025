from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from accounts.models import UserProfile
from carts.views import _cart_id
from carts.models import CartItem
from category.models import Category
from orders.models import OrderProduct
from store.forms import ReviewForm, UserProductForm
from .models import Product, ProductGallery, ProductImage, ReviewRating, UserProduct
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.contrib import messages

# Create your views here.


def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True)
        paginator = Paginator(products, 9)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        paginator = Paginator(products, 9)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(
            category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(
            request), product=single_product).exists()

    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(
                user=request.user, product_id=single_product.id).exists()

        except OrderProduct.DoesNotExist:
            orderproduct = None

    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(
        product_id=single_product.id, status=True)

    # Get the product gallery
    product_gallery = ProductGallery.objects.filter(
        product_id=single_product.id)
    

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }


    return render(request, 'store/product_detail.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']

        if keyword:
            products = Product.objects.order_by(
                '-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()

        context = {
            'products': products,
            'product_count': product_count,
        }
    return render(request, 'store/store.html', context)


@login_required
def register_product(request):
    if request.method == 'POST':
        product_form = UserProductForm(request.POST)
        files = request.FILES.getlist('image')
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.created_by = request.user
            product.save()
            for file in files:
                ProductImage.objects.create(user_product=product, image=file)
            return render(request, 'product_registered.html')  # Substitua pelo nome da sua URL de sucesso
    else:
        product_form = UserProductForm()
    
    return render(request, 'register_product.html', {
        'product_form': product_form,
    })


def product_registered(request):
    return render(request, 'product_registered.html')


def submit_review(request, product_id):
    url: str = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(
                request, 'Thank you! Your review has been updated.')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(
                    request, 'Thank you! Your review has been submitted.')
                return redirect(url)


@login_required
def confirm_exchange(request, product_id):
    try:
        user_product = UserProduct.objects.get(id=product_id, created_by=request.user, approved=True)
    except UserProduct.DoesNotExist:
        messages.error(request, 'Invalid product or you do not have permission to access this product.')
        return redirect('dashboard')  # Replace 'dashboard' with the appropriate URL name

    if request.method == 'POST':
        if 'accept' in request.POST and user_product.user_confirmation is None:
            user_product.user_confirmation = True
            user_product.created_by.TCM_wallet += user_product.tcm_payment
            user_product.created_by.save()
            user_product.save()
            messages.success(request, 'You have accepted the exchange and the TCM has been added to your wallet.')
        elif 'reject' in request.POST and user_product.user_confirmation is None:
            user_product.user_confirmation = False
            user_product.save()
            messages.info(request, 'You have rejected the exchange.')

        return redirect('dashboard')  # Replace 'dashboard' with the appropriate URL name

    context = {
        'user_product': user_product
    }
    return render(request, 'confirm_exchange.html', context)