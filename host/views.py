from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import HostDetail,CanCall
from .serializer import HostDetailSerializer
from datetime import datetime
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import ssl

class SendMailView(APIView):
    def post(self, request):
        try:
            recipient_email = request.data.get('recipient_email')
            subject = request.data.get('subject')
            message = request.data.get('message')
            html_message = request.data.get('html_message', None)
            
            # Validate required fields
            if not recipient_email or not subject or not message:
                return Response({
                    'status': 'error',
                    'message': 'recipient_email, subject, and message are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create SSL context that doesn't verify certificate
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return Response({
                'status': 'success',
                'message': 'Email sent successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Failed to send email: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class HostDetailCreateUpdateView(APIView):
    def post(self, request):
        mobile_number = request.data.get('mobile_number')
        
        try:
            host = HostDetail.objects.get(mobile_number=mobile_number)
            serializer = HostDetailSerializer(host, data=request.data)
        except HostDetail.DoesNotExist:
            serializer = HostDetailSerializer(data=request.data)
            
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Done',
                'data': "Done"
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 'error',
            'message': 'Invalid data',
            'errors': "Not Done"
        }, status=status.HTTP_400_BAD_REQUEST)

class HostListView(APIView):
    def get(self, request):
        hosts = HostDetail.objects.all()
        serializer = HostDetailSerializer(hosts, many=True)
        
        # Convert UTC to local time for each host
        for host in serializer.data:
            utc_time = datetime.strptime(host['last_active'], '%Y-%m-%dT%H:%M:%S.%fZ')
            local_time = timezone.localtime(timezone.make_aware(utc_time))
            host['last_active'] = local_time.strftime('%Y-%m-%d %H:%M:%S')
            
        return Response({
            'status': 'success',
            'message': 'Hosts retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        hosts = HostDetail.objects.all()
        serializer = HostDetailSerializer(hosts, many=True)
        return Response({
            'status': 'success',
            'message': 'Hosts retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
class CanCallView(APIView):
    def get(self, request):
        can_call = CanCall.objects.first()
        if can_call:
            return Response({
                'status': 'success',
                'message': 'Can call retrieved successfully',
                'data': {'can_call': can_call.can_call}
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'error',
                'message': 'Can call not found'
            }, status=status.HTTP_404_NOT_FOUND)