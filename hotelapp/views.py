from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
	BillDetailForm,
	GuestBillForm,
	GuestForm,
	HotelLoginForm,
	PaymentForm,
	ReservationForm,
	RoomForm,
	RoomTypeForm,
	ServiceForm,
	StaffForm,
)
from .models import BillDetail, Guest, GuestBill, Payment, Reservation, Room, RoomType, Service, Staff


def home(request):
	return render(request, "home.html")


def login_page(request):
	form = HotelLoginForm(request, data=request.POST if request.method == "POST" else None)
	next_url = request.POST.get("next", request.GET.get("next", ""))
	if request.method == "POST":
		if form.is_valid():
			login(request, form.get_user())
			messages.success(request, "Signed in successfully.")
			if next_url and url_has_allowed_host_and_scheme(
				next_url,
				allowed_hosts={request.get_host()},
				require_https=request.is_secure(),
			):
				return redirect(next_url)
			return redirect("home")
		messages.error(request, "Please check your username and password.")
	return render(request, "index.html", {"form": form, "next": next_url})


def register_user(request):
	"""Create an account with Django's built-in, password-safe registration form."""
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Your account was created and you are now signed in.")
			return redirect("home")
	else:
		form = UserCreationForm()

	return render(request, "register.html", {"form": form})


@require_POST
def logout_user(request):
	"""Log out the current user, show a message, and return to the home page."""
	logout(request)
	messages.success(request, "You have been logged out.")
	return redirect("home")


@require_POST
@login_required
def add_guest(request):
	"""CREATE: validate the submitted form and save a new guest."""
	form = GuestForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, "Guest created successfully.")
		return redirect("guest")

	messages.error(request, "Please correct the errors in the form.")
	return render(request, "guest.html", {
		"form": form,
		"guests": Guest.objects.all(),
		"is_editing": False,
	})


@login_required
def guest_list(request):
	"""READ: get all guests and display them in the guest table."""
	return render(request, "guest.html", {
		"form": GuestForm(),
		"guests": Guest.objects.all(),
		"is_editing": False,
	})


@login_required
def update_guest(request, pk):
	"""UPDATE: find a guest, validate changed fields, and save the update."""
	guest = get_object_or_404(Guest, pk=pk)
	form = GuestForm(request.POST if request.method == "POST" else None, instance=guest)
	if request.method == "POST":
		if form.is_valid():
			form.save()
			messages.success(request, "Guest updated successfully.")
			return redirect("guest")
		messages.error(request, "Please correct the errors in the form.")

	return render(request, "guest.html", {
		"form": form,
		"guests": Guest.objects.all(),
		"is_editing": True,
		"editing_record": guest,
	})


@require_POST
@login_required
def delete_guest(request, pk):
	"""DELETE: find the guest and delete it when no protected records use it."""
	guest = get_object_or_404(Guest, pk=pk)
	try:
		guest.delete()
	except ProtectedError:
		messages.error(request, "This guest cannot be deleted because it is still in use.")
	else:
		messages.success(request, "Guest deleted successfully.")
	return redirect("guest")


@require_POST
@login_required
def add_staff(request):
	"""CREATE: validate the submitted form and save a new staff member."""
	form = StaffForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, "Staff member created successfully.")
		return redirect("staff")

	messages.error(request, "Please correct the errors in the form.")
	return render(request, "staff.html", {
		"form": form,
		"staff_members": Staff.objects.all(),
		"is_editing": False,
	})


@login_required
def staff_list(request):
	"""READ: get all staff members and display them in the staff table."""
	return render(request, "staff.html", {
		"form": StaffForm(),
		"staff_members": Staff.objects.all(),
		"is_editing": False,
	})


