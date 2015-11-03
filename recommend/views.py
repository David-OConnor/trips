from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

from .forms import BookForm
from . import book_db


def index(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = BookForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            title, author = form.cleaned_data['title'], form.cleaned_data['author']

            book = book_db.query(title, author)[0]
            return HttpResponse("Here's your book: {} by {}".format(
                book.title, book.author))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = BookForm()

    context = {'title': "Book Recommendations",
               'form': form}

    return render(request, 'index.html', context)


def results(request):
    pass


# todo Require at least two titles.
# todo Have data consistency checks to throw out (or rank weakly) bogus data.
# todo Allow a registration option that will weigh your entries more heavily than other entries
# todo At least initially, don't let users rank their favourties, but rank recommendations.