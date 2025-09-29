import os
import time
import random
import json
import redis
from typing import Dict, Any, List
from datetime import timedelta

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from redis import Redis
from urllib.parse import urlparse
from .models import Todo


def get_redis() -> Redis:
    redis_url = os.environ.get("REDIS_URL")
    try:
        if redis_url:
            # Para Render/producción - usa REDIS_URL
            r = Redis.from_url(redis_url, decode_responses=True)
            # Test conexión
            r.ping()
            return r
        else:
            # Para desarrollo local
            r = Redis(
                host=os.environ.get("REDIS_HOST", "localhost"),
                port=int(os.environ.get("REDIS_PORT", "6379")),
                db=int(os.environ.get("REDIS_DB", "0")),
                decode_responses=True,
            )
            r.ping()
            return r
    except Exception as e:
        print(f"Redis connection error: {e}")
        print(f"REDIS_URL: {redis_url}")
        raise

# ARQUITECTURA ACTUALIZADA:
# - TODOs ahora se almacenan en PostgreSQL (modelo Django)
# - Redis se usa SOLO para caché temporal de consultas
# - Esto es más escalable y sigue mejores prácticas

@method_decorator(csrf_exempt, name="dispatch")
class HealthView(APIView):
    def get(self, request):
        r = get_redis()
        try:
            pong = r.ping()
            return Response({"ok": True, "redis": pong}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"ok": False, "error": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

@method_decorator(csrf_exempt, name="dispatch")
class TodoList(APIView):
    """Lista y crea TODOs usando PostgreSQL como almacén principal"""
    
    def get(self, request):
        """Obtener todas las tareas desde PostgreSQL"""
        try:
            todos = Todo.objects.all()
            todos_data = [todo.to_dict() for todo in todos]
            return Response(todos_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"detail": f"Error obteniendo tareas: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Crear nueva tarea en PostgreSQL"""
        try:
            title = (request.data or {}).get("title")
            if not title or not isinstance(title, str):
                return Response(
                    {"detail": "title (string) es requerido."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Crear tarea en PostgreSQL
            todo = Todo.objects.create(title=title.strip())
            
            # Invalidar caché de datos (si existe)
            try:
                r = get_redis()
                r.delete("todos_data_cache")
            except:
                pass  # Si Redis falla, no importa para el funcionamiento principal
                
            return Response(todo.to_dict(), status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": f"Error creando tarea: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(csrf_exempt, name="dispatch")
class TodoDetail(APIView):
    """Actualiza y elimina TODOs específicos usando PostgreSQL"""
    
    def patch(self, request, todo_id: int):
        """Actualizar tarea específica en PostgreSQL"""
        try:
            todo = Todo.objects.get(id=todo_id)
        except Todo.DoesNotExist:
            return Response({"detail": "No existe."}, status=status.HTTP_404_NOT_FOUND)

        try:
            payload = request.data or {}
            updated = False

            if "title" in payload:
                title = payload.get("title")
                if not isinstance(title, str):
                    return Response(
                        {"detail": "title debe ser string."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                todo.title = title.strip()
                updated = True

            if "done" in payload:
                done = payload.get("done")
                if not isinstance(done, bool):
                    return Response(
                        {"detail": "done debe ser booleano."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                todo.done = done
                updated = True

            if not updated:
                return Response(
                    {"detail": "Nada para actualizar."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            todo.save()
            
            # Invalidar caché
            try:
                r = get_redis()
                r.delete("todos_data_cache")
            except:
                pass
                
            return Response(todo.to_dict(), status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"detail": f"Error actualizando tarea: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, todo_id: int):
        """Eliminar tarea específica de PostgreSQL"""
        try:
            todo = Todo.objects.get(id=todo_id)
            todo.delete()
            
            # Invalidar caché
            try:
                r = get_redis()
                r.delete("todos_data_cache")
            except:
                pass
                
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Todo.DoesNotExist:
            return Response({"detail": "No existe."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"detail": f"Error eliminando tarea: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class DataView(APIView):
    """Endpoint simple para cargar y mostrar datos con caché"""
    
    def get(self, request):
        """Obtiene datos de tareas reales, usando caché si está disponible"""
        try:
            r = get_redis()
            cache_key = "todos_data_cache"
            
            # Intentar obtener datos del caché
            cached_data = r.get(cache_key)
            
            if cached_data:
                # Datos encontrados en caché
                data = json.loads(cached_data)
                data['from_cache'] = True
                data['load_time'] = 0  # Instantáneo desde caché
                return Response(data)
            
            # Cargar datos desde PostgreSQL con operaciones SÚPER COSTOSAS
            start_time = time.time()
            
            # 1. Múltiples consultas de agregación PESADAS
            total_todos = Todo.objects.count()
            completed_todos = Todo.objects.filter(done=True).count()
            pending_todos = Todo.objects.filter(done=False).count()
            
            # 2. Consultas con filtros complejos y rangos de fechas
            today = timezone.now().date()
            week_ago = timezone.now() - timedelta(days=7)
            month_ago = timezone.now() - timedelta(days=30)
            year_ago = timezone.now() - timedelta(days=365)
            
            # 3. CONSULTAS SÚPER PESADAS (simula reportes complejos reales)
            today_todos = Todo.objects.filter(created_at__date=today).count()
            week_todos = Todo.objects.filter(created_at__gte=week_ago).count()
            month_todos = Todo.objects.filter(created_at__gte=month_ago).count()
            year_todos = Todo.objects.filter(created_at__gte=year_ago).count()
            recent_completed = Todo.objects.filter(done=True, updated_at__gte=week_ago).count()
            
            # 4. Agregaciones por día (MUY COSTOSO)
            daily_stats = {}
            for days_back in range(7):  # Últimos 7 días
                date = today - timedelta(days=days_back)
                daily_count = Todo.objects.filter(created_at__date=date).count()
                daily_completed = Todo.objects.filter(created_at__date=date, done=True).count()
                daily_stats[str(date)] = {
                    'created': daily_count,
                    'completed': daily_completed
                }
            
            # 5. Consultas con LIKE patterns (SÚPER LENTO)
            urgent_todos = Todo.objects.filter(title__icontains='urgent').count()
            important_todos = Todo.objects.filter(title__icontains='important').count()
            critical_todos = Todo.objects.filter(title__icontains='critical').count()
            
            # 6. Consulta principal con ordenamiento COSTOSO
            todos_queryset = Todo.objects.all().order_by('-created_at', 'title')
            
            # 7. Procesamiento individual PESADO (simula lógica de negocio compleja)
            todos = []
            word_count_total = 0
            avg_title_length = 0
            
            for todo in todos_queryset:
                # Verificaciones individuales costosas
                is_recent = (timezone.now() - todo.created_at).days < 7
                is_very_recent = (timezone.now() - todo.created_at).total_seconds() < 24 * 3600
                title_words = len(todo.title.split())
                title_length = len(todo.title)
                word_count_total += title_words
                
                # Más cálculos innecesarios para simular carga
                has_numbers = any(char.isdigit() for char in todo.title)
                has_special = any(char in "!@#$%^&*()" for char in todo.title)
                
                todos.append({
                    'id': todo.id,
                    'title': todo.title,
                    'done': todo.done,
                    'created_at': todo.created_at.timestamp(),
                    'timestamp': todo.created_at.timestamp(),
                    'is_recent': is_recent,
                    'is_very_recent': is_very_recent,
                    'title_words': title_words,
                    'title_length': title_length,
                    'has_numbers': has_numbers,
                    'has_special_chars': has_special
                })
            
            # 8. Más cálculos estadísticos COSTOSOS
            if total_todos > 0:
                avg_title_length = word_count_total / total_todos
                completion_rate = (completed_todos / total_todos) * 100
                recent_completion_rate = (recent_completed / week_todos * 100) if week_todos > 0 else 0
            else:
                completion_rate = 0
                recent_completion_rate = 0
            
            # 9. Estadísticas adicionales PESADAS
            title_stats = {
                'avg_words': round(avg_title_length, 2),
                'total_characters': sum(len(t['title']) for t in todos),
                'avg_length': round(sum(len(t['title']) for t in todos) / len(todos), 2) if todos else 0,
                'with_numbers': sum(1 for t in todos if t['has_numbers']),
                'with_special': sum(1 for t in todos if t['has_special_chars'])
            }
            
            # Preparar respuesta con estadísticas SÚPER EXTENDIDAS
            todos_data = {
                'todos': todos,
                'stats': {
                    'total': total_todos,
                    'completed': completed_todos,
                    'pending': pending_todos,
                    'completion_rate': round(completion_rate, 1),
                    'recent_completion_rate': round(recent_completion_rate, 1),
                    'today_created': today_todos,
                    'week_created': week_todos,
                    'month_created': month_todos,
                    'year_created': year_todos,
                    'recent_completed': recent_completed,
                    'urgent_count': urgent_todos,
                    'important_count': important_todos,
                    'critical_count': critical_todos
                },
                'daily_stats': daily_stats,
                'title_analytics': title_stats,
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'from_cache': False
            }
            
            end_time = time.time()
            load_time = round((end_time - start_time) * 1000)  # En milisegundos
            todos_data['load_time'] = load_time
            
            # Guardar en caché por 30 segundos (Redis solo como caché)
            try:
                # Convertir timestamps a strings para JSON
                todos_data_for_cache = todos_data.copy()
                for todo in todos_data_for_cache['todos']:
                    todo['created_at'] = str(todo['created_at'])
                    todo['timestamp'] = str(todo['timestamp'])
                r.setex(cache_key, 30, json.dumps(todos_data_for_cache))
            except:
                pass  # Si Redis falla, no importa para el funcionamiento principal
            
            return Response(todos_data)
            
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        """Limpiar caché de datos de tareas"""
        try:
            r = get_redis()
            r.delete("todos_data_cache")
            return Response({"detail": "Caché de tareas limpiado"})
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class RedisAdminView(APIView):
    """Endpoint de administración para ver y gestionar Redis"""
    
    def get(self, request):
        """Ver información completa de Redis"""
        try:
            r = get_redis()
            
            # Obtener todas las keys
            all_keys = r.keys("*")
            
            # Información general
            info = {
                "redis_info": {
                    "total_keys": len(all_keys),
                    "memory_usage": r.info().get('used_memory_human', 'N/A'),
                    "connected_clients": r.info().get('connected_clients', 'N/A'),
                    "uptime": r.info().get('uptime_in_seconds', 'N/A'),
                },
                "keys_details": []
            }
            
            # Detalles de cada key
            for key in all_keys:
                try:
                    key_type = r.type(key)
                    ttl = r.ttl(key)
                    
                    key_info = {
                        "key": key,
                        "type": key_type,
                        "ttl": ttl if ttl > 0 else "No expira"
                    }
                    
                    # Obtener valor según el tipo
                    if key_type == "string":
                        try:
                            # Intentar decodificar como JSON
                            value = r.get(key)
                            try:
                                key_info["value"] = json.loads(value)
                                key_info["display"] = "JSON"
                            except:
                                key_info["value"] = value
                                key_info["display"] = "String"
                        except:
                            key_info["value"] = "Error leyendo valor"
                            
                    elif key_type == "hash":
                        key_info["value"] = r.hgetall(key)
                        key_info["display"] = "Hash"
                        
                    elif key_type == "zset":
                        # Para sorted sets, mostrar elementos con scores
                        zset_data = r.zrange(key, 0, -1, withscores=True)
                        key_info["value"] = [{"member": member, "score": score} for member, score in zset_data]
                        key_info["display"] = "Sorted Set"
                        
                    elif key_type == "list":
                        key_info["value"] = r.lrange(key, 0, -1)
                        key_info["display"] = "List"
                        
                    elif key_type == "set":
                        key_info["value"] = list(r.smembers(key))
                        key_info["display"] = "Set"
                    
                    info["keys_details"].append(key_info)
                    
                except Exception as e:
                    info["keys_details"].append({
                        "key": key,
                        "error": f"Error leyendo key: {str(e)}"
                    })
            
            return Response(info)
            
        except Exception as e:
            return Response(
                {"detail": f"Error conectando a Redis: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        """Limpiar keys específicas o todas"""
        try:
            r = get_redis()
            key_pattern = request.GET.get('pattern', '*')
            
            if key_pattern == "FLUSH_ALL":
                # Limpiar toda la base de datos
                r.flushdb()
                return Response({"detail": "Toda la base de datos Redis ha sido limpiada"})
            else:
                # Limpiar keys específicas
                keys_to_delete = r.keys(key_pattern)
                if keys_to_delete:
                    deleted_count = r.delete(*keys_to_delete)
                    return Response({
                        "detail": f"Eliminadas {deleted_count} keys con patrón '{key_pattern}'"
                    })
                else:
                    return Response({
                        "detail": f"No se encontraron keys con patrón '{key_pattern}'"
                    })
                    
        except Exception as e:
            return Response(
                {"detail": f"Error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
