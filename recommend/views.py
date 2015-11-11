from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from .forms import TripForm
from . import rec_code


def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TripForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            cities = form.cleaned_data['cities']

            similar = rec_code.process_input(cities)
            similar = list(similar.items())

            context = {'similar': similar}
            return render(request, 'results.html', context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TripForm()

    context = {'title': "Trip recommendations",
               'form': form}

    return render(request, 'index.html', context)


# def results(request):
#     context = {'title': "Trip recommendations",}
#
#     return render(request, 'index.html', context)


# todo Require at least two titles.
# todo Have data consistency checks to throw out (or rank weakly) bogus data.
# todo Allow a registration option that will weigh your entries more heavily than other entries
# todo At least initially, don't let users rank their favourties, but rank recommendations.