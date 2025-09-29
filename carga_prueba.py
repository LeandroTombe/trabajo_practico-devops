#!/usr/bin/env python3
"""
Script para cargar datos de prueba masivos en la base de datos
Ejecutar con: python carga_prueba.py
"""

import requests
import json
import random
import time
import concurrent.futures
import threading
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api"

def create_single_todo(data):
    """Crear una sola tarea - función para threading"""
    index, title, done = data
    try:
        response = requests.post(
            f"{API_BASE}/todos/",
            json={"title": title, "done": done},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.status_code == 201
    except:
        return False

def create_massive_todos(count=1000):
    """Crear muchas tareas SUPER RAPIDO usando threading paralelo"""
    
    # Listas de palabras para generar títulos variados
    adjectives = [
        "Urgente", "Importante", "Critico", "Opcional", "Rutinario", 
        "Complejo", "Simple", "Avanzado", "Basico", "Especial",
        "Temporal", "Permanente", "Prioritario", "Secundario", "Principal"
    ]
    
    nouns = [
        "tarea", "proyecto", "reporte", "analisis", "documento", 
        "presentacion", "reunion", "revision", "evaluacion", "implementacion",
        "diseno", "desarrollo", "testing", "deployment", "investigacion",
        "planificacion", "optimizacion", "refactoring", "migracion", "backup"
    ]
    
    actions = [
        "crear", "actualizar", "revisar", "completar", "validar",
        "procesar", "analizar", "optimizar", "corregir", "mejorar",
        "implementar", "disenar", "configurar", "instalar", "migrar"
    ]
    
    print(f"Creando {count:,} tareas SUPER RAPIDO con threading paralelo...")
    
    # Preparar todos los datos de antemano
    print("Preparando datos...")
    tasks_data = []
    for i in range(count):
        adj = random.choice(adjectives)
        action = random.choice(actions)
        noun = random.choice(nouns)
        title = f"{adj} {action} {noun} #{i+1}"
        done = random.random() < 0.3  # 30% completadas
        tasks_data.append((i, title, done))
    
    print(f"Iniciando {count:,} requests en paralelo...")
    start_time = time.time()
    
    created = 0
    errors = 0
    
    # Usar ThreadPoolExecutor para máxima velocidad
    max_workers = min(30, count)  # Hasta 30 threads paralelos
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Enviar todas las tareas
        future_to_index = {executor.submit(create_single_todo, data): i for i, data in enumerate(tasks_data)}
        
        # Procesar resultados conforme van llegando
        for future in concurrent.futures.as_completed(future_to_index):
            if future.result():
                created += 1
            else:
                errors += 1
            
            # Mostrar progreso cada 500 tareas
            if (created + errors) % 500 == 0:
                elapsed = time.time() - start_time
                rate = (created + errors) / elapsed if elapsed > 0 else 0
                remaining = count - (created + errors)
                eta = remaining / rate if rate > 0 else 0
                print(f"  Procesadas {created + errors:,}/{count:,} tareas... "
                      f"Rate: {rate:.1f}/s, ETA: {eta:.1f}s")
    
    elapsed_time = time.time() - start_time
    rate = created / elapsed_time if elapsed_time > 0 else 0
    
    print(f"\nRESULTADO SUPER RAPIDO:")
    print(f"  Tareas creadas: {created:,}")
    print(f"  Errores: {errors:,}")
    print(f"  Tiempo total: {elapsed_time:.2f}s")
    print(f"  Rate promedio: {rate:.1f} tareas/segundo")

def delete_single_todo(todo_id):
    """Eliminar una sola tarea - función para threading"""
    try:
        response = requests.delete(f"{API_BASE}/todos/{todo_id}/")
        return response.status_code == 204
    except:
        return False

def delete_all_todos_fast():
    """Eliminar TODAS las tareas """
    
    print("ELIMINANDO TODAS LAS TAREAS...")
    
    try:
        # Primero obtener todas las tareas existentes
        response = requests.get(f"{API_BASE}/todos/")
        if response.status_code != 200:
            print(f"Error obteniendo tareas: {response.status_code}")
            return
        
        todos = response.json()
        total_todos = len(todos)
        
        if total_todos == 0:
            print("No hay tareas para eliminar")
            return
        
        print(f"Encontradas {total_todos:,} tareas para eliminar...")
    
        
        # Preparar IDs de tareas
        todo_ids = [todo['id'] for todo in todos]
        
        start_time = time.time()
        deleted = 0
        errors = 0
        
        # Usar ThreadPoolExecutor para máxima velocidad de eliminación
        max_workers = min(40, total_todos)  # Hasta 40 threads paralelos
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar todas las eliminaciones
            future_to_id = {executor.submit(delete_single_todo, todo_id): todo_id for todo_id in todo_ids}
            
            # Procesar resultados conforme van llegando
            for future in concurrent.futures.as_completed(future_to_id):
                if future.result():
                    deleted += 1
                else:
                    errors += 1
                
                # Mostrar progreso cada 1000 eliminaciones
                if (deleted + errors) % 1000 == 0:
                    elapsed = time.time() - start_time
                    rate = (deleted + errors) / elapsed if elapsed > 0 else 0
                    remaining = total_todos - (deleted + errors)
                    eta = remaining / rate if rate > 0 else 0
                    print(f"  Eliminadas {deleted + errors:,}/{total_todos:,} tareas... "
                          f"Rate: {rate:.1f}/s, ETA: {eta:.1f}s")
        
        elapsed_time = time.time() - start_time
        rate = deleted / elapsed_time if elapsed_time > 0 else 0
        
        print(f"\nRESULTADO ELIMINACION:")
        print(f"  Tareas eliminadas: {deleted:,}")
        print(f"  Errores: {errors:,}")

        
        # Limpiar caché después de eliminar
        try:
            requests.delete(f"{API_BASE}/data/")
            print("  Cache limpiado")
        except:
            print("  No se pudo limpiar el cache")
            
    except Exception as e:
        print(f"Error eliminando tareas: {e}")

def create_massive_todos_sequential(count=1000):
    """Version secuencial RAPIDA para cantidades pequenas (100-500) - SIN pausas artificiales"""
    
    adjectives = ["Urgente", "Importante", "Critico", "Opcional", "Rutinario"]
    nouns = ["tarea", "proyecto", "reporte", "analisis", "documento"]
    actions = ["crear", "actualizar", "revisar", "completar", "validar"]
    
    print(f"Creando {count:,} tareas secuencialmente (SIN pausas)...")
    
    created = 0
    errors = 0
    start_time = time.time()
    
    for i in range(count):
        adj = random.choice(adjectives)
        action = random.choice(actions)
        noun = random.choice(nouns)
        title = f"{adj} {action} {noun} #{i+1}"
        done = random.random() < 0.3
        
        try:
            response = requests.post(
                f"{API_BASE}/todos/",
                json={"title": title, "done": done},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 201:
                created += 1
                if created % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = created / elapsed if elapsed > 0 else 0
                    print(f"  Creadas {created:,}/{count:,} tareas... Rate: {rate:.1f}/s")
            else:
                errors += 1
                
        except Exception as e:
            errors += 1
        
 
    
    elapsed_time = time.time() - start_time
    rate = created / elapsed_time if elapsed_time > 0 else 0
    
    print(f"\nResumen:")
    print(f"  Tareas creadas: {created:,}")
    print(f"  Errores: {errors:,}")
    print(f"  Tiempo total: {elapsed_time:.2f}s")
    print(f"  Rate promedio: {rate:.1f} tareas/segundo")

def test_cache_performance():
    """Probar el rendimiento con y sin cache"""
    
    print("\nINICIANDO PRUEBAS DE RENDIMIENTO...")
    
    # 1. Limpiar caché
    print("\n1. Limpiando cache...")
    try:
        response = requests.delete(f"{API_BASE}/data/")
        print(f"   Cache limpiado: {response.json()}")
    except:
        print("   Error limpiando cache")
    
    # 2. Primera carga (SIN caché)
    print("\n2. Primera carga (desde PostgreSQL)...")
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE}/data/")
        data = response.json()
        db_time = time.time() - start_time
        
        print(f"    Tiempo total: {db_time:.3f}s")
        print(f"    Total tareas: {data['stats']['total']:,}")
        print(f"    From cache: {data['from_cache']}")
        print(f"    Load time (server): {data['load_time']}ms")
        
    except Exception as e:
        print(f"    Error: {e}")
        return
    
    # 3. Segunda carga (CON caché)
    print("\n3. Segunda carga (desde Redis cache)...")
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE}/data/")
        data = response.json()
        cache_time = time.time() - start_time
        
        print(f"   Tiempo total: {cache_time:.3f}s")
        print(f"   Total tareas: {data['stats']['total']:,}")
        print(f"   From cache: {data['from_cache']}")
        print(f"   Load time (server): {data['load_time']}ms")
        
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # 4. Comparación
    print(f"\nRESULTADOS:")
    print(f"    PostgreSQL: {db_time:.3f}s")
    print(f"    Redis Cache: {cache_time:.3f}s")
    if db_time > 0 and cache_time > 0:
        improvement = ((db_time - cache_time) / db_time) * 100
        speedup = db_time / cache_time
        print(f"    Mejora: {improvement:.1f}% mas rapido")
        print(f"    Speedup: {speedup:.1f}x veces mas rapido")

