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

export default function HomeAssistant() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    try {
      const res = await api.get("/homeassistant/summary");
      setSummary(res.data);
      setError(null);
    } catch (e) {
      setError("Não foi possível conectar ao Home Assistant.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <CircularProgress />;

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  const online = summary?.status?.online;
  const devices = summary?.devices || {};
  const weather = summary?.weather || {};

  return (
    <>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          Home Assistant
        </Typography>
        <Chip
          label={online ? "Online" : "Offline"}
          color={online ? "success" : "error"}
        />
      </Box>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Total de entidades</Typography>
              <Typography variant="h5" sx={{ mt: 1 }}>{devices.total ?? "--"}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Online</Typography>
              <Typography variant="h5" sx={{ mt: 1 }}>{devices.online ?? "--"}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Offline</Typography>
              <Typography variant="h5" sx={{ mt: 1 }}>{devices.offline ?? "--"}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 3 }}>
          <Card>
            <CardContent>
              <Typography color="text.secondary">Clima</Typography>
              <Typography variant="h6" sx={{ mt: 1 }}>
                {weather.state ? `${weather.state}` : "--"}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {devices.domains && Object.entries(devices.domains).map(([domain, count]) => (
          <Grid size={{ xs: 6, md: 2 }} key={domain}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary">{domain}</Typography>
                <Typography variant="h6">{count}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </>
  );
}
