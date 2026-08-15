import { Box, Grid, CircularProgress } from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import VideocamIcon from "@mui/icons-material/Videocam";

import { useWeather } from "../../../hooks/useWeather";
import { useActivity } from "../../../hooks/useActivity";
import { useHomeAssistantAreas } from "../../../modules/jarvis/services/haApi";

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

// Cenas de verdade da casa (scripts.yaml, prefixo "cena_") — antes essa
// seção era 1 tile hardcoded pro projetor; agora pega toda cena real
// direto do estado ao vivo (byId), sem lista fixa que fica desatualizada
// toda vez que uma cena nova é criada em scripts.yaml.
const isSceneEntity = (id) => id.startsWith("script.cena_") || id.startsWith("scene.");

const PERSON_ENTITIES = ["person.casa_inteligente", "person.taiane", "person.teste_casa"];
const SCENE_ENTITY = "scene.unitv_projetor";
const MEDIA_PLAYER_ENTITIES = ["media_player.alexa_taiane", "media_player.bruno_s_n65b"];

const PERSON_STATE_LABEL = {
  home: "Em casa",
  not_home: "Fora",
  unknown: "Desconhecido",
};

export default function InicioView({ byId, activateScene, playPause }) {

  const { data: weatherData } = useWeather();
  const { data: activity } = useActivity(8);
  const { data: areas, isLoading: areasLoading } = useHomeAssistantAreas();

  const areasComDispositivos = (areas || [])
    .map((area) => ({
      ...area,
      entities: area.entity_ids
        .filter((id) => DOMINIOS_RELEVANTES.includes(id.split(".")[0]))
        .map((entityId) => ({ entityId })),
    }))
    .filter((area) => area.entities.length > 0);

  const automationEntities = Object.keys(byId).filter((id) => id.startsWith("automation."));
  const automationsOn = automationEntities.filter((id) => byId[id]?.state === "on").length;

  const cenaActions = Object.keys(byId)
    .filter(isSceneEntity)
    .map((id) => ({
      label: byId[id]?.attributes?.friendly_name?.replace(/^Cena:\s*/i, "") || id,
      domain: id.split(".")[0],
      service: "turn_on",
      entityId: id,
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
              />
            </Box>
          ))}
        </Box>

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
              />
            );
          })}

        </Box>

      </Box>
    </>
  );
}
