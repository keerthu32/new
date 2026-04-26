import { Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import Admin from "./pages/Admin";
import Buyer from "./pages/Buyer";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Seller from "./pages/Seller";

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/admin"
          element={
            <ProtectedRoute allow={["admin"]}>
              <Admin />
            </ProtectedRoute>
          }
        />
        <Route
          path="/seller"
          element={
            <ProtectedRoute allow={["seller", "admin"]}>
              <Seller />
            </ProtectedRoute>
          }
        />
        <Route
          path="/buyer"
          element={
            <ProtectedRoute allow={["buyer", "admin"]}>
              <Buyer />
            </ProtectedRoute>
          }
        />
      </Routes>
    </>
  );
}
