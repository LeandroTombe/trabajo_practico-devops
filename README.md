# 📝 Todo App con Arquitectura Moderna - Trabajo Práctico DevOps

Una aplicación web completa de gestión de tareas (Todo List) con **arquitectura profesional** que combina **PostgreSQL** como base de datos principal y **Redis** como sistema de caché. Construida con **Django REST Framework**, **React TypeScript** y desplegada usando **Docker Compose**

## 🏗️ Arquitectura del Sistema (Actualizada)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django API    │    │     Redis       │    │   SqlLite    │
│   (React TS)    │◄──►│   (Cache Layer) │◄──►│    (Cache)      │    │  (Database)     │
│   Puerto: 8081  │    │   Puerto: 8000  │    │   Puerto: 6379  │    │   Puerto: 5432  │
│   Nginx Server  │    │   REST + ORM    │    │   Session Store │    │   Persistence   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔧 Componentes Principales:

- **🌐 Frontend**: React con TypeScript y Vite, servido por Nginx optimizado
- **⚡ Backend**: Django REST Framework con ORM y sistema de caché inteligente
- **💾 Base de Datos**: PostgreSQL 15 para persistencia confiable y transacciones ACID

### 🌍 Configuración Dual

#### **Desarrollo Local** (Docker Compose):
- **Frontend**: Nginx proxy → `http://api:8000` (contenedor local)
- **Variables**: `API_URL=http://api:8000`

#### **Producción** (Render):
- **Frontend**: Nginx proxy → `https://tp-redis-api.onrender.com`
- **Variables**: `API_URL=https://tp-redis-api.onrender.com`


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



3. **Inicia el proyecto**
   ```bash
   # Usando el script de gestión (recomendado)
   ./scripts/manage.sh start
   
   # O directamente con Docker Compose
   docker-compose up -d
   ```

4. **Accede a la aplicación**
   - **Frontend**: http://localhost:8081 (desarrollo
   - **API**: http://localhost:8000
   - **Base de datos**: PostgreSQL puerto 5432
   - **Cache**: Redis puerto 6379
   - **Health Check**: http://localhost:8000/api/health/ (verificar conexiones)


### Docker Compose Directo
```bash
# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reconstruir e iniciar
docker-compose up --build -d
```

## 📁 Estructura del Proyecto

```
tp-redis-devops/
├── 📄 docker-compose.yml          # Orquestación de servicios
├── 📄 .env.example               # Plantilla de variables de entorno
├── 📄 render.yaml                # Configuración para despliegue en Render
├── 📄 .gitignore                 # Archivos ignorados por Git
├── 📁 api/                       # Backend Django
│   ├── 📄 Dockerfile             # Imagen del API
│   ├── 📄 requirements.txt       # Dependencias Python
│   ├── 📄 manage.py              # Script de gestión Django
│   ├── 📁 api_project/           # Configuración principal
│   └── 📁 todos/                 # Aplicación de tareas
├── 📁 web/                       # Frontend React
│   ├── 📄 Dockerfile             # Imagen del frontend
│   ├── 📄 package.json           # Dependencias Node.js
│   ├── 📄 tsconfig.json          # Configuración TypeScript
│   ├── 📁 src/                   # Código fuente React
│   └── 📁 nginx/                 # Configuración Nginx con templates
├── 📁 scripts/                   # Scripts de automatización
│   └── 📄 manage.sh              # Script principal de gestión
└── 📁 .github/workflows/         # CI/CD con GitHub Actions
    └── 📄 ci-cd.yml              # Pipeline automatizado
```

## 🐳 Servicios Docker

### Base de Datos PostgreSQL
- **Puerto**: 5432
- **Versión**: PostgreSQL 15-alpine
- **Uso**: Almacenamiento principal de datos con persistencia
- **Volumen**: `postgres_data` para persistencia entre reinicios
- **Configuración**: Usuario y base de datos configurables via .env

### Cache Redis
- **Puerto**: 6379
- **Versión**: Redis 7-alpine
- **Uso**: Cache inteligente de API responses y sesiones
- **TTL**: 900 segundos (15 minutos) para cache de endpoints
- **Configuración**: Optimizado para cache con invalidación automática

