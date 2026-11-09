from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import timedelta
from django.utils import timezone


class Plant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plants', verbose_name='Власник')
    name = models.CharField(max_length=100, verbose_name='Назва рослини')
    species = models.CharField(max_length=100, verbose_name='Вид рослини')
    acquired_date = models.DateField(null=True, blank=True, verbose_name='Дата придбання')
    watering_interval = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='Інтервал поливу (днів)')
    last_watered = models.DateField(null=True, blank=True, verbose_name='Дата останнього поливу')
    location = models.CharField(max_length=100, blank=True, verbose_name='Розташування')
    notes = models.TextField(blank=True, verbose_name='Додаткова інформація')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата додавання')

    def __str__(self):
        return self.name

    def get_next_watering_date(self):
        if self.last_watered:
            return self.last_watered + timedelta(days=self.watering_interval)

        return None

    def is_watering_overdue(self):
        next_date = self.get_next_watering_date()

        if next_date:
            return next_date < timezone.localdate()

        return False

    class Meta:
        ordering = ['name']
        verbose_name = 'Рослина'
        verbose_name_plural = 'Рослини'


class CareTask(models.Model):
    TASK_TYPES = [
        ('watering', 'Полив'),
        ('fertilizing', 'Підживлення'),
        ('repotting', 'Пересадка'),
        ('pruning', 'Обрізка'),
        ('other', 'Інше'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Високий'),
        (2, 'Середній'),
        (3, 'Низький'),
    ]

    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='tasks', verbose_name='Рослина')
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, verbose_name='Тип догляду')
    scheduled_date = models.DateField(verbose_name='Запланована дата')
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=2, verbose_name='Пріоритет')
    is_completed = models.BooleanField(default=False, verbose_name='Виконано')
    notes = models.TextField(blank=True, verbose_name='Примітки')

    def __str__(self):
        return f'{self.get_task_type_display()} - {self.plant.name}'

    def is_overdue(self):
        return (not self.is_completed and self.scheduled_date < timezone.localdate())

    class Meta:
        ordering = ['scheduled_date', 'priority']
        verbose_name = 'Завдання з догляду'
        verbose_name_plural = 'Завдання з догляду'


class CareLog(models.Model):
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='care_history', verbose_name='Рослина')
    task = models.ForeignKey(CareTask, on_delete=models.SET_NULL, null=True, blank=True, related_name='history_records', verbose_name='Завдання')
    care_type = models.CharField(max_length=20, choices=CareTask.TASK_TYPES, verbose_name='Тип догляду')
    performed_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата та час виконання')
    notes = models.TextField(blank=True, verbose_name='Примітки')

    def __str__(self):
        return f'{self.get_care_type_display()} - {self.plant.name}'

    class Meta:
        ordering = ['-performed_at']
        verbose_name = 'Запис історії догляду'
        verbose_name_plural = 'Історія догляду'

