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
import SectionLabel from "../components/dashboard/SectionLabel";

function formatBytes(bytes) {
  const n = Number(bytes || 0);
  if (n > 1024 * 1024 * 1024) return (n / 1024 / 1024 / 1024).toFixed(2) + " GB";
  if (n > 1024 * 1024) return (n / 1024 / 1024).toFixed(2) + " MB";
  if (n > 1024) return (n / 1024).toFixed(2) + " KB";
  return n + " B";
}

export default function Mikrotik() {
  const [status, setStatus] = useState(null);
  const [resource, setResource] = useState(null);
  const [interfaces, setInterfaces] = useState([]);
  const [leases, setLeases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function load() {
    try {
      const [s, r, i, l] = await Promise.all([
        api.get("/mikrotik/status"),
        api.get("/mikrotik/resource"),
        api.get("/mikrotik/interfaces"),
        api.get("/mikrotik/leases")
      ]);
      setStatus(s.data);
      setResource(r.data);
      setInterfaces(i.data || []);
      setLeases(Array.isArray(l.data) ? l.data : []);
      setError(null);
    } catch (e) {
      setError("Não foi possível conectar ao MikroTik.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 20000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <CircularProgress />;

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  const connected = status?.connected;
  const connectedDevices = leases.filter((l) => l.status === "bound").length;
  const wanInterface = interfaces.find((iface) => iface.name === "PPPOE-ISP");
  const internetOnline = wanInterface?.running === "true";
  const memUsedPct = resource
    ? Math.round(
        ((Number(resource["total-memory"]) - Number(resource["free-memory"])) /
          Number(resource["total-memory"])) *
          100
      )
    : null;
  const diskUsedPct = resource
    ? Math.round(
        ((Number(resource["total-hdd-space"]) - Number(resource["free-hdd-space"])) /
          Number(resource["total-hdd-space"])) *
          100
      )
    : null;

  return (
    <>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          MikroTik
        </Typography>
        <Box sx={{ display: "flex", gap: 1 }}>
          <Chip
            label={connected ? `Online — ${status.identity}` : "Offline"}
            color={connected ? "success" : "error"}
          />
          <Chip
            label={internetOnline ? "Internet Online" : "Internet Offline"}
            color={internetOnline ? "success" : "error"}
          />
        </Box>
      </Box>

      {resource && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">CPU</Typography>
                <Typography variant="h5" sx={{ mt: 1 }}>{resource["cpu-load"]}%</Typography>
                <Typography variant="caption" color="text.secondary">{resource.cpu}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Memória</Typography>
                <Typography variant="h5" sx={{ mt: 1 }}>{memUsedPct}%</Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatBytes(resource["free-memory"])} livres
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Disco</Typography>
                <Typography variant="h5" sx={{ mt: 1 }}>{diskUsedPct}%</Typography>
                <Typography variant="caption" color="text.secondary">
                  {formatBytes(resource["free-hdd-space"])} livres
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Uptime</Typography>
                <Typography variant="h6" sx={{ mt: 1 }}>{resource.uptime}</Typography>
                <Typography variant="caption" color="text.secondary">
                  RouterOS {resource.version}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <Typography color="text.secondary">Dispositivos conectados</Typography>
                <Typography variant="h5" sx={{ mt: 1 }}>{connectedDevices}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {leases.length} reservas cadastradas
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      <SectionLabel color="info">
        Interfaces
      </SectionLabel>

      <Grid container spacing={2}>
        {interfaces
          .filter((iface) => iface.type !== "loopback")
          .map((iface) => (
            <Grid size={{ xs: 12, md: 4 }} key={iface.id}>
              <Card
                sx={(theme) => ({
                  border: "1px solid",
                  borderColor: iface.running === "true" ? "success.main" : "rgba(255,255,255,.08)",
                  boxShadow: iface.running === "true" ? `0 0 14px -6px ${theme.palette.success.main}` : "none",
                })}
              >
                <CardContent>
                  <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
                    <Typography variant="subtitle1">{iface.name}</Typography>
                    <Chip
                      label={iface.running === "true" ? "up" : "down"}
                      color={iface.running === "true" ? "success" : "default"}
                      size="small"
                    />
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {iface.type}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    RX: {formatBytes(iface["rx-byte"])} · TX: {formatBytes(iface["tx-byte"])}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
      </Grid>
    </>
  );
}
