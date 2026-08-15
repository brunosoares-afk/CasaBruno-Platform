import { useEffect, useState } from "react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Box,
  Chip
} from "@mui/material";

import api from "../services/api";
import PacketLossCard from "../components/dashboard/PacketLossCard";

export default function Network() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await api.get("/network/devices");
        setDevices(res.data || []);
        setError(null);
      } catch {
        setError("Não foi possível carregar o status da rede.");
      } finally {
        setLoading(false);
      }
    }

    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <CircularProgress />;

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <>
      <Typography variant="h4" sx={{ mb: 4, fontWeight: 700 }}>
        Rede
      </Typography>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <PacketLossCard />
        </Grid>

        {devices.map((d) => (
          <Grid size={{ xs: 12, md: 4 }} key={d.host}>
            <Card>
              <CardContent>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
                  <Typography variant="h6">{d.name}</Typography>
                  <Chip
                    label={d.online ? "Online" : "Offline"}
                    color={d.online ? "success" : "error"}
                    size="small"
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {d.host}
                </Typography>
                {d.online && d.latency_ms != null && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Latência: {d.latency_ms} ms
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
