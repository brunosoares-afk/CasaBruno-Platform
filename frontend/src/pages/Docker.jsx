import { useEffect, useState } from "react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  CircularProgress,
  Box
} from "@mui/material";

import api from "../services/api";

export default function Docker() {
  const [containers, setContainers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    try {
      const res = await api.get("/containers");
      setContainers(res.data || []);
      setError(null);
    } catch (e) {
      setError("Não foi possível carregar os containers.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <CircularProgress />;

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 700 }}>
        Docker
      </Typography>

      <Grid container spacing={3}>
        {containers.map((c) => (
          <Grid size={{ xs: 12, md: 4 }} key={c.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
                  <Typography variant="h6">{c.name}</Typography>
                  <Chip
                    label={c.status}
                    color={c.status === "running" ? "success" : "default"}
                    size="small"
                  />
                </Box>

                <Typography variant="body2" color="text.secondary">
                  {c.image}
                </Typography>

                {c.ip && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    IP: {c.ip}
                  </Typography>
                )}

                {c.ports.length > 0 && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Portas: {c.ports.join(", ")}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </>
  );
}
