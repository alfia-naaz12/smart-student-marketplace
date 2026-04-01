from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.contrib import messages

from .models import Listing, Favorite, Message
from .forms import ListingForm, ReviewForm


# 🏠 HOME PAGE
def home(request):
    query = request.GET.get('q')
    listings = Listing.objects.all().order_by('-created_at')

    if query:
        listings = listings.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'marketplace/home.html', {
        'listings': listings,
        'query': query
    })


# 📄 LISTING DETAIL
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    reviews = listing.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

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

            messages.success(request, "🎉 Listing posted successfully!")

            return redirect('create_listing')

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


# ⭐ ADD REVIEW
@login_required
def add_review(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

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


# 💬 SEND MESSAGE (FROM DETAIL PAGE)
@login_required
def send_message(request, listing_id):
    if request.method == "POST":
        content = request.POST.get("message")

        listing = get_object_or_404(Listing, id=listing_id)

        if content:
            Message.objects.create(
                sender=request.user,
                receiver=listing.seller,
                listing=listing,
                content=content
            )

    return redirect('inbox')


# 💬 INBOX (FIXED CHAT SYSTEM)
@login_required
def inbox(request):

    # 🔥 HANDLE MESSAGE SEND FROM CHAT
    if request.method == "POST":
        content = request.POST.get("message")
        receiver_id = request.POST.get("receiver_id")
        listing_id = request.POST.get("listing_id")

        if content and receiver_id and listing_id:
            Message.objects.create(
                sender=request.user,
                receiver_id=receiver_id,
                listing_id=listing_id,
                content=content
            )

        return redirect(f'/inbox/?user={receiver_id}')

    # 🔥 ALL MESSAGES
    all_messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    )

    # 🔥 UNIQUE USERS (FIXED)
    users = []
    for msg in all_messages:
        if msg.sender != request.user and msg.sender not in users:
            users.append(msg.sender)

        if msg.receiver != request.user and msg.receiver not in users:
            users.append(msg.receiver)

    # 🔥 SELECT CHAT USER
    selected_user_id = request.GET.get('user')
    selected_user = None
    chat_messages = []
    selected_listing_id = None

    if selected_user_id:
        selected_user = User.objects.get(id=selected_user_id)

        # 🔥 GET LATEST MESSAGE (IMPORTANT)
        latest_message = Message.objects.filter(
            Q(sender=request.user, receiver=selected_user) |
            Q(sender=selected_user, receiver=request.user)
        ).order_by('-timestamp').first()

        if latest_message:
            selected_listing_id = latest_message.listing.id

            chat_messages = Message.objects.filter(
                (
                    Q(sender=request.user, receiver=selected_user) |
                    Q(sender=selected_user, receiver=request.user)
                ),
                listing_id=selected_listing_id
            ).order_by('timestamp')

    return render(request, 'marketplace/inbox.html', {
        'users': users,
        'chat_messages': chat_messages,
        'selected_user': selected_user,
        'selected_listing_id': selected_listing_id
    })


# 🏁 LANDING PAGE
def landing(request):
    return render(request, 'landing.html')