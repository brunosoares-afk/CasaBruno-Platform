import { Grid, Box } from "@mui/material";
import TvIcon from "@mui/icons-material/Tv";
import VideocamIcon from "@mui/icons-material/Videocam";
import HomeIcon from "@mui/icons-material/Home";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import SmartDisplayIcon from "@mui/icons-material/SmartDisplay";
import AcUnitIcon from "@mui/icons-material/AcUnit";
import CloseIcon from "@mui/icons-material/Close";
import SensorDoorIcon from "@mui/icons-material/SensorDoor";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import VolumeDownIcon from "@mui/icons-material/VolumeDown";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";

import EntitiesStatusCard from "../widgets/EntitiesStatusCard";
import ActionButtonGrid from "../widgets/ActionButtonGrid";

const STATUS_GERAL = [
    { entityId: "person.casa_inteligente", label: "Bruno" },
    { entityId: "person.taiane", label: "Taiane" },
    { entityId: "person.heitor", label: "Heitor" },
    { entityId: "sensor.icsee_pessoa_reconhecida", label: "Reconhecido pela câmera" },
    { entityId: "switch.portao_casa_switch_1", label: "Portão" },
    { entityId: "media_player.bruno_s_n65b", label: "TV" },
    { entityId: "media_player.alexa_taiane", label: "Alexa Taiane" },
];

const ILUMINACAO = [
    { entityId: "switch.lampada_cozinha_switch_1", label: "Lâmpada Cozinha" },
];

const ACESSOS = [
    {
        label: "Portão Casa (Pulso)",
        icon: <SensorDoorIcon fontSize="small" />,
        domain: "switch",
        service: "turn_on",
        entityId: "switch.portao_casa_switch_1",
    },
];

const CONTROLES = [
    { label: "TV Power", icon: <TvIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_tv_power" },
    { label: "BTV13 Power", icon: <SmartDisplayIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_btv13_power" },
    { label: "BTV13 Home", icon: <HomeIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_btv13_home" },
    { label: "BTV13 Voltar", icon: <ArrowBackIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_btv13_back" },
    { label: "Projetor Power", icon: <VideocamIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_projector_power" },
    { label: "Projetor Home", icon: <HomeIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_projector_home" },
    { label: "Projetor Voltar", icon: <ArrowBackIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_projector_back" },
    { label: "Ar Ligar", icon: <AcUnitIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_air_on" },
    { label: "Ar Desligar", icon: <CloseIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_air_off" },
    { label: "TV Philips Ligar", icon: <TvIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_tv_philips_power" },
    { label: "TV Philips Desligar", icon: <CloseIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_tv_philips_power_off" },
    { label: "TV Philips Vol +", icon: <VolumeUpIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_tv_philips_volume_up" },
    { label: "TV Philips Vol -", icon: <VolumeDownIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_tv_philips_volume_down" },
    { label: "TV Philips Mudo", icon: <VolumeOffIcon fontSize="small" />, domain: "script", service: "turn_on", entityId: "script.fred_tv_philips_mute" },
];

const DETECCAO_FACIAL = [
    { entityId: "binary_sensor.icsee_rosto_detectado", label: "Rosto detectado" },
    { entityId: "sensor.icsee_rostos_detectados", label: "Quantidade de rostos" },
];

export default function EquipamentosView() {

    return (
        <Grid container spacing={2}>

            <Grid size={{ xs: 12 }}>
                <ActionButtonGrid title="Controles" actions={CONTROLES} columns={3} color="warning" />
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
                <EntitiesStatusCard title="Status Geral" entities={STATUS_GERAL} />
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
                <EntitiesStatusCard title="Detecção Facial" entities={DETECCAO_FACIAL} color="error" />
            </Grid>

            <Grid size={{ xs: 12, md: 4 }}>
                <EntitiesStatusCard title="Iluminação" entities={ILUMINACAO} color="warning" />
                <Box sx={{ mt: 2 }}>
                    <ActionButtonGrid title="Acessos" actions={ACESSOS} columns={1} color="info" />
                </Box>
            </Grid>

        </Grid>
    );
}
