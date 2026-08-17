import { useMemo, useState } from "react";
import {
  Box,
  Typography,
  Chip,
  CircularProgress,
  Tabs,
  Tab
} from "@mui/material";

import { useHomeAssistantStates } from "../hooks/useHomeAssistantStates";
import { callService } from "../api/homeassistantService";

import InicioView from "./homeassistant/views/InicioView";
import CamerasView from "./homeassistant/views/CamerasView";
import EquipamentosView from "./homeassistant/views/EquipamentosView";
import AreasView from "./homeassistant/views/AreasView";
import CenasView from "./homeassistant/views/CenasView";
import AutomacoesView from "./homeassistant/views/AutomacoesView";
import RedeView from "./homeassistant/views/RedeView";
import AgendaView from "./homeassistant/views/AgendaView";

const TABS = [
  { value: "inicio", label: "Início" },
  { value: "cameras", label: "Câmeras" },
  { value: "equipamentos", label: "Equipamentos" },
  { value: "areas", label: "Áreas" },
  { value: "cenas", label: "Cenas" },
  { value: "automacoes", label: "Automações" },
  { value: "rede", label: "Rede" },
  { value: "agenda", label: "Agenda" },
];

export default function HomeAssistant() {

  const { data: states, isLoading, isError, refetch } = useHomeAssistantStates();
  const [tab, setTab] = useState("inicio");

  const byId = useMemo(() => {
    const map = {};
    (states || []).forEach((s) => { map[s.entity_id] = s; });
    return map;
  }, [states]);

  const online = !isError;

  async function toggleLight(entityId, isOn) {
    await callService("light", isOn ? "turn_off" : "turn_on", { entity_id: entityId });
    refetch();
  }

  async function pulseSwitch(entityId) {
    await callService("switch", "turn_on", { entity_id: entityId });
    refetch();
  }

  async function activateScene(entityId) {
    await callService("scene", "turn_on", { entity_id: entityId });
    refetch();
  }

  async function playPause(entityId) {
    await callService("media_player", "media_play_pause", { entity_id: entityId });
    refetch();
  }

  async function mediaNext(entityId) {
    await callService("media_player", "media_next_track", { entity_id: entityId });
    refetch();
  }

  async function mediaPrevious(entityId) {
    await callService("media_player", "media_previous_track", { entity_id: entityId });
    refetch();
  }

  async function setVolume(entityId, level) {
    await callService("media_player", "volume_set", { entity_id: entityId, volume_level: level });
    refetch();
  }

  if (isLoading) return <CircularProgress />;

  return (
    <>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>
          Principal
        </Typography>
        <Chip
          label={online ? "HA Online" : "HA Offline"}
          color={online ? "success" : "error"}
        />
      </Box>

      <Tabs
        value={tab}
        onChange={(_, v) => setTab(v)}
        variant="scrollable"
        scrollButtons="auto"
        allowScrollButtonsMobile
        sx={{ mb: 3 }}
      >
        {TABS.map((t) => (
          <Tab key={t.value} value={t.value} label={t.label} />
        ))}
      </Tabs>

      {tab === "inicio" && (
        <InicioView
          byId={byId}
          toggleLight={toggleLight}
          pulseSwitch={pulseSwitch}
          activateScene={activateScene}
          playPause={playPause}
          mediaNext={mediaNext}
          mediaPrevious={mediaPrevious}
          setVolume={setVolume}
        />
      )}

      {tab === "cameras" && <CamerasView />}
      {tab === "equipamentos" && <EquipamentosView />}
      {tab === "areas" && <AreasView />}
      {tab === "cenas" && <CenasView />}
      {tab === "automacoes" && <AutomacoesView />}
      {tab === "rede" && <RedeView />}
      {tab === "agenda" && <AgendaView />}

    </>
  );
}
