import { Grid } from "@mui/material";
import StatusCard from "../cards/StatusCard";

export default function SystemCards({ system }) {

    if (!system) return null;

    return (

        <Grid container spacing={3} sx={{ mb: 3 }}>

            <Grid size={{ xs: 12, md: 3 }}>
                <StatusCard
                    title="CPU"
                    value={`${system.cpu_percent}%`}
                />
            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>
                <StatusCard
                    title="Memória"
                    value={`${system.memory_percent}%`}
                />
            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>
                <StatusCard
                    title="Disco"
                    value={`${system.disk_percent}%`}
                />
            </Grid>

            <Grid size={{ xs: 12, md: 3 }}>
                <StatusCard
                    title="Hostname"
                    value={system.hostname}
                />
            </Grid>

        </Grid>

    );

}
