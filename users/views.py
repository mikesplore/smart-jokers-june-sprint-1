from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from .models import User
import json


def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    if request.method == 'GET':
        return JsonResponse({'user': {
            'id': user.id,
            'email': user.email,
            'user_type': user.user_type,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'is_active': user.is_active,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
        }})
    return HttpResponseNotAllowed(['GET'])


@csrf_exempt
def user_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create(
                email=data['email'],
                user_type=data['user_type'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=data['phone_number'],
                is_active=data.get('is_active', True)
            )
            return JsonResponse({'id': user.id}, status=201)
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseNotAllowed(['POST'])


@csrf_exempt
def user_update(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user.email = data.get('email', user.email)
            user.user_type = data.get('user_type', user.user_type)
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.phone_number = data.get('phone_number', user.phone_number)
            user.is_active = data.get('is_active', user.is_active)
            user.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return HttpResponseBadRequest(str(e))
    return HttpResponseNotAllowed(['PUT'])


@csrf_exempt
def user_delete(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    if request.method == 'DELETE':
        user.delete()
        return JsonResponse({'success': True})
    return HttpResponseNotAllowed(['DELETE'])


@method_decorator(csrf_exempt, name='dispatch')
class UserProfileView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user = User.objects.create(
                email=data.get('email'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                phone_number=data.get('phone_number'),
                user_type=data.get('user_type'),
                is_active=data.get('is_active', True)
            )
            return JsonResponse({'message': 'User profile created successfully', 'user_id': user.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    def get(self, request, *args, **kwargs):
        return JsonResponse({'error': 'GET method is not allowed on this endpoint'}, status=405)

    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user = User.objects.get(id=kwargs.get('user_id'))

            # Update user fields
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.phone_number = data.get('phone_number', user.phone_number)
            user.user_type = data.get('user_type', user.user_type)
            user.save()

            return JsonResponse({'message': 'User profile updated successfully'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
