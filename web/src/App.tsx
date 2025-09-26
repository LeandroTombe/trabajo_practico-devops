import React, { useEffect, useState } from "react";

type Todo = {
  id: number;
  title: string;
  done: boolean;
  created_at: number;
};

type DataItem = {
  todos: Array<{id: number, title: string, done: boolean, created_at: number, timestamp: number}>;
  stats: {
    total: number;
    completed: number;
    pending: number;
    completion_rate: number;
  };
  generated_at: string;
  from_cache: boolean;
  load_time: number;
  client_time?: number;
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
  
  // Nuevas funciones para datos
  async getData(): Promise<DataItem> {
    const start = performance.now();
    const res = await fetch("/api/data");
    if (!res.ok) throw new Error("Error obteniendo datos");
    const data = await res.json();
    const clientTime = Math.round(performance.now() - start);
    return { ...data, client_time: clientTime };
  },
  
  async clearCache(): Promise<void> {
    const res = await fetch("/api/data", { method: "DELETE" });
    if (!res.ok) throw new Error("Error limpiando caché");
  }
};

export default function App() {
  const [currentTab, setCurrentTab] = useState<'todos' | 'data'>('todos');
  const [todos, setTodos] = useState<Todo[]>([]);
  const [text, setText] = useState("");
  
  // Estados para la funcionalidad de datos
  const [data, setData] = useState<DataItem | null>(null);
  const [dataLoading, setDataLoading] = useState(false);
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
  
  // Funciones para manejar datos
  const loadData = async () => {
    setDataLoading(true);
    setErr(null);
    try {
      const result = await api.getData();
      setData(result);
    } catch (e: any) {
      setErr(e.message);
    } finally {
      setDataLoading(false);
    }
  };
  
  const clearDataCache = async () => {
    try {
      await api.clearCache();
      setData(null);
      setErr(null);
    } catch (e: any) {
      setErr(e.message);
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
      <h1>ToDo + Redis + Caché</h1>
      
      {/* Navegación por tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20, borderBottom: "1px solid #ddd" }}>
        <button
          onClick={() => setCurrentTab('todos')}
          style={{
            padding: "8px 16px",
            background: currentTab === 'todos' ? '#007acc' : 'transparent',
            color: currentTab === 'todos' ? 'white' : '#007acc',
            border: 'none',
            borderBottom: currentTab === 'todos' ? '2px solid #007acc' : '2px solid transparent',
            cursor: 'pointer'
          }}
        >
          TODOs
        </button>
        <button
          onClick={() => setCurrentTab('data')}
          style={{
            padding: "8px 16px",
            background: currentTab === 'data' ? '#007acc' : 'transparent',
            color: currentTab === 'data' ? 'white' : '#007acc',
            border: 'none',
            borderBottom: currentTab === 'data' ? '2px solid #007acc' : '2px solid transparent',
            cursor: 'pointer'
          }}
        >
          Datos (Caché)
        </button>
      </div>

      {/* Contenido condicional según la tab activa */}
      {currentTab === 'todos' && (
        <>
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
        </>
      )}
      
      {/* Tab de datos con caché */}
      {currentTab === 'data' && (
        <div>
          <div style={{ marginBottom: 16, display: "flex", gap: 8 }}>
            <button
              onClick={loadData}
              disabled={dataLoading}
              style={{
                padding: "8px 16px",
                background: "#28a745",
                color: "white",
                border: "none",
                borderRadius: 4,
                cursor: dataLoading ? "not-allowed" : "pointer"
              }}
            >
              {dataLoading ? "Cargando..." : "Cargar Datos"}
            </button>
            
            <button
              onClick={clearDataCache}
              style={{
                padding: "8px 16px",
                background: "#dc3545",
                color: "white",
                border: "none",
                borderRadius: 4,
                cursor: "pointer"
              }}
            >
              Limpiar Caché
            </button>
          </div>
          
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
          
          {data ? (
            <div>
              <div style={{
                background: data.from_cache ? "#d4edda" : "#fff3cd",
                border: `1px solid ${data.from_cache ? "#c3e6cb" : "#ffeaa7"}`,
                padding: 12,
                marginBottom: 16,
                borderRadius: 4
              }}>
                <h3 style={{ margin: "0 0 8px 0" }}>
                  {data.from_cache ? "🚀 Datos desde caché" : "⏳ Datos cargados (primera vez)"}
                </h3>
                <p style={{ margin: 0, fontSize: 14 }}>
                  <strong>Tiempo de carga:</strong> {data.load_time}ms
                  {data.client_time && ` (cliente: ${data.client_time}ms)`}
                  <br />
                  <strong>Generado:</strong> {data.generated_at}
                </p>
              </div>
              
              {/* Estadísticas de tareas */}
              <div style={{ display: "grid", gap: 16, gridTemplateColumns: "1fr 1fr", marginBottom: 20 }}>
                <div style={{ background: "#f8f9fa", padding: 16, borderRadius: 8 }}>
                  <h4 style={{ margin: "0 0 8px 0", color: "#495057" }}>📊 Estadísticas</h4>
                  <div style={{ fontSize: 14 }}>
                    <div>📝 Total: <strong>{data.stats.total}</strong></div>
                    <div>✅ Completadas: <strong>{data.stats.completed}</strong></div>
                    <div>⏳ Pendientes: <strong>{data.stats.pending}</strong></div>
                    <div>📈 Progreso: <strong>{data.stats.completion_rate}%</strong></div>
                  </div>
                </div>
                
                <div style={{ background: "#f8f9fa", padding: 16, borderRadius: 8 }}>
                  <h4 style={{ margin: "0 0 8px 0", color: "#495057" }}>⚡ Rendimiento</h4>
                  <div style={{ fontSize: 14 }}>
                    <div>🔍 Tareas consultadas: <strong>{data.todos.length}</strong></div>
                    <div>⏱️ Tiempo de consulta: <strong>{data.load_time}ms</strong></div>
                    <div>💾 Desde caché: <strong>{data.from_cache ? 'Sí' : 'No'}</strong></div>
                  </div>
                </div>
              </div>
              
              {/* Lista de tareas */}
              <div>
                <h4>� Tareas ({data.todos.length})</h4>
                {data.todos.length > 0 ? (
                  <ul style={{ listStyle: "none", padding: 0, fontSize: 14, maxHeight: 300, overflowY: "auto" }}>
                    {data.todos.map(todo => (
                      <li key={todo.id} style={{ 
                        padding: "8px 12px", 
                        borderBottom: "1px solid #eee",
                        background: todo.done ? "#d4edda" : "#fff3cd",
                        marginBottom: 4,
                        borderRadius: 4,
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center"
                      }}>
                        <span style={{
                          textDecoration: todo.done ? "line-through" : "none",
                          color: todo.done ? "#6c757d" : "#212529"
                        }}>
                          {todo.done ? "✅" : "⏳"} {todo.title}
                        </span>
                        <small style={{ color: "#6c757d" }}>
                          #{todo.id}
                        </small>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ textAlign: "center", color: "#6c757d", fontStyle: "italic" }}>
                    No hay tareas para mostrar. Ve a la pestaña "TODOs" para crear algunas.
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: "center", color: "#666", padding: 20 }}>
              <p>No hay datos de tareas cargados. Haz clic en "Cargar Datos" para consultar las tareas.</p>
              <p style={{ fontSize: 12 }}>
                💡 La primera consulta tomará ~800ms (simulando base de datos), la segunda será instantánea desde el caché Redis.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
