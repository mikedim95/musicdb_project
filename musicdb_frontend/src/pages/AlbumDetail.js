import { useParams } from "react-router-dom";
import { useQuery } from "react-query";
import { Spinner, Alert, ListGroup } from "react-bootstrap";

export default function AlbumDetail() {
  const { id } = useParams();
  const { data, isLoading, error } = useQuery(["album", id], () =>
    fetch(`/api/albums/${id}/`).then((res) => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
  );

  if (isLoading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{String(error.message)}</Alert>;
  if (!data) return <Alert variant="warning">Album not found</Alert>;

  return (
    <div>
      <h1>{data.title}</h1>
      <p>
        <strong>Artist:</strong> {data.artist}
      </p>
      <p>{data.description}</p>

      <h5>Tracklist</h5>
      <ListGroup>
        {data.tracklist.map((track, idx) => (
          <ListGroup.Item key={idx}>
            {track.position}. {track.song.title} — {track.song.duration}s
          </ListGroup.Item>
        ))}
      </ListGroup>
    </div>
  );
}
