from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import (
    PrependedText, PrependedAppendedText, FormActions)


class TripForm(forms.Form):
    # temporary test form
    cities = forms.CharField(label="", max_length=500)

    def __init__(self, *args, **kwargs):
        super(TripForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.layout = Layout(
            PrependedText('cities', '<i class="fa fa-search"></i>',
                          placeholder='Enter cities you\'ve enjoyed. ie '
                                      '\'paris france, richmond virginia, oslo norway\''),
        )
