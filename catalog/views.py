from django.shortcuts import render

def catalog_home(request):
    return render(
        request,
        "catalog-templates/catalog_home.html"
    )
