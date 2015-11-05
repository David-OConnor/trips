from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (
    PrependedText, PrependedAppendedText, FormActions)


class TripForm(forms.Form):
    # temporary test form
    cities = forms.CharField(label="City 1", max_length=50)

    def __init__(self, *args, **kwargs):
        super(TripForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.layout = Layout(
            PrependedText('cities', '@', placeholder='Enter cities you like'),
        )
