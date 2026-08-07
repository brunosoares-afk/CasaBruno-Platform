import { Card, CardContent, Typography } from "@mui/material";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

export default function GaugeCard({ title, value }) {
  const percentage = Number(value) || 0;

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
          variant="subtitle1"
          gutterBottom
        >
          {title}
        </Typography>

        <div style={{ width: 130, margin: "auto" }}>
          <CircularProgressbar
            value={percentage}
            text={`${percentage}%`}
            styles={buildStyles({
              pathColor: "#22c55e",
              textColor: "#ffffff",
              trailColor: "#374151"
            })}
          />
        </div>

      </CardContent>
    </Card>
  );
}
