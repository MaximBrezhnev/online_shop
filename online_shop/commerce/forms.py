from django import forms


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