### Frontend Nginx
- **Puerto**: 8081 (desarrollo), 80 (producción)
- **Configuración**: Templates dinámicos con variables de entorno
- **Proxy**: Configuración dual para desarrollo local vs producción
- **Template**: `default.conf.template` → `default.conf` procesado automáticamente

### API Backend (Django)
- **Puerto**: 8000
- **Framework**: Django REST Framework con ORM
- **Base de datos**: PostgreSQL (principal) + Redis (cache)
- **Imagen**: `mirandaariano/tp-redis-devops-api:latest`
- **Características**: 
  - Cache inteligente con invalidación automática
  - Health check endpoint para monitoreo
  - Migraciones automáticas de base de datos

### Frontend (React)
- **Puerto**: 8081 (desarrollo) / 80 (producción)
- **Framework**: React con TypeScript
- **Build**: Vite
- **Servidor**: Nginx
- **Imagen**: `mirandaariano/tp-redis-devops-web:latest`

## 🔄 CI/CD Pipeline

El proyecto incluye un pipeline automatizado de CI/CD con GitHub Actions:

- **Triggers**: Push a `main` y Pull Requests
- **Build**: Construcción automática de imágenes Docker
- **Tests**: Validación de código y dependencias
- **Deploy**: Publicación automática a Docker Hub


## 🧪 API Endpoints

La API REST ofrece los siguientes endpoints con cache inteligente:

### Tareas (Todos)
```http
GET    /api/todos/          # Listar todas las tareas (con cache Redis)
POST   /api/todos/          # Crear nueva tarea (invalida cache)
GET    /api/todos/{id}/     # Obtener tarea específica (con cache)
PUT    /api/todos/{id}/     # Actualizar tarea (invalida cache)
DELETE /api/todos/{id}/     # Eliminar tarea (invalida cache)
```

### Sistema y Monitoreo
```http
GET    /api/health/         # Health check de Sqllite y Redis
```

### Ejemplo de respuesta:
```json
{
  "id": 1,
  "title": "Completar documentación",
  "description": "Escribir README completo",
  "completed": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Ejemplo Health Check:
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🛠️ Desarrollo

### Estructura del Frontend (React)
- `src/App.tsx`: Componente principal con gestión de estado
- `src/main.tsx`: Punto de entrada
- Configuración con Vite para hot reload

### Estructura del Backend (Django)
- `api_project/`: Configuración principal del proyecto
  - `settings.py`: Configuración de PostgreSQL y Redis cache
  - `urls.py`: Routing principal de la API
- `todos/`: Aplicación de gestión de tareas
  - `models.py`: Modelo Django para PostgreSQL
  - `views.py`: API views con cache inteligente
- `requirements.txt`: Dependencias Python incluyendo psycopg2 y django-redis

### Arquitectura de Cache
El sistema implementa un cache inteligente de dos niveles:

1. **PostgreSQL (Persistencia)**: Almacena todos los datos de forma permanente
2. **Redis (Cache)**: Cache temporal de 15 minutos para mejorar performance

**Invalidación automática**: Cualquier operación de escritura (POST/PUT/DELETE) invalida el cache automáticamente.

### Variables de Entorno

El proyecto utiliza un sistema de configuración dual que se adapta automáticamente al entorno:

**Desarrollo Local** (Docker Compose):
```bash
# Configuración para contenedores locales
DATABASE_URL=postgresql://user:password@postgres:5432/todos
REDIS_URL=redis://redis:6379/0
API_URL=http://api:8000  # Apunta al contenedor interno
```

**Producción** (Render):
```bash
# Configuración para servicios externos
DATABASE_URL=postgresql://usuario:password@host-externo:5432/database
REDIS_URL=redis://host-redis-externo:6379/0
API_URL=https://tp-redis-api.onrender.com  # URL pública del API
```

**Sistema de Templates Nginx**:
- El archivo `default.conf.template` usa `${API_URL}` como variable
- Nginx procesa automáticamente el template según el entorno
- Elimina conflictos entre desarrollo local y producción

📖 **Archivo de referencia**: Ver `.env.example` para configuración completa

## 🚀 Despliegue

### Desarrollo Local
```bash
# Con imágenes locales y base de datos completa
docker-compose up -d

# Verificar que todos los servicios estén funcionando
docker-compose ps
curl http://localhost:8000/api/health/
```


# Verificar despliegue
curl http://localhost:8000/api/health/
```

