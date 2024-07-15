from django import forms
from .models import ProductImage, ReviewRating, UserProduct

# Register Product


class UserProductForm(forms.ModelForm):
    terms = forms.BooleanField(
        required=True, 
        error_messages={'required': 'You must accept the terms and conditions'}, 
        widget=forms.CheckboxInput(attrs={'class': 'terms-checkbox'})
    )

    class Meta:
        model = UserProduct
        fields = ['product_name', 'description', 'category', 'terms']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


# Review Form

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']
