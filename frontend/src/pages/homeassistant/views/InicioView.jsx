import { Box, Grid, CircularProgress } from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import VideocamIcon from "@mui/icons-material/Videocam";

import { useWeather } from "../../../hooks/useWeather";
import { useActivity } from "../../../hooks/useActivity";
import { useHomeAssistantAreas, useHomeAssistantScenes } from "../../../modules/jarvis/services/haApi";

import WeatherCard from "../../../components/dashboard/WeatherCard";
import SwitchCard from "../../../components/dashboard/SwitchCard";
import MediaPlayerCard from "../../../components/dashboard/MediaPlayerCard";
import HeaderStats from "../../../components/dashboard/HeaderStats";
import ActivityFeed from "../../../components/dashboard/ActivityFeed";
import SectionLabel from "../../../components/dashboard/SectionLabel";
import FloorPlanPanel from "./inicio/FloorPlanPanel";
import ActionButtonGrid from "../widgets/ActionButtonGrid";
import EntitiesStatusCard from "../widgets/EntitiesStatusCard";

// Mesmo filtro de "ruído" já usado em AreasView.jsx — domínios que fazem
// sentido controlar/ver de relance por cômodo (câmeras ficam de fora,
// já têm aba própria).
const DOMINIOS_RELEVANTES = [
  "light", "switch", "climate", "cover", "fan",
  "media_player", "binary_sensor", "lock", "vacuum",
];

const PERSON_ENTITIES = ["person.casa_inteligente", "person.taiane", "person.heitor"];
const SCENE_ENTITY = "scene.unitv_projetor";
const MEDIA_PLAYER_ENTITIES = ["media_player.bruno_s_n65b", "media_player.alexa_taiane"];

// Mesma lista de EquipamentosView.jsx (DETECCAO_FACIAL) — trazida pra
// cá também, a pedido do usuário.
const DETECCAO_FACIAL = [
  { entityId: "binary_sensor.icsee_rosto_detectado", label: "Rosto detectado" },
  { entityId: "sensor.icsee_rostos_detectados", label: "Quantidade de rostos" },
];

// Mesma lista de EquipamentosView.jsx (STATUS_GERAL) — trazida pra cá
// também, a pedido do usuário.
const STATUS_GERAL = [
  { entityId: "person.casa_inteligente", label: "Bruno" },
  { entityId: "person.taiane", label: "Taiane" },
  { entityId: "person.heitor", label: "Heitor" },
  { entityId: "sensor.icsee_pessoa_reconhecida", label: "Reconhecido pela câmera" },
  { entityId: "switch.portao_casa_switch_1", label: "Portão" },
  { entityId: "media_player.bruno_s_n65b", label: "TV" },
  { entityId: "media_player.alexa_taiane", label: "Alexa Taiane" },
];

const PERSON_STATE_LABEL = {
  home: "Em casa",
  not_home: "Fora",
  unknown: "Desconhecido",
};

