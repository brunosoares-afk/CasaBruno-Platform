import {
    Card,
    CardContent,
    Typography,
    Chip,
    Stack
} from "@mui/material";

export default function DockerPanel({ docker }) {

    if (!docker) return null;

    return (

        <Card sx={{ mt: 3 }}>

            <CardContent>

                <Typography variant="h6" gutterBottom>
                    Docker
                </Typography>

                <Typography>

                    Containers ativos:
                    {" "}
                    {docker.running}
                    {" / "}
                    {docker.containers}

                </Typography>

                <Stack
                    direction="row"
                    spacing={1}
                    flexWrap="wrap"
                    sx={{ mt: 2 }}
                >

                    {docker.list.map(container => (

                        <Chip
                            key={container.id}
                            label={container.name}
                            color={
                                container.status === "running"
                                    ? "success"
                                    : "default"
                            }
                        />

                    ))}

                </Stack>

            </CardContent>

        </Card>

    );

}
