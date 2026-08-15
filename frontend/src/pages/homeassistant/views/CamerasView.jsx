import { Box } from "@mui/material";
import CameraCard from "../../../components/dashboard/CameraCard";

const CAMERA_ENTITIES = [
  { id: "camera.camera_icsee_frente", name: "Câmera Frente" },
  { id: "camera.192_168_2_80", name: "Câmera Externa" },
];

export default function CamerasView() {

  return (
    <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap" }}>
      {CAMERA_ENTITIES.map((cam) => (
        <Box key={cam.id} sx={{ flex: "1 1 320px" }}>
          <CameraCard entityId={cam.id} name={cam.name} />
        </Box>
      ))}
    </Box>
  );
}
