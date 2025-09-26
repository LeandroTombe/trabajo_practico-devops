from django.urls import path
from todos.views import HealthView, TodoList, TodoDetail, DataView

urlpatterns = [
    path("api/health", HealthView.as_view(), name="health"),
    path("api/todos", TodoList.as_view(), name="todo-list"),
    path("api/todos/<int:todo_id>", TodoDetail.as_view(), name="todo-detail"),
    path("api/data", DataView.as_view(), name="data"),
]