@login_required
def update_staff(request, pk):
	"""UPDATE: find a staff member, validate changed fields, and save the update."""
	staff_member = get_object_or_404(Staff, pk=pk)
	form = StaffForm(request.POST if request.method == "POST" else None, instance=staff_member)
	if request.method == "POST":
		if form.is_valid():
			form.save()
			messages.success(request, "Staff member updated successfully.")
			return redirect("staff")
		messages.error(request, "Please correct the errors in the form.")

	return render(request, "staff.html", {
		"form": form,
		"staff_members": Staff.objects.all(),
		"is_editing": True,
		"editing_record": staff_member,
	})


@require_POST
@login_required
def delete_staff(request, pk):
	"""DELETE: find the staff member and remove it from the database."""
	staff_member = get_object_or_404(Staff, pk=pk)
	staff_member.delete()
	messages.success(request, "Staff member deleted successfully.")
	return redirect("staff")


@require_POST
@login_required
def add_room_type(request):
	"""CREATE: validate the submitted form and save a new room type."""
	form = RoomTypeForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, "Room type created successfully.")
		return redirect("roomtype")

	messages.error(request, "Please correct the errors in the form.")
	return render(request, "roomtype.html", {
		"form": form,
		"room_types": RoomType.objects.all(),
		"is_editing": False,
	})


@login_required
def room_type_list(request):
	"""READ: get all room types and display them in the room type table."""
	return render(request, "roomtype.html", {
		"form": RoomTypeForm(),
		"room_types": RoomType.objects.all(),
		"is_editing": False,
	})


@login_required
def update_room_type(request, pk):
	"""UPDATE: find a room type, validate changed fields, and save the update."""
	room_type = get_object_or_404(RoomType, pk=pk)
	form = RoomTypeForm(request.POST if request.method == "POST" else None, instance=room_type)
	if request.method == "POST":
		if form.is_valid():
			form.save()
			messages.success(request, "Room type updated successfully.")
			return redirect("roomtype")
		messages.error(request, "Please correct the errors in the form.")

	return render(request, "roomtype.html", {
		"form": form,
		"room_types": RoomType.objects.all(),
		"is_editing": True,
		"editing_record": room_type,
	})


@require_POST
@login_required
def delete_room_type(request, pk):
	"""DELETE: find the room type and remove it if no rooms depend on it."""
	room_type = get_object_or_404(RoomType, pk=pk)
	try:
		room_type.delete()
	except ProtectedError:
		messages.error(request, "This room type cannot be deleted because it is still in use.")
	else:
		messages.success(request, "Room type deleted successfully.")
	return redirect("roomtype")


@require_POST
@login_required
def add_room(request):
	"""CREATE: validate the submitted form and save a new room."""
	form = RoomForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, "Room created successfully.")
		return redirect("room")

	messages.error(request, "Please correct the errors in the form.")
	return render(request, "room.html", {
		"form": form,
		"rooms": Room.objects.all(),
		"is_editing": False,
	})


@login_required
def room_list(request):
	"""READ: get all rooms and display them in the room table."""
	return render(request, "room.html", {
		"form": RoomForm(),
		"rooms": Room.objects.all(),
		"is_editing": False,
	})


@login_required
def update_room(request, pk):
	"""UPDATE: find a room, validate changed fields, and save the update."""
	room = get_object_or_404(Room, pk=pk)
	form = RoomForm(request.POST if request.method == "POST" else None, instance=room)
	if request.method == "POST":
		if form.is_valid():
			form.save()
			messages.success(request, "Room updated successfully.")
			return redirect("room")
		messages.error(request, "Please correct the errors in the form.")

	return render(request, "room.html", {
		"form": form,
		"rooms": Room.objects.all(),
		"is_editing": True,
		"editing_record": room,
	})


@require_POST
@login_required
def delete_room(request, pk):
	"""DELETE: find the room and remove it if no reservations depend on it."""
	room = get_object_or_404(Room, pk=pk)
	try:
		room.delete()
	except ProtectedError:
		messages.error(request, "This room cannot be deleted because it is still in use.")
	else:
		messages.success(request, "Room deleted successfully.")
	return redirect("room")


