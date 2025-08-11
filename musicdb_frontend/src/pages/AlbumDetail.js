import { useParams, Link } from "react-router-dom";
import { useQuery } from "react-query";
import { Spinner, Alert, ListGroup, Breadcrumb } from "react-bootstrap";

function formatSeconds(s) {
  if (!Number.isFinite(s)) return `${s ?? "?"}s`;
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${String(sec).padStart(2, "0")}`;
}

export default function AlbumDetail() {
  const { id } = useParams();

  const { data, isLoading, error } = useQuery(["album", id], () =>
    fetch(`/api/albums/${id}/?format=json`, {
      headers: { Accept: "application/json" },
    }).then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
  );

  if (isLoading) return <Spinner animation="border" />;
  if (error) return <Alert variant="danger">{String(error.message)}</Alert>;
  if (!data) return <Alert variant="warning">Album not found</Alert>;

  // be defensive about serializer shapes
  const tracklist = Array.isArray(data.tracks) ? data.tracks : [];
  console.log("AlbumDetail: tracklist", tracklist);
  const tracks = tracklist.map((t, i) => ({
    key: t.id ?? i,
    pos: t.position ?? i + 1,
    title: t.song?.title ?? t.title ?? "(untitled)",
    duration: t.song?.duration ?? t.duration ?? null,
  }));

  return (
    <div>
      <Breadcrumb className="mb-3">
        <Breadcrumb.Item linkAs={Link} linkProps={{ to: "/" }}>
          Home
        </Breadcrumb.Item>
        <Breadcrumb.Item active>{data.title}</Breadcrumb.Item>
      </Breadcrumb>

      <h1 className="mb-1">{data.title}</h1>
      <div className="text-muted mb-3">
        {data.artist} •{" "}
        {data.release_year ?? new Date(data.release_date).getFullYear()}
      </div>

      {data.description && <p className="mb-4">{data.description}</p>}

      <h5 className="mb-2">Tracklist</h5>
      {tracks.length === 0 ? (
        <p className="text-muted">No tracks</p>
      ) : (
        <ListGroup>
          {tracks.map((t) => (
            <ListGroup.Item key={t.key}>
              {t.pos}. {t.title}
              {t.duration != null
                ? ` — ${formatSeconds(Number(t.duration))}`
                : ""}
            </ListGroup.Item>
          ))}
        </ListGroup>
      )}
    </div>
  );
}
