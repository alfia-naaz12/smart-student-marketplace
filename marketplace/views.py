from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Favorite, Listing
from .forms import ListingForm, ReviewForm


def home(request):
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    listings = Listing.objects.all().order_by('-created_at')

    if query:
        listings = listings.filter(title__icontains=query) | listings.filter(description__icontains=query)

    if min_price:
        listings = listings.filter(price__gte=min_price)

    if max_price:
        listings = listings.filter(price__lte=max_price)

    return render(request, 'marketplace/home.html', {
        'listings': listings,
        'query': query
    })


from .models import Favorite   # ADD THIS

def listing_detail(request, id):
    listing = get_object_or_404(Listing, id=id)

    reviews = listing.seller.reviews.all()
    avg_rating = None

    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()

    # ✅ CHECK IF USER LIKED
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user,
            listing=listing
        ).exists()

    return render(request, 'marketplace/detail.html', {
        'listing': listing,
        'avg_rating': avg_rating,
        'is_favorited': is_favorited   # PASS THIS
    })


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            return redirect('/')
    else:
        form = ListingForm()

    return render(request, 'marketplace/create_listing.html', {'form': form})


@login_required
def edit_listing(request, id):
    listing = get_object_or_404(Listing, id=id)

    if listing.seller != request.user:
        return redirect('/')

    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            return redirect(f'/listing/{id}/')
    else:
        form = ListingForm(instance=listing)

    return render(request, 'marketplace/edit_listing.html', {'form': form})


@login_required
def delete_listing(request, id):
    listing = get_object_or_404(Listing, id=id)

    if listing.seller != request.user:
        return redirect('/')

    if request.method == 'POST':
        listing.delete()
        return redirect('/')

    return render(request, 'marketplace/confirm_delete.html', {'listing': listing})


@login_required
def my_listings(request):
    listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_listings.html', {'listings': listings})


@login_required
def add_review(request, seller_id):
    seller = get_object_or_404(User, id=seller_id)

    if seller == request.user:
        return redirect('/')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.seller = seller
            review.save()
            return redirect('/')
    else:
        form = ReviewForm()

    return render(request, 'marketplace/add_review.html', {'form': form})

@login_required
def toggle_favorite(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        listing=listing
    )

    if not created:
        favorite.delete()

    return redirect(f'/listing/{listing_id}/')

def landing(request):
    return render(request, 'landing.html')