@require_POST
@login_required
def add_reservation(request):
	"""CREATE: validate the submitted form and save a new reservation."""
	form = ReservationForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, "Reservation created successfully.")
		return redirect("reservation")

	messages.error(request, "Please correct the errors in the form.")
	return render(request, "reservation.html", {
		"form": form,
		"reservations": Reservation.objects.all(),
		"is_editing": False,
	})


@login_required
def reservation_list(request):
	"""READ: get all reservations and display them in the reservations table."""
	return render(request, "reservation.html", {
		"form": ReservationForm(),
		"reservations": Reservation.objects.all(),
		"is_editing": False,
	})


@login_required
def update_reservation(request, pk):
	"""UPDATE: find a reservation, validate changed fields, and save the update."""
	reservation = get_object_or_404(Reservation, pk=pk)
	form = ReservationForm(request.POST if request.method == "POST" else None, instance=reservation)
	if request.method == "POST":
		if form.is_valid():
			form.save()
			messages.success(request, "Reservation updated successfully.")
			return redirect("reservation")
		messages.error(request, "Please correct the errors in the form.")

	return render(request, "reservation.html", {
		"form": form,
		"reservations": Reservation.objects.all(),
		"is_editing": True,
		"editing_record": reservation,
	})


@require_POST
@login_required
def delete_reservation(request, pk):
	"""DELETE: find the reservation and remove it if no protected records use it."""
	reservation = get_object_or_404(Reservation, pk=pk)
	try:
		reservation.delete()
	except ProtectedError:
		messages.error(request, "This reservation cannot be deleted because it is still in use.")
	else:
		messages.success(request, "Reservation deleted successfully.")
	return redirect("reservation")


@require_POST
@login_required
def add_service(request):
	"""CREATE: validate the submitted form and save a new service."""
	form = ServiceForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, "Service created successfully.")
		return redirect("services")

	messages.error(request, "Please correct the errors in the form.")
	return render(request, "services.html", {
		"form": form,
		"services": Service.objects.all(),
		"is_editing": False,
	})


@login_required
def service_list(request):
	"""READ: get all services and display them in the services table."""
	return render(request, "services.html", {
		"form": ServiceForm(),
		"services": Service.objects.all(),
		"is_editing": False,
	})


@login_required
def update_service(request, pk):
	"""UPDATE: find a service, validate changed fields, and save the update."""
	service = get_object_or_404(Service, pk=pk)
	form = ServiceForm(request.POST if request.method == "POST" else None, instance=service)
	if request.method == "POST":
		if form.is_valid():
			form.save()
			messages.success(request, "Service updated successfully.")
			return redirect("services")
		messages.error(request, "Please correct the errors in the form.")

	return render(request, "services.html", {
		"form": form,
		"services": Service.objects.all(),
		"is_editing": True,
		"editing_record": service,
	})


@require_POST
@login_required
def delete_service(request, pk):
	"""DELETE: find the service and remove it if no bill details depend on it."""
	service = get_object_or_404(Service, pk=pk)
	try:
		service.delete()
	except ProtectedError:
		messages.error(request, "This service cannot be deleted because it is still in use.")
	else:
		messages.success(request, "Service deleted successfully.")
	return redirect("services")


@require_POST
@login_required
def add_guest_bill(request):
	"""CREATE: validate the submitted form and save a new guest bill."""
	form = GuestBillForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, "Guest bill created successfully.")
		return redirect("guestbill")

	messages.error(request, "Please correct the errors in the form.")
	return render(request, "guestbill.html", {
		"form": form,
		"bills": GuestBill.objects.all(),
		"is_editing": False,
	})


@login_required
def guest_bill_list(request):
	"""READ: get all guest bills and display them in the guest bills table."""
	return render(request, "guestbill.html", {
		"form": GuestBillForm(),
		"bills": GuestBill.objects.all(),
		"is_editing": False,
	})


