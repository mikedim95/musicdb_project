import { useQuery } from "react-query";
import { Table, Spinner, Alert } from "react-bootstrap";
import { Link } from "react-router-dom";

export default function AlbumList() {
  const { data, isLoading, error } = useQuery("albums", () =>
    fetch("http://localhost:8000/api/albums/", {
      headers: { Accept: "application/json" },
    }).then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
  );

  if (isLoading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{String(error.message)}</Alert>;

  return (
    <div>
      <h1>Albums</h1>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Title</th>
            <th>Artist</th>
            <th>Price</th>
          </tr>
        </thead>
        <tbody>
          {data.map((album) => (
            <tr key={album.id}>
              <td>
                <Link to={`/albums/${album.id}`}>{album.title}</Link>
              </td>
              <td>{album.artist}</td>
              <td>${Number(album.price).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}
