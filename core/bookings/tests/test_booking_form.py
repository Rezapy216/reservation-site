from django.test import SimpleTestCase,TestCase
from datetime import datetime, timedelta

from ..forms import BookingForm


# class TestBookingForm(TestCase):

#     def test_post_form_with_valid_data(self):
#         form = BookingForm(data={
#             'date_in': datetime.today(),
#             'date_out': datetime.today() + timedelta(days=3),
#             'number_of_people': 3
#         })
#         self.assertTrue(form.is_valid())
