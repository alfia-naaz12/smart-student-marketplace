from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Avg

from .models import Listing, Favorite
from .forms import ListingForm, ReviewForm


# 🏠 HOME PAGE (SEARCH + FILTER)
def home(request):
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    category = request.GET.get('category')

    listings = Listing.objects.all().order_by('-created_at')

    # 🔍 Search
    if query:
        listings = listings.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    # 💰 Price filters
    if min_price:
        listings = listings.filter(price__gte=min_price)

    if max_price:
        listings = listings.filter(price__lte=max_price)

    # 📂 Category filter
    if category:
        listings = listings.filter(category__id=category)

    return render(request, 'marketplace/home.html', {
        'listings': listings,
        'query': query
    })


# 📄 LISTING DETAIL PAGE
def listing_detail(request, id):
    listing = get_object_or_404(Listing, id=id)

    reviews = listing.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # ❤️ Check if user favorited
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(
            user=request.user,
            listing=listing
        ).exists()

    return render(request, 'marketplace/detail.html', {
        'listing': listing,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'is_favorited': is_favorited
    })


# ➕ CREATE LISTING
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


# ✏️ EDIT LISTING
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


# ❌ DELETE LISTING
@login_required
def delete_listing(request, id):
    listing = get_object_or_404(Listing, id=id)

    if listing.seller != request.user:
        return redirect('/')

    if request.method == 'POST':
        listing.delete()
        return redirect('/')

    return render(request, 'marketplace/confirm_delete.html', {'listing': listing})


# 👤 MY LISTINGS
@login_required
def my_listings(request):
    listings = Listing.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_listings.html', {'listings': listings})


# ⭐ ADD REVIEW (FIXED)
@login_required
def add_review(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    # prevent self-review
    if listing.seller == request.user:
        return redirect(f'/listing/{listing_id}/')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.listing = listing
            review.save()
            return redirect(f'/listing/{listing_id}/')
    else:
        form = ReviewForm()

    return render(request, 'marketplace/add_review.html', {
        'form': form,
        'listing': listing
    })


# ❤️ TOGGLE FAVORITE
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


# 🏁 LANDING PAGE
def landing(request):
    return render(request, 'landing.html')