@login_required
def update_guest_bill(request, pk):
	"""UPDATE: find a guest bill, validate changed fields, and save the update."""
	bill = get_object_or_404(GuestBill, pk=pk)
	form = GuestBillForm(request.POST if request.method == "POST" else None, instance=bill)
	if request.method == "POST":
		if form.is_valid():
			form.save()
			messages.success(request, "Guest bill updated successfully.")
			return redirect("guestbill")
		messages.error(request, "Please correct the errors in the form.")

	return render(request, "guestbill.html", {
		"form": form,
		"bills": GuestBill.objects.all(),
		"is_editing": True,
		"editing_record": bill,
	})


@require_POST
@login_required
def delete_guest_bill(request, pk):
	"""DELETE: find the guest bill and delete it, including its bill details."""
	bill = get_object_or_404(GuestBill, pk=pk)
	bill.delete()
	messages.success(request, "Guest bill deleted successfully.")
	return redirect("guestbill")


@require_POST
@login_required
def add_bill_detail(request):
	"""CREATE: validate the submitted form and save a new bill detail."""
	form = BillDetailForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, "Bill detail created successfully.")
		return redirect("billdetails")

	messages.error(request, "Please correct the errors in the form.")
	return render(request, "billdetails.html", {
		"form": form,
		"bill_details": BillDetail.objects.all(),
		"is_editing": False,
	})


@login_required
def bill_detail_list(request):
	"""READ: get all bill details and display them in the bill details table."""
	return render(request, "billdetails.html", {
		"form": BillDetailForm(),
		"bill_details": BillDetail.objects.all(),
		"is_editing": False,
	})


@login_required
def update_bill_detail(request, pk):
	"""UPDATE: find a bill detail, validate changed fields, and save the update."""
	detail = get_object_or_404(BillDetail, pk=pk)
	form = BillDetailForm(request.POST if request.method == "POST" else None, instance=detail)
	if request.method == "POST":
		if form.is_valid():
			form.save()
			messages.success(request, "Bill detail updated successfully.")
			return redirect("billdetails")
		messages.error(request, "Please correct the errors in the form.")

	return render(request, "billdetails.html", {
		"form": form,
		"bill_details": BillDetail.objects.all(),
		"is_editing": True,
		"editing_record": detail,
	})


@require_POST
@login_required
def delete_bill_detail(request, pk):
	"""DELETE: find the bill detail and remove it from the database."""
	detail = get_object_or_404(BillDetail, pk=pk)
	detail.delete()
	messages.success(request, "Bill detail deleted successfully.")
	return redirect("billdetails")


@require_POST
@login_required
def add_payment(request):
	"""CREATE: validate the submitted form and save a new payment."""
	form = PaymentForm(request.POST)
	if form.is_valid():
		form.save()
		messages.success(request, "Payment created successfully.")
		return redirect("payment")

	messages.error(request, "Please correct the errors in the form.")
	return render(request, "payment.html", {
		"form": form,
		"payments": Payment.objects.all(),
		"is_editing": False,
	})


@login_required
def payment_list(request):
	"""READ: get all payments and display them in the payments table."""
	return render(request, "payment.html", {
		"form": PaymentForm(),
		"payments": Payment.objects.all(),
		"is_editing": False,
	})


@login_required
def update_payment(request, pk):
	"""UPDATE: find a payment, validate changed fields, and save the update."""
	payment = get_object_or_404(Payment, pk=pk)
	form = PaymentForm(request.POST if request.method == "POST" else None, instance=payment)
	if request.method == "POST":
		if form.is_valid():
			form.save()
			messages.success(request, "Payment updated successfully.")
			return redirect("payment")
		messages.error(request, "Please correct the errors in the form.")

	return render(request, "payment.html", {
		"form": form,
		"payments": Payment.objects.all(),
		"is_editing": True,
		"editing_record": payment,
	})


@require_POST
@login_required
def delete_payment(request, pk):
	"""DELETE: find the payment and remove it from the database."""
	payment = get_object_or_404(Payment, pk=pk)
	payment.delete()
	messages.success(request, "Payment deleted successfully.")
	return redirect("payment")
