import phonenumbers
from django import forms

from commerce.models import Order


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "search-input",
                "placeholder": "Введите запрос",
            }
        )
    )


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            "surname",
            "name",
            "middle_name",
            "address",
            "phone_number"
        )
        labels = {
            "surname": "Фамилия",
            "name": "Имя",
            "middle_name": "Отчество",
            "address": "Адрес",
            "phone_number": "Номер телефона"
        }

    def clean_surname(self):
        surname = self.cleaned_data['surname']
        if not surname.replace('-', '').isalpha():
            raise forms.ValidationError('Фамилия должна содержать только буквы и дефисы.')
        return surname

    def clean_name(self):
        name = self.cleaned_data['name']
        if not name.replace('-', '').isalpha():
            raise forms.ValidationError('Имя должно содержать только буквы и дефисы.')
        return name

    def clean_middle_name(self):
        middle_name = self.cleaned_data['middle_name']
        if not middle_name.replace('-', '').isalpha():
            raise forms.ValidationError('Отчество должно содержать только буквы и дефисы.')
        return middle_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']

        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError('Некорректный номер телефона.')
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError('Некорректный номер телефона.')

        return phone_number

