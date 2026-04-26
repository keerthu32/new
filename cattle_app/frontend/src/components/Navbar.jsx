import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const role = localStorage.getItem("role");
  const navigate = useNavigate();

  const logout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <nav style={{ display: "flex", gap: 12, padding: 12 }}>
      <Link to="/">Home</Link>
      {!role && <Link to="/login">Login</Link>}
      {!role && <Link to="/register">Register</Link>}
      {role === "admin" && <Link to="/admin">Admin</Link>}
      {role === "seller" && <Link to="/seller">Seller</Link>}
      {role === "buyer" && <Link to="/buyer">Buyer</Link>}
      {role && <button onClick={logout}>Logout</button>}
    </nav>
  );
}
