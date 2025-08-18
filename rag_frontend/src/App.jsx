// App.jsx
import { Routes, Route } from "react-router-dom";
import Home from "./Home";
import Admin from "./Admin";
import NotFound from "./NotFound";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/admin" element={<Admin />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
