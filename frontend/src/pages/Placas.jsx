import { useEffect, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Grid,
  IconButton,
  TextField,
  Typography,
} from "@mui/material";
import DeleteIcon from "@mui/icons-material/Delete";
import DirectionsCarIcon from "@mui/icons-material/DirectionsCar";

import api from "../services/api";
import SectionLabel from "../components/dashboard/SectionLabel";

// Lista de placas que abrem o portão sozinhas quando a câmera Yoosee
// reconhece — antes era uma única placa hardcoded no código
// (plate-detect-yoosee), agora é essa lista, editável aqui sem precisar
// mexer em código nem reiniciar nada.
export default function Placas() {
  const [plates, setPlates] = useState(null);
  const [name, setName] = useState("");
  const [plate, setPlate] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  async function load() {
    try {
      const res = await api.get("/plates");
      setPlates(res.data);
      setError(null);
    } catch {
      setError("Não consegui carregar a lista de placas.");
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function adicionar() {
    if (!name.trim() || !plate.trim()) return;
    setBusy(true);
    setMessage(null);
    setError(null);
    try {
      const res = await api.post("/plates", { name: name.trim(), plate: plate.trim() });
      setMessage(`Placa ${res.data.plate} cadastrada pra ${res.data.name}.`);
      setName("");
      setPlate("");
      await load();
    } catch (e) {
      setError(e?.response?.data?.detail || "Falha ao cadastrar a placa.");
    } finally {
      setBusy(false);
    }
  }

  async function remover(placa) {
    setBusy(true);
    setMessage(null);
    setError(null);
    try {
      await api.delete(`/plates/${placa}`);
      setMessage(`Placa ${placa} removida.`);
      await load();
    } catch {
      setError(`Falha ao remover ${placa}.`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>
        Placas
      </Typography>

      {message && <Alert severity="success" sx={{ mb: 2 }}>{message}</Alert>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <SectionLabel color="primary">Cadastrar placa de confiança</SectionLabel>

      <Card sx={{ p: 2, mb: 3 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Qualquer placa cadastrada aqui abre o portão sozinha quando a
            câmera Yoosee reconhecer, com uma tolerância pequena a erro de
            leitura (OCR).
          </Typography>

          <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "center" }}>
            <TextField
              label="Nome"
              size="small"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <TextField
              label="Placa"
              size="small"
              value={plate}
              onChange={(e) => setPlate(e.target.value.toUpperCase())}
            />
            <Button
              variant="contained"
              startIcon={<DirectionsCarIcon />}
              onClick={adicionar}
              disabled={busy || !name.trim() || !plate.trim()}
            >
              Cadastrar
            </Button>
            {busy && <CircularProgress size={20} />}
          </Box>
        </CardContent>
      </Card>

      <SectionLabel color="info">Cadastradas</SectionLabel>

      {plates === null ? (
        <CircularProgress size={24} />
      ) : (
        <Grid container spacing={2}>
          {plates.map((p) => (
            <Grid key={p.plate} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card>
                <CardContent sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <Box>
                    <Typography variant="subtitle1">{p.name}</Typography>
                    <Typography variant="body2" color="text.secondary">{p.plate}</Typography>
                  </Box>
                  <IconButton color="error" onClick={() => remover(p.plate)} disabled={busy}>
                    <DeleteIcon />
                  </IconButton>
                </CardContent>
              </Card>
            </Grid>
          ))}
          {plates.length === 0 && (
            <Typography color="text.secondary" sx={{ p: 2 }}>
              Nenhuma placa cadastrada ainda.
            </Typography>
          )}
        </Grid>
      )}
    </Box>
  );
}
