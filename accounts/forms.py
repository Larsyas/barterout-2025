from django import forms
import re
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Digite a senha',
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirme a senha',
    }))

    email = forms.EmailField(
        max_length=255, help_text="Obrigatório. Informe um e-mail válido.")

    document = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '(CPF/RG/PASSAPORTE)',
    }), max_length=15, help_text="Informe um CPF, RG ou Passaporte válido.")

    address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Rua Exemplo 1337, FL, US',
    }), max_length=255, help_text="Informe seu endereço.")

    terms = forms.BooleanField(
        required=True, 
        error_messages={'required': 'Você deve aceitar os termos e condições'}, 
        widget=forms.CheckboxInput(attrs={'class': 'terms-checkbox'})
    )


    class Meta:
        model = Account
        fields = ['first_name', 'last_name',
                 'username', 'phone_number',
                 'email', 'address',
                 'document', 'password',
                 'terms'
                 ]


    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].widget.attrs['placeholder'] = '(xx) x xxxx-xxxx'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['terms'].widget.attrs['class'] += ' terms-checkbox'
        self.fields['password'].help_text = '- Deve ser uma senha forte.'

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        
        if password:
            # Check if the password contains at least one digit
            if not any(char.isdigit() for char in password):
                raise forms.ValidationError(
                    'A senha deve conter pelo menos um dígito.'
                )
            # Check if the password contains at least one lowercase letter
            if not any(char.islower() for char in password):
                raise forms.ValidationError(
                    'A senha deve conter pelo menos uma letra minúscula.'
                )
            # Check if the password contains at least one uppercase letter
            if not any(char.isupper() for char in password):
                raise forms.ValidationError(
                    'A senha deve conter pelo menos uma letra maiúscula.'
                )
            # Check if the password contains at least one symbol
            if not re.search(r'[!@#$%^&*()\-\_=+{};:,<.>]', password):
                raise forms.ValidationError(
                    'A senha deve conter pelo menos um símbolo.'
                )
            
            if password != confirm_password:
                raise forms.ValidationError(
                    'As senhas não coincidem.'
                )
        
        
        terms = cleaned_data.get('terms')
        if not terms:
            raise forms.ValidationError(
                'Você deve aceitar os termos e condições para se registrar.'
            )
        
        return cleaned_data



class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={
                                       'invalid': ("Apenas arquivos de imagem")},
                                        widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city',
                  'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
