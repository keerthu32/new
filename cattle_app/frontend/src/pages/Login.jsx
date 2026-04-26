import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    const { data } = await loginUser(form);
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("role", data.role);
    if (data.role === "admin") navigate("/admin");
    if (data.role === "seller") navigate("/seller");
    if (data.role === "buyer") navigate("/buyer");
  };

  return (
    <form onSubmit={submit}>
      <h2>Login</h2>
      <input placeholder="Email" onChange={(e) => setForm({ ...form, email: e.target.value })} />
      <input placeholder="Password" type="password" onChange={(e) => setForm({ ...form, password: e.target.value })} />
      <button type="submit">Login</button>
    </form>
  );
}
