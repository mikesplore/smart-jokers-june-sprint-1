from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User


def user_list(request):
    if request.method == 'GET':
        users = list(User.objects.values())
        return JsonResponse({'users': users})
    return HttpResponseNotAllowed(['GET'])


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
