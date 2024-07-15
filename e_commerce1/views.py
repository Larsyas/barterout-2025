from django.shortcuts import render
from store.models import Product, ReviewRating
from django.db.models import Avg


def home(request):
    products = Product.objects.filter(
        is_available=True).annotate(
            average_rating=Avg('reviewrating__rating')
    ).order_by('-average_rating', 'created_date')

    for product in products:
        reviews = ReviewRating.objects.filter(
            product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,
    }

    return render(request, 'home.html', context)
