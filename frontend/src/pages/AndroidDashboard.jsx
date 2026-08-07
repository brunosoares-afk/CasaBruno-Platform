import { useEffect, useState } from "react";
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Stack,
  CircularProgress,
  Chip
} from "@mui/material";

import api from "../services/api";

const SCENES = [
  { id: "unitv", label: "UNITV" },
  { id: "desenho-heitor", label: "Desenho Heitor" },
];

export default function AndroidDashboard() {

  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sceneStatus, setSceneStatus] = useState({});

  async function load() {
    try {
      const res = await api.get("/android/devices");
      setDevices(res.data.devices || []);
    } finally {
      setLoading(false);
    }
  }

  async function send(device, command) {
    await api.get(`/android/${device}/${command}`);
    load();
  }

  async function runScene(sceneId) {
    setSceneStatus((prev) => ({ ...prev, [sceneId]: "Iniciando..." }));
    try {
      const res = await api.post(`/scenes/${sceneId}`);
      setSceneStatus((prev) => ({ ...prev, [sceneId]: res.data.message }));
    } catch (e) {
      setSceneStatus((prev) => ({ ...prev, [sceneId]: "Erro ao iniciar" }));
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) return <CircularProgress />;

  return (
    <>
      <Grid container spacing={3}>
        {devices.map((d) => (
          <Grid size={{ xs: 12, md: 6 }} key={d.id}>
            <Card>
              <CardContent>

                <Typography variant="h5">
                  {d.name}
                </Typography>

                <Typography sx={{ mb: 2 }}>
                  Status: {d.status}
                </Typography>

                <Stack direction="row" spacing={2}>

                  <Button
                    variant="contained"
                    onClick={() => send(d.id, "home")}
                  >
                    Home
                  </Button>

                  <Button
                    variant="contained"
                    onClick={() => send(d.id, "back")}
                  >
                    Voltar
                  </Button>

                  <Button
                    variant="contained"
                    onClick={() => send(d.id, "power")}
                  >
                    Power
                  </Button>

                </Stack>

              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Typography variant="h6" sx={{ mt: 4, mb: 2 }}>
        Cenas
      </Typography>

      <Grid container spacing={3}>
        {SCENES.map((scene) => (
          <Grid size={{ xs: 12, md: 6 }} key={scene.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  {scene.label}
                </Typography>

                <Stack direction="row" spacing={2} alignItems="center">
                  <Button
                    variant="contained"
                    color="secondary"
                    onClick={() => runScene(scene.id)}
                  >
                    Ativar
                  </Button>

                  {sceneStatus[scene.id] && (
                    <Chip label={sceneStatus[scene.id]} size="small" />
                  )}
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </>
  );
}