### Monitoreo
```bash
# Ver estado de servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs específicos de un servicio
docker-compose logs -f api        # Backend Django
docker-compose logs -f database   # PostgreSQL
docker-compose logs -f cache      # Redis

# Health check de la aplicación
curl http://localhost:8000/api/health/

# Verificar conexión a PostgreSQL
docker exec -it tp-redis-devops-database-1 psql -U admin -d todos_db -c "\dt"

# Verificar cache Redis
docker exec -it tp-redis-devops-cache-1 redis-cli KEYS "*"

# Ver salud de contenedores
docker inspect --format='{{json .State.Health}}' <container_name>
```


### Problemas Comunes

1. **Puerto en uso**
   ```bash
   # Cambiar puertos en .env
   API_PORT=8001
   WEB_PORT=8082
   DATABASE_PORT=5433
   REDIS_PORT=6380
   ```

2. **Error de conexión PostgreSQL**
   ```bash
   # Verificar estado del contenedor
   docker-compose ps database
   docker-compose logs database
   
   # Verificar conexión desde el API
   curl http://localhost:8000/api/health/
   ```

3. **Error de cache Redis**
   ```bash
   # Verificar estado del contenedor
   docker-compose ps cache
   docker-compose logs cache
   
   # Limpiar cache manualmente
   docker exec -it tp-redis-devops-cache-1 redis-cli FLUSHALL
   ```

4. **Problemas de migración de base de datos**
   ```bash
   # Ejecutar migraciones manualmente
   docker exec -it tp-redis-devops-api-1 python manage.py migrate
   
   # Ver estado de migraciones
   docker exec -it tp-redis-devops-api-1 python manage.py showmigrations
   ```

5. **Reconstruir desde cero**
   ```bash
   ./scripts/manage.sh clean
   docker-compose down -v  # Elimina también los volúmenes
   docker-compose up --build -d
   ```

6. **Verificar volúmenes de datos**
   ```bash
   # Listar volúmenes
   docker volume ls | grep tp-redis-devops
   
   # Inspeccionar volumen de PostgreSQL
   docker volume inspect tp-redis-devops_postgres_data
   ```

## 📚 Recursos Adicionales

- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)
- [Django-Redis Cache](https://github.com/jazzband/django-redis)
- [React TypeScript](https://react-typescript-cheatsheet.netlify.app/)
- [Docker Compose](https://docs.docker.com/compose/)




### Verificar que todo funciona correctamente

```bash
# 1. Iniciar todos los servicios
docker-compose up -d

# 2. Verificar que todos los contenedores están corriendo
docker-compose ps

# 3. Verificar salud del sistema
curl http://localhost:8000/api/health/

# 4. Crear una tarea de prueba
curl -X POST http://localhost:8000/api/todos/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Tarea de prueba", "description": "Verificar que la API funciona"}'

# 5. Listar todas las tareas (debería venir del cache después de la primera consulta)
curl http://localhost:8000/api/todos/
```

### Comandos útiles para desarrollo

```bash
# Ver logs de todos los servicios en tiempo real
docker-compose logs -f

# Acceder a la base de datos PostgreSQL
docker exec -it tp-redis-devops-database-1 psql -U admin -d todos_db

# Acceder al CLI de Redis
docker exec -it tp-redis-devops-cache-1 redis-cli

# Ejecutar comandos Django (migraciones, shell, etc.)
docker exec -it tp-redis-devops-api-1 python manage.py shell

# Verificar migraciones
docker exec -it tp-redis-devops-api-1 python manage.py showmigrations

# Crear superusuario de Django
docker exec -it tp-redis-devops-api-1 python manage.py createsuperuser
```

### Performance y Cache

```bash
# Ver qué está en el cache de Redis
docker exec -it tp-redis-devops-cache-1 redis-cli KEYS "*"

# Limpiar todo el cache
docker exec -it tp-redis-devops-cache-1 redis-cli FLUSHALL

# Ver información del cache Redis
docker exec -it tp-redis-devops-cache-1 redis-cli INFO memory

# Ver estadísticas de PostgreSQL
docker exec -it tp-redis-devops-database-1 psql -U admin -d todos_db -c "SELECT * FROM pg_stat_activity;"
```
