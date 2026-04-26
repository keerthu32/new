import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../api";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "buyer" });
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    await registerUser(form);
    navigate("/login");
  };

  return (
    <form onSubmit={submit}>
      <h2>Register</h2>
      <input placeholder="Name" onChange={(e) => setForm({ ...form, name: e.target.value })} />
      <input placeholder="Email" onChange={(e) => setForm({ ...form, email: e.target.value })} />
      <input placeholder="Password" type="password" onChange={(e) => setForm({ ...form, password: e.target.value })} />
      <select onChange={(e) => setForm({ ...form, role: e.target.value })} value={form.role}>
        <option value="buyer">buyer</option>
        <option value="seller">seller</option>
        <option value="admin">admin</option>
      </select>
      <button type="submit">Register</button>
    </form>
  );
}
