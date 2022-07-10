from django.shortcuts import render, redirect
from .models import Listing
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
import boto3
import environ
import uuid
import googlemaps
import json
from decimal import Decimal
from django.forms.models import model_to_dict

env = environ.Env()
environ.Env.read_env()

def geocodeFromPostalCode(postal_code):
    try:
        gmaps = googlemaps.Client(key=env('GOOGLE_MAPS_KEY'))
        geocode_result = gmaps.geocode(postal_code)
        coord = geocode_result[0]['geometry']['location']
    except:
        coord = None
    return coord
    
def home(request):
    return render(request, 'home.html')

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    form = CustomUserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

def max_price_func(max_price, listings):
    max_price = Decimal(max_price)
    listings_copy = []
    for i in range(len(listings)):
        if listings[i]["price"] <= max_price:
            listings_copy.append(listings[i])
    return listings_copy

def min_price_func(min_price, listings):
    min_price = Decimal(min_price)
    listings_copy = []
    for i in range(len(listings)):
        if listings[i]["price"] >= min_price:
            listings_copy.append(listings[i])
    return listings_copy

def bounded_func(min_price, max_price, listings):
    max_price = Decimal(max_price)
    min_price = Decimal(min_price)
    listings_copy = []
    for i in range(len(listings)):
        if listings[i]["price"] <= max_price and listings[i]["price"] >= min_price:
            listings_copy.append(listings[i])
    return listings_copy

def listings(request):
    n_vehicles = len(Listing.objects.filter(category='vehicle'))
    n_real_estates = len(Listing.objects.filter(category='real_estate'))
    n_services = len(Listing.objects.filter(category='service'))
    n_arts = len(Listing.objects.filter(category='art'))
    n_others = len(Listing.objects.filter(category='other'))
    filter_params={}
    search_param=""
    if 'search' in request.POST and request.POST['search'] != "":
        search_param = request.POST['search'].upper()
        if 'service' in request.POST or 'vehicle' in request.POST or 'real_estate' in request.POST or 'art' in request.POST or 'other' in request.POST or ( 'min_price' in request.POST and request.POST['min_price'] != "" ) or ( 'max_price' in request.POST and request.POST['max_price'] != "" ):
            listings = []
            filter_params=request.POST
            if 'service' in request.POST:
                listings.append(list(Listing.objects.filter(category='service', title__contains=search_param).values()))
            if "vehicle" in request.POST:
                listings.append(list(Listing.objects.filter(category='vehicle', title__contains=search_param).values()))
            if "real_estate" in request.POST:
                listings.append(list(Listing.objects.filter(category='real_estate', title__contains=search_param).values()))
            if "art" in request.POST:
                listings.append(list(Listing.objects.filter(category='art'), title__contains=search_param).values())
            if "other" in request.POST:
                listings.append(list(Listing.objects.filter(category='other'), title__contains=search_param).values())
            if "max_price" in request.POST or "min_price" in request.POST:
                if request.POST["max_price"] and request.POST["min_price"]:
                    listings.append(list(Listing.objects.filter(price__lte = request.POST["max_price"], price__gte = request.POST["min_price"], title__contains=search_param).values()))
                elif request.POST["min_price"]:
                    listings.append(list(Listing.objects.filter(price__gte = float(request.POST["min_price"]), title__contains=search_param).values()))
                elif request.POST["max_price"]:
                    listings.append(list(Listing.objects.filter(price__lte = float(request.POST["max_price"]), title__contains=search_param).values()))
            listings = [item for items in listings for item in items]
        else:
            listings = list(Listing.objects.filter(title__contains=search_param).values())
    else:
        if 'service' in request.POST or 'vehicle' in request.POST or 'real_estate' in request.POST or 'art' in request.POST or 'other' in request.POST or ( 'min_price' in request.POST and request.POST['min_price'] != "" ) or ( 'max_price' in request.POST and request.POST['max_price'] != "" ):
            listings = []
            filter_params=request.POST
            if 'service' in request.POST:
                listings.append(list(Listing.objects.filter(category='service').values()))
            if "vehicle" in request.POST:
                listings.append(list(Listing.objects.filter(category='vehicle').values()))
            if "real_estate" in request.POST:
                listings.append(list(Listing.objects.filter(category='real_estate').values()))
            if "art" in request.POST:
                listings.append(list(Listing.objects.filter(category='art').values()))
            if "other" in request.POST:
                listings.append(list(Listing.objects.filter(category='other').values()))
            listings = [item for items in listings for item in items]
            if "max_price" in request.POST or "min_price" in request.POST:
                if 'service' not in request.POST and 'vehicle' not in request.POST and 'real_estate' not in request.POST and 'art' not in request.POST and 'other' not in request.POST:
                    listings = list(Listing.objects.all().values())
                if request.POST["max_price"] and request.POST["min_price"]:
                    listings = bounded_func(request.POST["min_price"], request.POST["max_price"], listings)
                elif request.POST["min_price"]:
                    listings = min_price_func(request.POST["min_price"], listings)
                elif request.POST["max_price"]:
                    listings = max_price_func(request.POST["max_price"], listings)
        else:
            listings = list(Listing.objects.all().values())
    if "sort" in request.POST:
        filter_params=request.POST
        if request.POST["sort"] == "lowest":
            sort_list = list(listings)
            for i in range(0, len(sort_list)):
                min_price = sort_list[i]["price"]
                min_index = i
                for j in range(i+1, len(sort_list)):
                    if sort_list[j]["price"] < min_price:
                        min_price = sort_list[j]["price"]
                        min_index = j                
                current = sort_list[i]
                sort_list[i] = sort_list[min_index]
                sort_list[min_index] = current
            listings = sort_list
        if request.POST["sort"] == "highest":
            sort_list = list(listings)
            for i in range(0, len(sort_list)):
                max_price = sort_list[i]["price"]
                max_index = i
                for j in range(i+1, len(sort_list)):
                    if sort_list[j]["price"] > max_price:
                        max_price = sort_list[j]["price"]
                        max_index = j                
                current = sort_list[i]
                sort_list[i] = sort_list[max_index]
                sort_list[max_index] = current
            listings = sort_list
        if request.POST["sort"] == "oldest":
            sort_list = list(listings)
            for i in range(0, len(sort_list)):
                oldest = sort_list[i]["date_posted"]
                oldest_index = i
                for j in range(i+1, len(sort_list)):
                    if sort_list[j]["date_posted"] < oldest:
                        oldest = sort_list[j]["date_posted"]
                        oldest_index = j                
                current = sort_list[i]
                sort_list[i] = sort_list[oldest_index]
                sort_list[oldest_index] = current
            listings = sort_list
        if request.POST["sort"] == "newest":
            sort_list = list(listings)
            for i in range(0, len(sort_list)):
                newest = sort_list[i]["date_posted"]
                newest_index = i
                for j in range(i+1, len(sort_list)):
                    if sort_list[j]["date_posted"] > newest:
                        newest = sort_list[j]["date_posted"]
                        newest_index = j
                current = sort_list[i]
                sort_list[i] = sort_list[newest_index]
                sort_list[newest_index] = current
            listings = sort_list
    if isinstance(listings, list):
        listings_obj = listings
    else:
        listings_obj = list(listings.values())
    return render(request, 'listings_index.html', { 'listings': listings, 'filter': filter_params, 'search': search_param.lower(), 'listings_obj': listings_obj,'n_vehicles':n_vehicles,'n_arts':n_arts,'n_services':n_services,'n_real_estates':n_real_estates,'n_others':n_others })
        
