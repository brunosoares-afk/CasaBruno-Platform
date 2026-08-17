import { Grid, CircularProgress } from "@mui/material";
import EntitiesStatusCard from "../widgets/EntitiesStatusCard";
import { useHomeAssistantAreas } from "../../../modules/jarvis/services/haApi";

// O HA tem muita entidade "ruído" por área (diagnóstico, botões de rotina
// da Alexa, sensores de tinta de impressora etc.) — filtra só pros domínios
// que fazem sentido controlar/ver de relance numa visão por área.
// Câmeras ficam de fora de propósito — já têm aba própria ("Câmeras").
const DOMINIOS_RELEVANTES = [
    "light", "switch", "climate", "cover", "fan",
    "media_player", "binary_sensor", "person", "lock", "vacuum",
];

export default function AreasView() {

    const { data: areas, isLoading } = useHomeAssistantAreas();

    if (isLoading) return <CircularProgress />;

    const areasComDispositivos = (areas || [])
        .map((area) => ({
            ...area,
            entities: area.entities
                .filter(({ entity_id }) => DOMINIOS_RELEVANTES.includes(entity_id.split(".")[0]))
                .map(({ entity_id, label }) => ({ entityId: entity_id, label })),
        }))
        .filter((area) => area.entities.length > 0);

    return (
        <Grid container spacing={2}>
            {areasComDispositivos.map((area) => (
                <Grid key={area.area_id} size={{ xs: 12, md: 6 }}>
                    <EntitiesStatusCard title={area.name} entities={area.entities} />
                </Grid>
            ))}
        </Grid>
    );
}
