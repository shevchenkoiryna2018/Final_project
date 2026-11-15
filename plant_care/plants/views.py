from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

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
            messages.success(request, 'Обліковий запис успішно створено! Ласкаво просимо до PlantCare!')
            return redirect('plants:dashboard')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def index(request):
    return render(request, 'plants/index.html')


@login_required
def dashboard(request):
    plants = Plant.objects.filter(owner=request.user)
    tasks = CareTask.objects.filter(plant__owner=request.user)
    overdue_watering_count = sum(1 for plant in plants if plant.is_watering_overdue())

    search_query = request.GET.get('q', '').strip()
    watering_filter = request.GET.get('watering', 'all')
    sort_by = request.GET.get('sort', 'name_asc')
    if search_query:
        query = search_query.casefold()

        filtered_plants = [
            plant for plant in plants
            if query in plant.name.casefold() or query in plant.species.casefold()
        ]
    else:
        filtered_plants = plants

    if watering_filter == 'overdue':
        filtered_plants = [
            plant for plant in filtered_plants
            if plant.is_watering_overdue()
        ]

    if sort_by == 'name_desc':
        filtered_plants = sorted(
            filtered_plants,
            key=lambda plant: plant.name.casefold(),
            reverse=True
        )

    elif sort_by == 'newest':
        filtered_plants = sorted(
            filtered_plants,
            key=lambda plant: plant.created_at,
            reverse=True
        )

    elif sort_by == 'oldest':
        filtered_plants = sorted(
            filtered_plants,
            key=lambda plant: plant.created_at
        )

    elif sort_by == 'watering':
        filtered_plants = sorted(
            filtered_plants,
            key=lambda plant: (
                plant.get_next_watering_date() is None,
                plant.get_next_watering_date()
            )
        )

    else:
        filtered_plants = sorted(
            filtered_plants,
            key=lambda plant: plant.name.casefold()
        )

    context = {
        'plants': filtered_plants,
        'plants_count': plants.count(),
        'pending_tasks_count': tasks.filter(is_completed=False).count(),
        'completed_tasks_count': tasks.filter(is_completed=True).count(),
        'overdue_watering_count': overdue_watering_count,
        'overdue_tasks_count': tasks.filter(is_completed=False, scheduled_date__lt=timezone.localdate()).count(),
        'search_query': search_query,
        'watering_filter': watering_filter,
        'sort_by': sort_by,
    }

    return render(request, 'plants/dashboard.html', context)


@login_required
def plant_create(request):
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES)

        if form.is_valid():
            plant = form.save(commit=False)
            plant.owner = request.user
            plant.save()
            messages.success(request, 'Рослину успішно додано!')
            return redirect('plants:dashboard')

    else:
        form = PlantForm()

    return render(request, 'plants/plant_form.html', {'form': form})


@login_required
def plant_update(request, id):
    plant = get_object_or_404(Plant, id=id, owner=request.user)

    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES, instance=plant)

        if form.is_valid():
            form.save()
            messages.success(request, 'Зміни успішно збережено!')
            return redirect('plants:dashboard')

    else:
        form = PlantForm(instance=plant)

    return render(request, 'plants/plant_form.html', {'form': form})


@login_required
def plant_delete(request, id):
    plant = get_object_or_404(Plant, id=id, owner=request.user)

    if request.method == 'POST':
        plant.delete()
        messages.success(request, 'Рослину успішно видалено!')
        return redirect('plants:dashboard')

    return render(request, 'plants/plant_confirm_delete.html', {'plant': plant})


@login_required
def task_create(request):
    if request.method == 'POST':
        form = CareTaskForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Завдання успішно створено!')
            return redirect('plants:task_list')
    else:
        form = CareTaskForm(user=request.user)

    return render(request, 'plants/task_form.html', {'form': form})


@login_required
def task_update(request, id):
    task = get_object_or_404(CareTask, id=id, plant__owner=request.user, is_completed=False)

    if request.method == 'POST':
        form = CareTaskForm(request.POST, user=request.user, instance=task)

        if form.is_valid():
            form.save()
            messages.success(request, 'Завдання успішно оновлено!')
            return redirect('plants:task_list')

    else:
        form = CareTaskForm(user=request.user, instance=task)

    return render(request, 'plants/task_form.html', {'form': form})


@login_required
def task_delete(request, id):
    task = get_object_or_404(CareTask, id=id, plant__owner=request.user, is_completed=False)

    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Завдання успішно видалено!')
        return redirect('plants:task_list')

    return render(request, 'plants/task_confirm_delete.html', {'task': task})


@login_required
def task_list(request):
    tasks = CareTask.objects.filter(plant__owner=request.user)

    status = request.GET.get('status', 'all')

    if status == 'pending':
        tasks = tasks.filter(is_completed=False)

    elif status == 'completed':
        tasks = tasks.filter(is_completed=True)

    elif status == 'overdue':
        tasks = tasks.filter(is_completed=False, scheduled_date__lt=timezone.localdate())

    tasks = tasks.order_by('is_completed', 'scheduled_date', 'priority')

    return render(request, 'plants/task_list.html', {'tasks': tasks, 'status': status})


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

        messages.success(request, 'Завдання виконано! Запис додано до історії догляду.')

    return redirect('plants:task_list')


@login_required
def care_history(request):
    history = CareLog.objects.filter(plant__owner=request.user).order_by('-performed_at')

    return render(request, 'plants/care_history.html', {'history': history})


