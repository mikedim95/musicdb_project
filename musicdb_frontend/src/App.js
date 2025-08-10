import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import AlbumList from "./pages/AlbumList";
import AlbumDetail from "./pages/AlbumDetail";

export default function App() {
  return (
    <Router>
      <div className="container py-4">
        <Routes>
          <Route path="/" element={<AlbumList />} />
          <Route path="/albums/:id" element={<AlbumDetail />} />
        </Routes>
      </div>
    </Router>
  );
}