if __name__ == "__main__":
    print("CARGADOR DE DATOS DE PRUEBA Y BENCHMARK DE CACHE")
    print("=" * 60)
    
    # Menú
    while True:
        print("\nOPCIONES:")
        print("1. Crear 100 tareas de prueba")
        print("2. Crear 500 tareas de prueba") 
        print("3. Crear 1000 tareas de prueba")
        print("4. Crear 5000 tareas de prueba")
        print("5. Test de rendimiento basico")
        print("6. ELIMINAR TODAS LAS TAREAS")
        print("0. Salir")
        
        choice = input("\nSelecciona una opcion: ").strip()
        
        if choice == "1":
            create_massive_todos_sequential(100)  # Secuencial para pocas
        elif choice == "2":
            create_massive_todos_sequential(500)  # Secuencial para pocas
        elif choice == "3":
            create_massive_todos(1000)  # Paralelo para muchas
        elif choice == "4":
            create_massive_todos(5000)  # Paralelo para muchas
        elif choice == "5":
            test_cache_performance()
        elif choice == "6":
            print("ADVERTENCIA: Esto eliminara TODAS las tareas de la base de datos!")
            confirm = input("Estas seguro? (y/N): ").strip().lower()
            if confirm == 'y':
                delete_all_todos_fast()  # Usar la función súper rápida
            else:
                print("Cancelado")
        elif choice == "0":
            print("Hasta luego!")
            break
        else:
            print("Opcion invalida")