export default function InicioView({ byId, activateScene, playPause, mediaNext, mediaPrevious, setVolume }) {

  const { data: weatherData } = useWeather();
  const { data: activity } = useActivity(8);
  const { data: areas, isLoading: areasLoading } = useHomeAssistantAreas();
  const { data: scenes } = useHomeAssistantScenes();

  const areasComDispositivos = (areas || [])
    .map((area) => ({
      ...area,
      entities: area.entities
        .filter(({ entity_id }) => DOMINIOS_RELEVANTES.includes(entity_id.split(".")[0]))
        .map(({ entity_id, label }) => ({ entityId: entity_id, label })),
    }))
    .filter((area) => area.entities.length > 0);

  const automationEntities = Object.keys(byId).filter((id) => id.startsWith("automation."));
  const automationsOn = automationEntities.filter((id) => byId[id]?.state === "on").length;

  const cenaActions = (scenes || [])
    .map(({ entity_id, label }) => ({
      label,
      domain: "script",
      service: "turn_on",
      entityId: entity_id,
    }))
    .sort((a, b) => a.label.localeCompare(b.label));

  return (
    <>
      {/* PREVISÃO DO TEMPO: topo */}
      <Box sx={{ mb: 3 }}>
        <WeatherCard data={weatherData} />
      </Box>

      {/* CONTROLES: mídia primeiro (play/pause de verdade, não coberto
          pelo card genérico por área), depois os cômodos */}
      <Box sx={{ mb: 3 }}>

        <SectionLabel color="primary">
          MÍDIA
        </SectionLabel>

        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
          {MEDIA_PLAYER_ENTITIES.map((id) => (
            <Box key={id} sx={{ flex: "1 1 260px", maxWidth: { xs: "100%", md: 320 } }}>
              <MediaPlayerCard
                entity={byId[id]}
                onPlayPause={() => playPause(id)}
                onNext={mediaNext ? () => mediaNext(id) : undefined}
                onPrevious={mediaPrevious ? () => mediaPrevious(id) : undefined}
                onVolumeChange={setVolume ? (level) => setVolume(id, level) : undefined}
              />
            </Box>
          ))}
        </Box>

      </Box>

      {/* STATUS GERAL — mesma lista de EquipamentosView.jsx */}
      <Box sx={{ mb: 3 }}>
        <EntitiesStatusCard title="Status Geral" entities={STATUS_GERAL} color="primary" />
      </Box>

      {/* CÔMODOS — mesma fonte de dados/filtro da aba "Áreas", trazida
          pra tela principal em vez de enterrada numa aba própria. */}
      <Box sx={{ mb: 3 }}>

        <SectionLabel color="primary">
          CÔMODOS
        </SectionLabel>

        {areasLoading ? (
          <CircularProgress size={24} />
        ) : (
          <Grid container spacing={2}>
            {areasComDispositivos.map((area) => (
              <Grid key={area.area_id} size={{ xs: 12, sm: 6, md: 4 }}>
                <EntitiesStatusCard title={area.name} entities={area.entities} color="primary" />
              </Grid>
            ))}
          </Grid>
        )}

      </Box>

      {/* CENAS+INFORMAÇÕES (esq) / PLANTA DA CASA (centro) / PRESENÇA (dir) */}
      <Box sx={{ display: "flex", gap: 2, alignItems: "flex-start", flexWrap: "wrap" }}>

        {/* ESQUERDA: Cenas em cima, Informações embaixo */}
        <Box sx={{ flex: "1 1 280px", maxWidth: { xs: "100%", md: 340 } }}>

          {cenaActions.length > 0 ? (
            <ActionButtonGrid title="CENAS" actions={cenaActions} columns={2} color="secondary" />
          ) : (
            <>
              <SectionLabel color="secondary">
                CENAS
              </SectionLabel>
              <SwitchCard
                icon={<VideocamIcon />}
                name="Projetor"
                isOn={false}
                onToggle={() => activateScene(SCENE_ENTITY)}
                color="secondary"
              />
            </>
          )}

          <SectionLabel color="info" sx={{ mt: 3 }}>
            INFORMAÇÕES
          </SectionLabel>

          <HeaderStats
            stats={activity?.stats}
            automationsOn={automationsOn}
            automationsTotal={automationEntities.length}
          />

          <Box sx={{ mt: 2 }}>
            <ActivityFeed items={activity?.recent} />
          </Box>

        </Box>

        {/* CENTRO: planta da casa */}
        <Box sx={{ flex: "2 1 320px", minWidth: 0 }}>
          <FloorPlanPanel byId={byId} />
        </Box>

        {/* DIREITA: Presença */}
        <Box sx={{ flex: "1 1 220px", maxWidth: { xs: "100%", md: 260 } }}>

          <SectionLabel color="success">
            PRESENÇA
          </SectionLabel>

          {PERSON_ENTITIES.map((id) => {
            const p = byId[id];
            return (
              <SwitchCard
                key={id}
                icon={<PersonIcon />}
                name={p?.attributes?.friendly_name || id}
                isOn={p?.state === "home"}
                stateLabel={p ? (PERSON_STATE_LABEL[p.state] || p.state) : "--"}
                color="success"
                lastChanged={p?.last_updated}
              />
            );
          })}

          <Box sx={{ mt: 2 }}>
            <EntitiesStatusCard title="Detecção Facial" entities={DETECCAO_FACIAL} color="error" />
          </Box>

        </Box>

      </Box>
    </>
  );
}
