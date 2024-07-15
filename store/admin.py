from django.conf import settings
from django.contrib import admin
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.urls import reverse
from .models import Product, ProductGallery, ProductImage, ReviewRating, Variation, UserProduct
import admin_thumbnails


@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_name',
        'price',
        'stock',
        'category',
        'created_date',
        'modified_date',
        'is_available',)

    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]


class VariationAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'variation_category',
        'variation_value',
        'created_date',
        'is_active',)

    list_editable = ('is_active',)

    list_filter = (
        'product',
        'variation_category',
        'variation_value',)
    

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.action(description='Approve selected products')
def approve_products(modeladmin, request, queryset):
    for user_product in queryset:
        user_product.approved = True
        # if user_product.tcm_payment and user_product.user_confirmation is True:
        #     user_product.created_by.TCM_wallet += user_product.tcm_payment
        #     user_product.created_by.save()
        user_product.save()


@admin.action(description='Reject selected products')
def reject_products(modeladmin, request, queryset):
    for user_product in queryset:
        user_product.rejected = True
        
        user_product.save()


@admin.register(UserProduct)
class UserProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'category', 'created_by',
                    'approved', 'rejected', 'user_confirmation', 'tcm_payment', 'created_date']
    list_filter = ['approved', 'created_date']
    actions = [approve_products, reject_products]

    inlines = [ProductImageInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # if obj.approved and obj.tcm_payment:
        #     obj.created_by.TCM_wallet += obj.tcm_payment
        #     obj.created_by.save()


UserProductAdmin.actions = [approve_products, reject_products]


# @receiver(post_save, sender=UserProduct)
# def auto_approve_user_product(sender, instance, created, **kwargs):
#     if instance.approved and instance.user_confirmation is None:
#         # Create the confirmation URL
#         confirm_url = f'{settings.SITE_URL}{reverse("confirm_exchange", args=[instance.id])}'
#         # Send email to user for confirmation
#         send_mail(
#             'Product Approval Confirmation',
#             f'Your product {instance.product_name} has been approved for an exchange of {instance.tcm_payment} TCM. Please log in to your account to accept or reject this offer: {confirm_url}',
#             settings.DEFAULT_FROM_EMAIL,
#             [instance.created_by.email],
#             fail_silently=False,
#         )

# @receiver(post_save, sender=UserProduct)
# def auto_reject_user_product(sender, instance, created, **kwargs):
#     if instance.rejected and instance.user_confirmation is None:
#         # Send email to user for confirmation
#         send_mail(
#             'Product Rejection Confirmation',
#             f'Your product {instance.product_name} has been rejected for our staff team. We are sorry to say we could not accept your product conditions.',
#             settings.DEFAULT_FROM_EMAIL,
#             [instance.created_by.email],
#             fail_silently=False,
#         )

@receiver(post_save, sender=UserProduct)
def auto_approve_or_reject_user_product(sender, instance, created, **kwargs):
    if instance.approved and instance.user_confirmation is None:
        # Product approved, send approval email
        confirm_url = f'{settings.SITE_URL}{reverse("confirm_exchange", args=[instance.id])}'
        send_mail(
            'Product Approval Confirmation',
            f'Your product {instance.product_name} has been approved for an exchange of {instance.tcm_payment} TCM. Please log in to your account to accept or reject this offer: {confirm_url}',
            settings.DEFAULT_FROM_EMAIL,
            [instance.created_by.email],
            fail_silently=False,
        )
    elif instance.rejected and instance.user_confirmation is None and not created:
        # Product rejected, send rejection email only if this is the initial rejection
        send_mail(
            'Product Rejection Confirmation',
            f'Your product {instance.product_name} has been rejected by our staff team. We are sorry to say we could not accept your product conditions.',
            settings.DEFAULT_FROM_EMAIL,
            [instance.created_by.email],
            fail_silently=False,
        )

# admin.site.register(UserProduct, UserProductAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)
admin.site.register(ProductImage)