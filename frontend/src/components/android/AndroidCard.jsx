import { Card, CardContent, Typography, Chip, Stack } from "@mui/material";

import RemoteControl from "./RemoteControl";
import AppButtons from "./AppButtons";

export default function AndroidCard({ device }) {

    return (

        <Card sx={{ borderRadius: 4 }}>

            <CardContent>

                <Stack
                    direction="row"
                    justifyContent="space-between"
                    alignItems="center"
                    mb={2}
                >

                    <Typography variant="h6">
                        {device.name}
                    </Typography>

                    <Chip
                        color={device.status === "online" ? "success" : "error"}
                        label={device.status}
                    />

                </Stack>

                <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                >
                    {device.host}
                </Typography>

                <AppButtons device={device.id} />

                <RemoteControl device={device.id} />

            </CardContent>

        </Card>

    );

}
