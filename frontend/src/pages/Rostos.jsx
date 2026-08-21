import { useEffect, useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid,
  IconButton,
  TextField,
  Typography,
  Alert,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import CameraAltIcon from "@mui/icons-material/CameraAlt";
import ModelTrainingIcon from "@mui/icons-material/ModelTraining";

import api from "../services/api";
import SectionLabel from "../components/dashboard/SectionLabel";

// Cadastro de rosto pela câmera ao vivo (não é upload de foto) — a
// pessoa precisa estar na frente da câmera "da sala" (icsee frente) na
// hora de clicar "Capturar". O backend só faz proxy pro serviço de
// detecção (face-detect-icsee:8091), que recorta o rosto do frame
// atual e salva. "Treinar" reprocessa tudo e recarrega o modelo
// sozinho, sem precisar reiniciar nada.
export default function Rostos() {
  const [people, setPeople] = useState(null);
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  async function load() {
    try {
      const res = await api.get("/detection/people");
      setPeople(res.data);
      setError(null);
    } catch {
      setError("Não consegui falar com o serviço de detecção facial.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function capturar() {
    if (!name.trim()) return;
    setBusy(true);
    setMessage(null);
    setError(null);
    try {
      const res = await api.post("/detection/enroll", null, { params: { name: name.trim() } });
      setMessage(`Capturado! ${res.data.name} agora tem ${res.data.saved} fotos.`);
      await load();
    } catch (e) {
      setError(e?.response?.data?.detail || "Falha na captura — confira se tem alguém de frente pra câmera agora.");
    } finally {
      setBusy(false);
    }
  }

  async function treinar() {
    setBusy(true);
    setMessage(null);
    setError(null);
    try {
      await api.post("/detection/train");
      setMessage("Modelo retreinado e recarregado com sucesso.");
    } catch (e) {
      setError(e?.response?.data?.detail || "Falha ao treinar — precisa de pelo menos uma pessoa com fotos.");
    } finally {
      setBusy(false);
    }
  }

  async function remover(pessoa) {
    setBusy(true);
    setMessage(null);
    setError(null);
    try {
      await api.delete(`/detection/people/${pessoa}`);
      setMessage(`${pessoa} removido do cadastro.`);
      await load();
    } catch {
      setError(`Falha ao remover ${pessoa}.`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>
        Rostos
      </Typography>

      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <SectionLabel color="primary">Capturar novo rosto</SectionLabel>

      <Card sx={{ p: 2, mb: 3 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            A pessoa precisa estar de frente pra câmera da sala agora. Clique
            "Capturar" várias vezes (10-20x, variando ângulo/expressão), depois
            "Treinar modelo" uma vez no final.
          </Typography>

          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "center" }}>
            <TextField
              label="Nome"
              size="small"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <Button
              variant="contained"
              startIcon={<CameraAltIcon />}
              onClick={capturar}
              disabled={busy || !name.trim()}
            >
              Capturar
            </Button>
            <Button
              variant="outlined"
              color="secondary"
              startIcon={<ModelTrainingIcon />}
              onClick={treinar}
              disabled={busy}
            >
              Treinar modelo
            </Button>
            {busy && <CircularProgress size={20} />}
          </Box>
        </CardContent>
      </Card>

      <SectionLabel color="info">Cadastrados</SectionLabel>

      {people === null ? (
        <CircularProgress size={24} />
      ) : (
        <Grid container spacing={2}>
          {Object.entries(people).map(([pessoa, quantidade]) => (
            <Grid key={pessoa} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card>
                <CardContent sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <Box>
                    <Typography variant="subtitle1">{pessoa}</Typography>
                    <Chip
                      size="small"
                      label={`${quantidade} foto${quantidade === 1 ? "" : "s"}`}
                      color={quantidade > 0 ? "success" : "default"}
                    />
                  </Box>
                  <IconButton color="error" onClick={() => remover(pessoa)} disabled={busy}>
                    <DeleteIcon />
                  </IconButton>
                </CardContent>
              </Card>
            </Grid>
          ))}
          {Object.keys(people).length === 0 && (
            <Typography color="text.secondary" sx={{ p: 2 }}>
              Ninguém cadastrado ainda.
            </Typography>
          )}
        </Grid>
      )}
    </Box>
  );
}
