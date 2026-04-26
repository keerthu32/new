import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ children, allow }) {
  const role = localStorage.getItem("role");
  if (!role) return <Navigate to="/login" replace />;
  if (allow && !allow.includes(role)) return <Navigate to="/" replace />;
  return children;
}
