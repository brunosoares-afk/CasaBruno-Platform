import { Card, CardContent, Typography } from "@mui/material";

export default function StatusCard({ title, value }) {
  return (
    <Card
      sx={{
        background: "#1e293b",
        color: "#fff",
        borderRadius: 3,
        height: "100%"
      }}
    >
      <CardContent>
        <Typography
          variant="subtitle2"
          color="gray"
        >
          {title}
        </Typography>

        <Typography
          variant="h4"
          sx={{ mt: 2 }}
        >
          {value}
        </Typography>
      </CardContent>
    </Card>
  );
}
