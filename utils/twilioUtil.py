import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
from_number = os.environ["TWILIO_FROM_NUMBER"]
client = Client(account_sid, auth_token)


def send_otp_twilio(phone_number: str, otp_code: int):
    try:
        message = client.messages.create(
            body=f"OTP from SteetFoods is {otp_code}",
            from_=from_number,
            to="+91" + phone_number,
        )
        return message
    except TwilioRestException as err:
        logging.exception(err)
