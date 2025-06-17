from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import User


class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

class UserDetailView(DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user'

class UserCreateView(CreateView):
    model = User
    fields = ['email', 'user_type', 'first_name', 'last_name', 'phone_number', 'is_active']
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user-list')

class UserUpdateView(UpdateView):
    model = User
    fields = ['email', 'user_type', 'first_name', 'last_name', 'phone_number', 'is_active']
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('user-list')

class UserDeleteView(DeleteView):
    model = User
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('user-list')
