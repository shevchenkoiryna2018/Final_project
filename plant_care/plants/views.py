from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from .forms import PlantForm, RegisterForm, CareTaskForm
from .models import Plant, CareTask, CareLog

from django.utils import timezone
from django.db import transaction
from django.views.decorators.http import require_POST


def register(request):
    if request.user.is_authenticated:
        return redirect('plants:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('plants:dashboard')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def index(request):
    return render(request, 'plants/index.html')


@login_required
def dashboard(request):
    plants = Plant.objects.filter(owner=request.user)

    context = {'plants': plants,}

    return render(request, 'plants/dashboard.html', context)


@login_required
def plant_create(request):
    if request.method == 'POST':
        form = PlantForm(request.POST)

        if form.is_valid():
            plant = form.save(commit=False)
            plant.owner = request.user
            plant.save()
            return redirect('plants:dashboard')

    else:
        form = PlantForm()

    return render(request, 'plants/plant_form.html', {'form': form})


@login_required
def plant_update(request, id):
    plant = get_object_or_404(Plant, id=id, owner=request.user)

    if request.method == 'POST':
        form = PlantForm(request.POST, instance=plant)

        if form.is_valid():
            form.save()
            return redirect('plants:dashboard')

    else:
        form = PlantForm(instance=plant)

    return render(request, 'plants/plant_form.html', {'form': form})


@login_required
def plant_delete(request, id):
    plant = get_object_or_404(Plant, id=id, owner=request.user)

    if request.method == 'POST':
        plant.delete()
        return redirect('plants:dashboard')

    return render(request, 'plants/plant_confirm_delete.html', {'plant': plant})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = CareTaskForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            return redirect('plants:dashboard')
    else:
        form = CareTaskForm(user=request.user)

    return render(request, 'plants/task_form.html', {'form': form})


@login_required
def task_list(request):
    tasks = CareTask.objects.filter(plant__owner=request.user).order_by('is_completed', 'scheduled_date', 'priority')

    return render(request, 'plants/task_list.html', {'tasks': tasks})


@login_required
@require_POST
def task_complete(request, id):
    task = get_object_or_404(CareTask, id=id, plant__owner=request.user)

    if not task.is_completed:
        with transaction.atomic():
            task.is_completed = True
            task.save()

            CareLog.objects.create(
                plant=task.plant,
                task=task,
                care_type=task.task_type,
                notes=task.notes,
            )

            if task.task_type == 'watering':
                task.plant.last_watered = timezone.localdate()
                task.plant.save()

    return redirect('plants:task_list')



