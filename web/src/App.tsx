import React, { useEffect, useState } from "react";

type Todo = {
  id: number;
  title: string;
  done: boolean;
  created_at: number;
};

const api = {
  async list(): Promise<Todo[]> {
    const res = await fetch("/api/todos");
    if (!res.ok) throw new Error("Error listando tareas");
    return res.json();
  },
  async add(title: string): Promise<Todo> {
    const res = await fetch("/api/todos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    if (!res.ok) throw new Error("Error creando tarea");
    return res.json();
  },
  async toggle(id: number, done: boolean): Promise<Todo> {
    const res = await fetch(`/api/todos/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ done }),
    });
    if (!res.ok) throw new Error("Error actualizando tarea");
    return res.json();
  },
  async remove(id: number): Promise<void> {
    const res = await fetch(`/api/todos/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Error eliminando tarea");
  },
};

export default function App() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setErr(null);
    try {
      const data = await api.list();
      setTodos(data);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    try {
      const created = await api.add(text.trim());
      setTodos((t) => [...t, created]);
      setText("");
    } catch (e: any) {
      setErr(e.message);
    }
  };

  const onToggle = async (todo: Todo) => {
    try {
      const updated = await api.toggle(todo.id, !todo.done);
      setTodos((t) => t.map((x) => (x.id === todo.id ? updated : x)));
    } catch (e: any) {
      setErr(e.message);
    }
  };

  const onDelete = async (todo: Todo) => {
    try {
      await api.remove(todo.id);
      setTodos((t) => t.filter((x) => x.id !== todo.id));
    } catch (e: any) {
      setErr(e.message);
    }
  };

  return (
    <div
      style={{
        maxWidth: 640,
        margin: "40px auto",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1>ToDo + Redis</h1>

      <form
        onSubmit={onAdd}
        style={{ display: "flex", gap: 8, marginBottom: 16 }}
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Nueva tarea..."
          style={{ flex: 1, padding: 8, fontSize: 16 }}
        />
        <button type="submit" style={{ padding: "8px 12px", fontSize: 16 }}>
          Agregar
        </button>
      </form>

      {err && (
        <div
          style={{
            background: "#fee",
            border: "1px solid #f88",
            padding: 8,
            marginBottom: 12,
          }}
        >
          {err}
        </div>
      )}

      {loading ? (
        <p>Cargando…</p>
      ) : todos.length === 0 ? (
        <p>Sin tareas aún.</p>
      ) : (
        <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: 8 }}>
          {todos.map((todo) => (
            <li
              key={todo.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: 8,
                padding: 12,
                display: "flex",
                alignItems: "center",
                gap: 12,
              }}
            >
              <input
                type="checkbox"
                checked={todo.done}
                onChange={() => onToggle(todo)}
              />
              <div
                style={{
                  flex: 1,
                  textDecoration: todo.done ? "line-through" : "none",
                }}
              >
                {todo.title}
              </div>
              <button
                onClick={() => onDelete(todo)}
                style={{ padding: "6px 10px" }}
              >
                ❌
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
