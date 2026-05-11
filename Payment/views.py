import razorpay
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Payment


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = int(request.data.get("amount"))

        client = razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        ))

        payment_data = {
            "amount": amount * 100,
            "currency": "INR",
            "payment_capture": 1,
        }

        order = client.order.create(data=payment_data)

        Payment.objects.create(
            user=request.user,
            amount=amount,
            order_id=order["id"]
        )

        return Response({
            "order_id": order["id"],
            "amount": amount,
            "key": settings.RAZORPAY_KEY_ID
        })
        
class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_id = request.data.get("razorpay_payment_id")
        order_id = request.data.get("razorpay_order_id")

        try:
            payment = Payment.objects.get(order_id=order_id)

            payment.payment_id = payment_id
            payment.status = "success"
            payment.save()

            return Response({
                "message": "Payment successful"
            })

        except Payment.DoesNotExist:
            return Response({
                "error": "Payment not found"
            }, status=404)