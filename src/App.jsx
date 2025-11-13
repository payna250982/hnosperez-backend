import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [fichajes, setFichajes] = useState([]);
  const [message, setMessage] = useState("");

  // ESTA ES LA LÍNEA QUE HEMOS CAMBIADO:
  const API = import.meta.env.VITE_API_URL; // URL del backend

  // Registrar usuario
  const handleRegister = async () => {
    try {
      const res = await axios.post(`${API}/register`, { username, password });
      setMessage(res.data.message);
      setUsername("");
      setPassword("");
      fetchFichajes();
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail
          ? Array.isArray(err.response.data.detail)
            ? err.response.data.detail.map(e => e.msg).join(", ")
            : err.response.data.detail
          : "Error desconocido";
      setMessage(errorMsg);
    }
  };

  // Fichar entrada
  const handleEntrada = async () => {
    try {
      const res = await axios.post(`${API}/fichar_entrada`, { username });
      setMessage(res.data.message);
      fetchFichajes();
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail || "Error al fichar entrada";
      setMessage(errorMsg);
    }
  };

  // Fichar salida
  const handleSalida = async () => {
    try {
      const res = await axios.post(`${API}/fichar_salida`, { username });
      setMessage(res.data.message);
      fetchFichajes();
    } catch (err) {
      const errorMsg =
        err.response?.data?.detail || "Error al fichar salida";
      setMessage(errorMsg);
    }
  };

  // Obtener fichajes
  const fetchFichajes = async () => {
    try {
      const res = await axios.get(`${API}/fichajes`);
      setFichajes(res.data);
    } catch (err) {
      console.log(err);
    }
  };

  useEffect(() => {
    fetchFichajes();
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h1>Control de Horas HnosPerez</h1>

      <div style={{ marginBottom: 20 }}>
        <input
          placeholder="Usuario"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          placeholder="Contraseña"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="button" onClick={handleRegister}>
          Registrar Usuario
        </button>
      </div>

      <div style={{ marginBottom: 20 }}>
        <button type="button" onClick={handleEntrada}>
          Fichar Entrada
        </button>
        <button type="button" onClick={handleSalida}>
          Fichar Salida
        </button>
      </div>

      {message && <p>{message}</p>}

      <h2>Fichajes</h2>
      <table border="1" cellPadding="5">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Entrada</th>
            <th>Salida</th>
          </tr>
        </thead>
        <tbody>
          {fichajes.map((f, index) => (
            <tr key={index}>
              <td>{f.usuario}</td>
              <td>{f.entrada}</td>
              <td>{f.salida || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
