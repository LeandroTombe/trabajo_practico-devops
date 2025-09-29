from django.db import models


class User(models.Model):
    """Modelo para usuarios de ejemplo"""
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Product(models.Model):
    """Modelo para productos de ejemplo"""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Todo(models.Model):
    """Modelo para tareas/todos - almacenamiento principal en PostgreSQL"""
    title = models.CharField(max_length=255)
    done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Todo #{self.id}: {self.title}"
    
    class Meta:
        ordering = ['-created_at']  # Más recientes primero
        
    def to_dict(self):
        """Serializar a diccionario para JSON response"""
        return {
            'id': self.id,
            'title': self.title,
            'done': self.done,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }