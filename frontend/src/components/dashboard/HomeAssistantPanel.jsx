import {
    Card,
    CardContent,
    Typography,
    Chip
} from "@mui/material";

export default function HomeAssistantPanel({ homeassistant }) {

    if (!homeassistant) return null;

    return (

        <Card sx={{ mt: 3 }}>

            <CardContent>

                <Typography variant="h6">
                    Home Assistant
                </Typography>

                <Chip

                    sx={{ mt: 2 }}

                    color={
                        homeassistant.online
                            ? "success"
                            : "error"
                    }

                    label={
                        homeassistant.online
                            ? "Online"
                            : "Offline"
                    }

                />

            </CardContent>

        </Card>

    );

}
