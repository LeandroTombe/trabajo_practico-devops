# 📝 Todo App con Redis - Trabajo Práctico DevOps

Una aplicación web completa de gestión de tareas (Todo List) construida con **Django REST Framework**, **React TypeScript** y **Redis**, desplegada usando **Docker Compose**. Este proyecto demuestra prácticas modernas de DevOps y desarrollo full-stack.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │    │   Backend       │    │   Database      │
│   (React TS)    │◄──►│   (Django API)  │◄──►│   (Redis)       │
│   Puerto: 8080  │    │   Puerto: 8000  │    │   Puerto: 6379  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componentes:

- **Frontend**: Aplicación React con TypeScript servida por Nginx
- **Backend**: API REST desarrollada con Django REST Framework
- **Base de Datos**: Redis para almacenamiento rápido de datos
- **Orquestación**: Docker Compose para gestión de contenedores

## ✨ Características

- ✅ **CRUD completo** de tareas (Crear, Leer, Actualizar, Eliminar)
- ✅ **Interfaz moderna** y responsive con React + TypeScript
- ✅ **API REST** documentada y escalable
- ✅ **Base de datos en memoria** Redis para alta performance
- ✅ **Arquitectura containerizada** con Docker
- ✅ **Configuración de desarrollo** lista para usar
- ✅ **Manejo de estados** y errores en el frontend

## 🚀 Inicio Rápido

### Prerrequisitos

Asegúrate de tener instalado:
- [Docker](https://www.docker.com/get-started) (versión 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (versión 2.0+)

### Instalación y Ejecución

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/MirandaAriano/tp-redis-devops.git
   cd tp-redis-devops
   ```

2. **Inicia todos los servicios**
   ```bash
   docker-compose up --build
   ```
   
   Este comando:
   - Construye las imágenes Docker
   - Inicia Redis, la API de Django y el frontend de React
   - Configura la red entre contenedores

3. **Accede a la aplicación**
   - **Frontend**: http://localhost:8080
   - **API Backend**: http://localhost:8000
   - **Redis**: localhost:6379

### Modo Desarrollo (Detached)

Para ejecutar en segundo plano:
```bash
docker-compose up -d --build
```

Para ver los logs:
```bash
docker-compose logs -f
```

Para detener los servicios:
```bash
docker-compose down
```

## 📁 Estructura del Proyecto

```
tp-redis-devops/
├── 📄 docker-compose.yml          # Orquestación de servicios
├── 📄 README.md                   # Este archivo
├── 📁 api/                        # Backend Django
│   ├── 📄 Dockerfile              # Imagen del backend
│   ├── 📄 requirements.txt        # Dependencias Python
│   ├── 📄 manage.py               # CLI de Django
│   ├── 📁 api_project/            # Configuración principal
│   └── 📁 todos/                  # App de tareas
│       └── 📄 views.py            # Lógica de la API
└── 📁 web/                        # Frontend React
    ├── 📄 Dockerfile              # Imagen del frontend
    ├── 📄 package.json            # Dependencias Node.js
    ├── 📄 tsconfig.json           # Configuración TypeScript
    ├── 📄 index.html              # Archivo HTML base
    ├── 📁 nginx/                  # Configuración del servidor web
    └── 📁 src/                    # Código fuente React
        ├── 📄 main.tsx            # Punto de entrada
        └── 📄 App.tsx             # Componente principal
```

## 🔧 Configuración Técnica

### Variables de Entorno

El proyecto utiliza las siguientes variables de entorno (configuradas en `docker-compose.yml`):

| Variable | Valor por Defecto | Descripción |
|----------|-------------------|-------------|
| `REDIS_HOST` | `redis` | Host del servidor Redis |
| `REDIS_PORT` | `6379` | Puerto de Redis |
| `REDIS_DB` | `0` | Base de datos Redis |
| `DJANGO_SECRET_KEY` | `dev-secret-key-change-me` | Clave secreta de Django |
| `DJANGO_DEBUG` | `1` | Modo debug de Django |

### Puertos Utilizados

| Servicio | Puerto Host | Puerto Contenedor | Descripción |
|----------|-------------|-------------------|-------------|
| Frontend | 8080 | 80 | Aplicación web React |
| Backend API | 8000 | 8000 | API REST Django |
| Redis | 6379 | 6379 | Base de datos Redis |

## 🛠️ Desarrollo Local

### Ejecutar el Backend solamente

```bash
cd api
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000
```

### Ejecutar el Frontend solamente

```bash
cd web
npm install
npm run build
# Servir con cualquier servidor web estático
```

### Ejecutar Redis solamente

```bash
docker run --name redis -p 6379:6379 -d redis:7-alpine
```

## 📚 API Endpoints

La API REST proporciona los siguientes endpoints:

| Método | Endpoint | Descripción | Ejemplo de Payload |
|--------|----------|-------------|-------------------|
| `GET` | `/api/todos` | Lista todas las tareas | - |
| `POST` | `/api/todos` | Crea una nueva tarea | `{"title": "Nueva tarea"}` |
| `PATCH` | `/api/todos/:id` | Actualiza una tarea | `{"done": true}` |
| `DELETE` | `/api/todos/:id` | Elimina una tarea | - |

### Ejemplo de Respuesta

```json
{
  "id": 1,
  "title": "Aprender Docker",
  "done": false,
  "created_at": 1694198400
}
```

## 🧪 Testing

### Probar la API con curl

```bash
# Listar tareas
curl http://localhost:8000/api/todos

# Crear tarea
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Tarea de prueba"}'

# Marcar como completada
curl -X PATCH http://localhost:8000/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'

# Eliminar tarea
curl -X DELETE http://localhost:8000/api/todos/1
```

## 🐛 Troubleshooting

### Problemas Comunes

1. **Puerto ya en uso**
   ```bash
   # Cambiar puertos en docker-compose.yml
   # O detener servicios que usen los puertos 8000, 8080, 6379
   ```

2. **Contenedores no se comunican**
   ```bash
   # Verificar que todos los servicios estén corriendo
   docker-compose ps
   
   # Revisar logs
   docker-compose logs api
   docker-compose logs web
   docker-compose logs redis
   ```

3. **Datos de Redis se pierden**
   ```bash
   # Redis usa almacenamiento en memoria por defecto
   # Para persistencia, añadir volúmenes en docker-compose.yml
   ```

### Comandos Útiles

```bash
# Reconstruir imágenes
docker-compose build --no-cache

# Acceder al contenedor de la API
docker-compose exec api bash

# Ver logs en tiempo real
docker-compose logs -f api

# Limpiar volúmenes y contenedores
docker-compose down -v
docker system prune -a
```
