from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import (
	BillDetail,
	Guest,
	GuestBill,
	Payment,
	Reservation,
	Room,
	RoomType,
	Service,
	Staff,
)


class HotelPageTests(TestCase):
	def authenticate_test_user(self):
		user = User.objects.create_user(
			username="hotelguest",
			password="T3al!SatelliteRiver#82",
		)
		self.client.force_login(user)

	def test_logout_clears_session_and_redirects_home(self):
		User.objects.create_user(
			username="hotelguest",
			password="T3al!SatelliteRiver#82",
		)
		self.client.login(
			username="hotelguest",
			password="T3al!SatelliteRiver#82",
		)

		response = self.client.post(reverse("logout"), follow=True)

		self.assertRedirects(response, reverse("home"))
		self.assertFalse(response.wsgi_request.user.is_authenticated)
		self.assertContains(response, "You have been logged out.")

	def test_logout_rejects_get_requests(self):
		response = self.client.get(reverse("logout"))

		self.assertEqual(response.status_code, 405)

	def test_login_authenticates_user_and_redirects_home(self):
		User.objects.create_user(
			username="hotelguest",
			password="T3al!SatelliteRiver#82",
		)

		response = self.client.post(
			reverse("login"),
			{
				"username": "hotelguest",
				"password": "T3al!SatelliteRiver#82",
			},
			follow=True,
		)

		self.assertRedirects(response, reverse("home"))
		self.assertTrue(response.wsgi_request.user.is_authenticated)
		self.assertContains(response, "Signed in successfully.")

	def test_login_rejects_incorrect_password(self):
		User.objects.create_user(
			username="hotelguest",
			password="T3al!SatelliteRiver#82",
		)

		response = self.client.post(
			reverse("login"),
			{
				"username": "hotelguest",
				"password": "incorrect-password",
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.wsgi_request.user.is_authenticated)
		self.assertContains(response, "Please check your username and password.")

	def test_protected_page_returns_to_requested_page_after_login(self):
		User.objects.create_user(
			username="hotelguest",
			password="T3al!SatelliteRiver#82",
		)

		response = self.client.get(reverse("guest"))

		self.assertRedirects(
			response,
			f"{reverse('login')}?next={reverse('guest')}",
			fetch_redirect_response=False,
		)
		response = self.client.post(
			reverse("login"),
			{
				"username": "hotelguest",
				"password": "T3al!SatelliteRiver#82",
				"next": reverse("guest"),
			},
			follow=True,
		)

		self.assertRedirects(response, reverse("guest"))
		self.assertTrue(response.wsgi_request.user.is_authenticated)

	def test_unauthenticated_user_cannot_create_hotel_records(self):
		response = self.client.post(
			reverse("add_service"),
			{
				"service_id": "SV101",
				"name": "Laundry",
				"description": "Laundry service",
				"cost": "15000",
				"availability": Service.Availability.AVAILABLE,
			},
		)

		self.assertRedirects(
			response,
			f"{reverse('login')}?next={reverse('add_service')}",
			fetch_redirect_response=False,
		)
		self.assertFalse(Service.objects.filter(service_id="SV101").exists())

	def test_login_rejects_external_next_url(self):
		User.objects.create_user(
			username="hotelguest",
			password="T3al!SatelliteRiver#82",
		)

		response = self.client.post(
			reverse("login"),
			{
				"username": "hotelguest",
				"password": "T3al!SatelliteRiver#82",
				"next": "https://example.com/",
			},
			follow=True,
		)

		self.assertRedirects(response, reverse("home"))

	def test_registration_creates_user_signs_them_in_and_redirects_home(self):
		response = self.client.post(
			reverse("register"),
			{
				"username": "hotelguest",
				"password1": "T3al!SatelliteRiver#82",
				"password2": "T3al!SatelliteRiver#82",
			},
			follow=True,
		)

		self.assertRedirects(response, reverse("home"))
		user = User.objects.get(username="hotelguest")
		self.assertTrue(user.check_password("T3al!SatelliteRiver#82"))
		self.assertNotEqual(user.password, "T3al!SatelliteRiver#82")
		self.assertTrue(response.wsgi_request.user.is_authenticated)
		self.assertContains(response, "Your account was created and you are now signed in.")

	def test_registration_rejects_mismatched_passwords(self):
		response = self.client.post(
			reverse("register"),
			{
				"username": "hotelguest",
				"password1": "T3al!SatelliteRiver#82",
				"password2": "DifferentPassword#2026",
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(User.objects.filter(username="hotelguest").exists())

	def test_hotel_pages_render(self):
		self.authenticate_test_user()
		page_names = [
			"home",
			"login",
			"guest",
			"staff",
			"roomtype",
			"room",
			"reservation",
			"services",
			"guestbill",
			"billdetails",
			"payment",
		]

		for page_name in page_names:
			with self.subTest(page=page_name):
				response = self.client.get(reverse(page_name))
				self.assertEqual(response.status_code, 200)

	def test_service_form_saves_and_shows_success_message(self):
		self.authenticate_test_user()
		response = self.client.post(
			reverse("add_service"),
			{
				"service_id": "SV100",
				"name": "Laundry",
				"description": "Laundry service",
				"cost": "15000",
				"availability": Service.Availability.AVAILABLE,
			},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(Service.objects.filter(service_id="SV100").exists())
		self.assertContains(response, "Service created successfully.")
		self.assertContains(response, "SV100")

	def test_invalid_service_form_does_not_save(self):
		self.authenticate_test_user()
		response = self.client.post(
			reverse("add_service"),
			{
				"service_id": "SV101",
				"name": "Laundry",
				"description": "",
				"cost": "15000",
				"availability": Service.Availability.AVAILABLE,
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Service.objects.filter(service_id="SV101").exists())
		self.assertContains(response, "Please correct the errors in the form.")

	def test_service_can_be_read_updated_and_deleted(self):
		self.authenticate_test_user()
		service = Service.objects.create(
			service_id="SV102",
			name="Laundry",
			description="Laundry service",
			cost="15000",
			availability=Service.Availability.AVAILABLE,
		)

		edit_url = reverse("update_service", kwargs={"pk": service.pk})
		edit_response = self.client.get(edit_url)
		self.assertEqual(edit_response.status_code, 200)
		self.assertContains(edit_response, 'value="Laundry"')
		self.assertContains(edit_response, "Delete")

		update_response = self.client.post(
			edit_url,
			{
				"service_id": service.pk,
				"name": "Room service",
				"description": "Food delivery",
				"cost": "20000",
				"availability": Service.Availability.AVAILABLE,
			},
			follow=True,
		)
		self.assertEqual(update_response.status_code, 200)
		service.refresh_from_db()
		self.assertEqual(service.name, "Room service")
		self.assertContains(update_response, "Service updated successfully.")

		delete_url = reverse("delete_service", kwargs={"pk": service.pk})
		self.assertEqual(self.client.get(delete_url).status_code, 405)
		delete_response = self.client.post(delete_url, follow=True)
		self.assertEqual(delete_response.status_code, 200)
		self.assertFalse(Service.objects.filter(pk=service.pk).exists())
		self.assertContains(delete_response, "Service deleted successfully.")

	def test_protected_record_cannot_be_deleted(self):
		self.authenticate_test_user()
		guest = Guest.objects.create(
			guest_id="G100",
			first_name="Ari",
			last_name="Guest",
			contact="123456789",
			email="ari@example.com",
			address="Hotel Road",
			nationality="Example",
			gender=Guest.Gender.OTHER,
		)
		room_type = RoomType.objects.create(
			room_type_id="RT100",
			name="Standard",
			description="Standard room",
			capacity=2,
			price_per_night="100",
		)
		room = Room.objects.create(
			room_id="R100",
			room_type=room_type,
			room_number="100",
			floor=1,
			status=Room.Status.AVAILABLE,
		)
		Reservation.objects.create(
			reservation_id="RS100",
			guest=guest,
			room=room,
			reservation_date="2026-01-01",
			check_in_date="2026-01-10",
			check_out_date="2026-01-12",
			status=Reservation.Status.CONFIRMED,
		)

		response = self.client.post(
			reverse("delete_guest", kwargs={"pk": guest.pk}),
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(Guest.objects.filter(pk=guest.pk).exists())
		self.assertContains(response, "This guest cannot be deleted because it is still in use.")

	def test_each_model_has_working_create_read_update_and_delete_pages(self):
		self.authenticate_test_user()
		records = [
			(
				"guest",
				"add_guest",
				"update_guest",
				"delete_guest",
				"G200",
				{
					"guest_id": "G200",
					"first_name": "Ari",
					"last_name": "Guest",
					"contact": "123456789",
					"email": "ari@example.com",
					"address": "Hotel Road",
					"nationality": "Example",
					"gender": Guest.Gender.OTHER,
				},
				"first_name",
				"Ari Updated",
			),
			(
				"staff",
				"add_staff",
				"update_staff",
				"delete_staff",
				"S200",
				{
					"staff_id": "S200",
					"first_name": "Sam",
					"last_name": "Staff",
					"email": "sam@example.com",
					"contact": "123456789",
					"role": "Receptionist",
					"salary": "1000",
					"gender": Staff.Gender.OTHER,
				},
				"role",
				"Manager",
			),
			(
				"roomtype",
				"add_room_type",
				"update_room_type",
				"delete_room_type",
				"RT200",
				{
					"room_type_id": "RT200",
					"name": "Standard",
					"description": "Standard room",
					"capacity": "2",
					"price_per_night": "100",
				},
				"name",
				"Suite",
			),
			(
				"room",
				"add_room",
				"update_room",
				"delete_room",
				"R200",
				{
					"room_id": "R200",
					"room_type": "RT200",
					"room_number": "200",
					"floor": "2",
					"status": Room.Status.AVAILABLE,
				},
				"room_number",
				"201",
			),
			(
				"reservation",
				"add_reservation",
				"update_reservation",
				"delete_reservation",
				"RS200",
				{
					"reservation_id": "RS200",
					"guest": "G200",
					"room": "R200",
					"reservation_date": "2026-01-01",
					"check_in_date": "2026-01-10",
					"check_out_date": "2026-01-12",
					"status": Reservation.Status.CONFIRMED,
				},
				"status",
				Reservation.Status.PENDING,
			),
			(
				"services",
				"add_service",
				"update_service",
				"delete_service",
				"SV200",
				{
					"service_id": "SV200",
					"name": "Laundry",
					"description": "Laundry service",
					"cost": "15",
					"availability": Service.Availability.AVAILABLE,
				},
				"name",
				"Room service",
			),
			(
				"guestbill",
				"add_guest_bill",
				"update_guest_bill",
				"delete_guest_bill",
				"B200",
				{
					"bill_id": "B200",
					"guest": "G200",
					"reservation": "RS200",
					"total_amount": "100",
					"tax": "10",
					"discount": "0",
					"final_amount": "110",
					"bill_date": "2026-01-12",
					"status": GuestBill.Status.PAID,
				},
				"discount",
				"5",
			),
			(
				"billdetails",
				"add_bill_detail",
				"update_bill_detail",
				"delete_bill_detail",
				"BD200",
				{
					"detail_id": "BD200",
					"bill": "B200",
					"service": "SV200",
					"quantity": "1",
					"unit_price": "15",
					"total_amount": "15",
				},
				"quantity",
				"2",
			),
			(
				"payment",
				"add_payment",
				"update_payment",
				"delete_payment",
				"P200",
				{
					"payment_id": "P200",
					"reservation": "RS200",
					"payment_date": "2026-01-12",
					"amount": "110",
					"payment_method": Payment.Method.CASH,
					"payment_status": Payment.Status.PAID,
				},
				"amount",
				"120",
			),
		]

		# CREATE: submit each model's form and confirm it redirects after saving.
		for list_name, add_name, _, _, pk, form_data, _, _ in records:
			with self.subTest(create=add_name):
				response = self.client.post(reverse(add_name), form_data)
				self.assertEqual(response.status_code, 302)

		# READ: open each list page and confirm the saved records are displayed.
		for list_name, _, _, _, pk, _, _, _ in records:
			with self.subTest(read=list_name):
				response = self.client.get(reverse(list_name))
				self.assertEqual(response.status_code, 200)
				self.assertContains(response, pk)

		# UPDATE: submit changed values through each model's dedicated update page.
		for list_name, _, update_name, _, pk, form_data, field, new_value in records:
			with self.subTest(update=update_name):
				form_data[field] = new_value
				response = self.client.post(
					reverse(update_name, kwargs={"pk": pk}),
					form_data,
				)
				self.assertEqual(response.status_code, 302)

		# DELETE: remove dependent records first so protected relationships stay valid.
		for _, _, _, delete_name, pk, _, _, _ in reversed(records):
			with self.subTest(delete=delete_name):
				response = self.client.post(
					reverse(delete_name, kwargs={"pk": pk}),
				)
				self.assertEqual(response.status_code, 302)