@login_required
def listings_new(request):
    return render (request,'listings_new.html')

@login_required
def listings_create(request):
    url = ''
    user_id = request.user.id
    photo_file = request.FILES.get('picture', None)
    location = request.POST['location'] 
    if not location:
        location = "M5H2N2"
    geolocation = json.dumps(geocodeFromPostalCode(location))
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            s3.upload_fileobj(photo_file, env('BUCKET'), key)
            url = f"{env('S3_BASE_URL')}/{key}"
        except:
            print('An error occurred uploading file to S3')
    if not photo_file:
        url = '/static/css/assets/logo_new.svg'
    Listing.objects.create(
            user= request.user,
            title= request.POST['item_name'].upper(),
            price= request.POST['price'],
            category= request.POST['category'],
            location= location,
            geolocation = geolocation,
            description= request.POST['description'],
            picture = url
    )
    return redirect(f'/listings/user/{user_id}/')
    
def listings_detail(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    return render(request, 'listings_show.html', {'listing': listing, 'listing_obj': model_to_dict(listing)})

@login_required
def listings_delete(request, listing_id):
    listing = Listing.objects.filter(id=listing_id)
    listing.delete()
    user_id = request.user.id
    return redirect(f'/listings/user/{user_id}/')

def listings_edit(request, listing_id):
    listing = Listing.objects.get(id = listing_id)
    if (request.user.id == listing.user.id):
        return render(request, 'listing_edit.html', {'listing': listing})
    else:
        return render(request, 'error.html', {'message': 'You do not have access to edit this post.'})

def listings_update(request, listing_id):
    listing = Listing.objects.get(id = listing_id)
    if (request.user == listing.user):
        location = request.POST['location']
        if not location:
            location = "M5H2N2"
        geolocation = json.dumps(geocodeFromPostalCode(location))
        listing.title = request.POST["title"].upper()
        listing.price = request.POST["price"]
        listing.category = request.POST["category"]
        listing.description = request.POST["description"]
        listing.location = location
        listing.geolocation = geolocation
        listing.save()
        return redirect(f'/listings/user/{request.user.id}/')
    else:
        return render(request, 'error.html', {'message': 'You do not have access to edit this post.'})

def user_listings(request, user_id):
    try:
        listings = Listing.objects.filter(user = user_id)
    except Listing.DoesNotExist:
        listings = []
    return render(request, 'user_listings.html', {'listings': listings})



