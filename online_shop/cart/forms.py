import phonenumbers
from cart.models import Order
from django import forms


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("surname", "name", "middle_name", "address", "phone_number")
        labels = {
            "surname": "Фамилия",
            "name": "Имя",
            "middle_name": "Отчество",
            "address": "Адрес",
            "phone_number": "Номер телефона",
        }

    def clean_surname(self) -> str:
        surname = self.cleaned_data["surname"]
        if not surname.replace("-", "").isalpha():
            raise forms.ValidationError(
                "Фамилия должна содержать только буквы и дефисы."
            )
        return surname

    def clean_name(self) -> str:
        name = self.cleaned_data["name"]
        if not name.replace("-", "").isalpha():
            raise forms.ValidationError("Имя должно содержать только буквы и дефисы.")
        return name

    def clean_middle_name(self) -> str:
        middle_name = self.cleaned_data["middle_name"]
        if not middle_name.replace("-", "").isalpha():
            raise forms.ValidationError(
                "Отчество должно содержать только буквы и дефисы."
            )
        return middle_name

    def clean_phone_number(self) -> str:
        phone_number = self.cleaned_data["phone_number"]

        try:
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError("Некорректный номер телефона.")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError("Некорректный номер телефона.")

        return phone_number
