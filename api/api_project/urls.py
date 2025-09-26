from django.urls import path
from todos.views import HealthView, TodoList, TodoDetail

urlpatterns = [
    path("api/health", HealthView.as_view(), name="health"),
    path("api/todos", TodoList.as_view(), name="todo-list"),
    path("api/todos/<int:todo_id>", TodoDetail.as_view(), name="todo-detail"),
]
