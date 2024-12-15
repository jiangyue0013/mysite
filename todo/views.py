from django.shortcuts import render, redirect
from django import forms
from django.template.context_processors import request
from django.utils.timezone import now
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'status', 'priority']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'placeholder': 'Select a date and time',
            }),
        }

    # Custom verification methods
    def clean_title(self):
        # check the length of title
        title = self.cleaned_data.get('title')
        if len(title) > 200:
            raise forms.ValidationError("The title must not exceed 200 characters!")
        return title

    def clean_deadline(self):
        # check the deadline time
        deadline = self.cleaned_data.get('deadline')
        if deadline < now():
            raise forms.ValidationError("The deadline can't be past time!")
        return deadline

# index view method: show all tasks
@login_required
def index(request):
    latest_task_list = Task.objects.filter(user=request.user).order_by('deadline')
    context = {"latest_task_list": latest_task_list}
    return render(request, "todo/index.html", context)

# create task view method: create new task
@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            form.save()
            messages.success(request,"Task created successfully!")
            return redirect(reverse('index'))
        else:
            messages.error(request, "Failed to create the task. Please check the input.")
    else:
        form = TaskForm()

    return render(request, "todo/create_task.html", {'form': form})

# deelete task by id
@login_required
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.delete()
        messages.success(request, "Task deleted successfully!")
    except Task.DoesNotExist:
        messages.success(request, "Task does not exist!")

    return redirect(reverse('index'))

# update task by id
@login_required
def update_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id, user=request.user)
    except Task.DoesNotExist:
        messages.success(request, "Task does not exist!")
        return redirect(reverse('index'))

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect(reverse('index'))
        else:
            messages.error(request, "Failed to update the task. Please check the input.")
    else:
        form = TaskForm(instance=task)

    return render(request, "todo/update_task.html", {'form': form, 'task': task})
