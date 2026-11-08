from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404

from .forms import PlantForm, RegisterForm
from .models import Plant, CareTask, CareLog


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


