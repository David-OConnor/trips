from django import forms


class BookForm(forms.Form):
    # temporary test form
    title = forms.CharField(label="Title", max_length=50)
    author = forms.CharField(label="Author", max_length=50)