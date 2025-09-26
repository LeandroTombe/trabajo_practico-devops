import os
import time
import random
import json
import redis
from typing import Dict, Any, List

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from redis import Redis
from urllib.parse import urlparse


def get_redis() -> Redis:
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        # Para Render/producción - usa REDIS_URL
        return Redis.from_url(redis_url, decode_responses=True)
    else:
        # Para desarrollo local
        return Redis(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", "6379")),
            db=int(os.environ.get("REDIS_DB", "0")),
            decode_responses=True,
        )

# Convención de claves:
#   todo:next_id   -> INCR para nuevo ID
#   todo:ids       -> ZSET (score=timestamp) con IDs
#   todo:{id}      -> HASH con fields: title, done ("0"/"1"), created_at (epoch)

def serialize_todo(r: Redis, todo_id: int) -> Dict[str, Any]:
    data = r.hgetall(f"todo:{todo_id}")
    if not data:
        return {}
    return {
        "id": todo_id,
        "title": data.get("title", ""),
        "done": data.get("done", "0") == "1",
        "created_at": float(data.get("created_at", "0.0")),
    }

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
    def get(self, request):
        r = get_redis()
        ids = r.zrange("todo:ids", 0, -1)  # asc por timestamp
        todos: List[Dict[str, Any]] = []
        for sid in ids:
            t = serialize_todo(r, int(sid))
            if t:
                todos.append(t)
        return Response(todos, status=status.HTTP_200_OK)

    def post(self, request):
        r = get_redis()
        title = (request.data or {}).get("title")
        if not title or not isinstance(title, str):
            return Response({"detail": "title (string) es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        new_id = r.incr("todo:next_id")
        now = time.time()
        pipe = r.pipeline()
        pipe.hset(f"todo:{new_id}", mapping={
            "title": title.strip(),
            "done": "0",
            "created_at": str(now),
        })
        pipe.zadd("todo:ids", {new_id: now})
        pipe.execute()

        return Response(serialize_todo(r, new_id), status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name="dispatch")
class TodoDetail(APIView):
    def patch(self, request, todo_id: int):
        r = get_redis()
        key = f"todo:{todo_id}"
        if not r.exists(key):
            return Response({"detail": "No existe."}, status=status.HTTP_404_NOT_FOUND)

        payload = request.data or {}
        updates = {}

        if "title" in payload:
            title = payload.get("title")
            if not isinstance(title, str):
                return Response({"detail": "title debe ser string."}, status=status.HTTP_400_BAD_REQUEST)
            updates["title"] = title.strip()

        if "done" in payload:
            done = payload.get("done")
            if not isinstance(done, bool):
                return Response({"detail": "done debe ser booleano."}, status=status.HTTP_400_BAD_REQUEST)
            updates["done"] = "1" if done else "0"

        if not updates:
            return Response({"detail": "Nada para actualizar."}, status=status.HTTP_400_BAD_REQUEST)

        r.hset(key, mapping=updates)
        return Response(serialize_todo(r, todo_id), status=status.HTTP_200_OK)

    def delete(self, request, todo_id: int):
        r = get_redis()
        key = f"todo:{todo_id}"
        if not r.exists(key):
            return Response({"detail": "No existe."}, status=status.HTTP_404_NOT_FOUND)

        pipe = r.pipeline()
        pipe.delete(key)
        pipe.zrem("todo:ids", todo_id)
        pipe.execute()

        return Response(status=status.HTTP_204_NO_CONTENT)


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
            
            # Cargar datos reales (sin caché) - tiempo real de consulta
            start_time = time.time()
            
            # Obtener todas las tareas reales desde Redis
            todo_ids = r.zrange("todo:ids", 0, -1, withscores=True)
            todos = []
            
            for todo_id_bytes, timestamp in todo_ids:
                todo_id = int(todo_id_bytes)
                key = f"todo:{todo_id}"
                todo_data = r.hgetall(key)
                if todo_data:
                    created_at_str = todo_data.get('created_at', '0')
                    try:
                        created_at = int(float(created_at_str))
                    except (ValueError, TypeError):
                        created_at = 0
                    
                    done_value = todo_data.get('done', 'false').lower()
                    is_done = done_value in ['true', '1']
                    
                    todos.append({
                        'id': todo_id,
                        'title': todo_data.get('title', ''),
                        'done': is_done,
                        'created_at': created_at,
                        'timestamp': timestamp
                    })
            
            # Crear estadísticas de las tareas
            total_todos = len(todos)
            completed_todos = len([t for t in todos if t['done']])
            pending_todos = total_todos - completed_todos
            
            # Preparar respuesta con datos reales
            todos_data = {
                'todos': todos,
                'stats': {
                    'total': total_todos,
                    'completed': completed_todos,
                    'pending': pending_todos,
                    'completion_rate': round((completed_todos / total_todos * 100) if total_todos > 0 else 0, 1)
                },
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'from_cache': False
            }
            
            end_time = time.time()
            load_time = round((end_time - start_time) * 1000)  # En milisegundos
            todos_data['load_time'] = load_time
            
            # Guardar en caché por 30 segundos (menos tiempo para ver mejor el efecto)
            r.setex(cache_key, 30, json.dumps(todos_data))
            
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
