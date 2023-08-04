from django.shortcuts import render, redirect
from django.urls import reverse
from markdown2 import markdown
from django import forms

from random import randint

from . import util


class AddNewForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(widget=forms.Textarea())


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
    # fetch title
    entry = util.get_entry(title)
    # if exists
    if entry:
        entry = markdown(entry)
    # render
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": entry
    })
    
    
def search(request):
    # query
    query = request.GET.get("q", "")
    # Get entries
    entries = util.list_entries()
    # Get results
    found = False
    results = []
    for entry in entries:
        # found
        if entry.lower() == query.lower():
            found = True
            query = entry
            break
        if query.lower() in entry.lower():
            results += [entry]
            
    # if Found
    if found == True:
        return redirect(reverse("encyclopedia:entry", kwargs={'title':query}))
    else:
        return render(request, "encyclopedia/search.html", {
            "query": query,
            "results": results
        })


def add(request):
    # get to page
    if request.method == 'GET':
        return render(request, "encyclopedia/add.html", {
            "form": AddNewForm(),
            "error": False
        })
        
    # add page
    else:
        error = False
        form = AddNewForm(request.POST)
        if form.is_valid():
            # Get data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            # check if already exists
            if title not in util.list_entries():
                # Add the page to the disk
                util.save_entry(title, content)
                return redirect(reverse("encyclopedia:entry", kwargs={"title":title}))
            else:
                error = True

        return render(request, "encyclopedia/add.html", {
            "form": form,
            "error": error
        })
        
        
def random(request):
    # get random title
    titles = util.list_entries()
    index = randint(0, len(titles) - 1)
    title = titles[index]
    # redirect
    return redirect(reverse("encyclopedia:entry", kwargs={"title":title}))


def edit(request, title):
    # edit page
    if request.method == "GET":
        # fetch title
        entry = util.get_entry(title)
        # render
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "entry": entry
        })
    
    # save changes
    else:
        form = AddNewForm(request.POST)
        if form.is_valid():
            # Get data
            content = form.cleaned_data["content"]
            # Save the page in the disk
            print("title", title)
            util.save_entry(title, content)
            return redirect(reverse("encyclopedia:entry", kwargs={"title":title}))
        # error occured
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": form
            })
            