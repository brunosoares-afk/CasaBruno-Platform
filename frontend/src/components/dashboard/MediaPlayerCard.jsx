import { Card, Box, Typography, IconButton } from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PauseIcon from "@mui/icons-material/Pause";

const COLOR = "primary";

export default function MediaPlayerCard({ entity, onPlayPause }) {

    if (!entity) return null;

    const attrs = entity.attributes || {};
    const isPlaying = entity.state === "playing";
    const canToggle = entity.state === "playing" || entity.state === "paused";
    const title = attrs.media_title || attrs.friendly_name || entity.entity_id;
    const artist = attrs.media_artist;

    return (

        <Card
            sx={(theme) => ({
                flex: 1,
                p: 2,
                display: "flex",
                alignItems: "center",
                gap: 2,
                border: "1px solid",
                borderColor: isPlaying ? `${COLOR}.main` : "rgba(255,255,255,.08)",
                boxShadow: isPlaying ? `0 0 18px -4px ${theme.palette[COLOR].main}` : "none",
                transition: "box-shadow .2s ease, border-color .2s ease",
            })}
        >

            <Box sx={{ minWidth: 0, flex: 1 }}>

                <Typography sx={{ fontSize: 12, color: "text.secondary", whiteSpace: "normal", wordBreak: "break-word" }}>
                    {attrs.friendly_name || entity.entity_id}
                </Typography>

                <Typography sx={{ fontSize: 14, fontWeight: 600, whiteSpace: "normal", wordBreak: "break-word" }}>
                    {title}
                </Typography>

                {artist && (
                    <Typography sx={{ fontSize: 12, color: "text.secondary", whiteSpace: "normal", wordBreak: "break-word" }}>
                        {artist}
                    </Typography>
                )}

            </Box>

            {canToggle && (
                <IconButton
                    onClick={onPlayPause}
                    sx={(theme) => ({
                        width: 42,
                        height: 42,
                        flexShrink: 0,
                        bgcolor: isPlaying ? `${COLOR}.main` : "rgba(255,255,255,.06)",
                        color: isPlaying ? "#fff" : "text.secondary",
                        boxShadow: isPlaying ? `0 0 14px -2px ${theme.palette[COLOR].main}` : "none",
                        transition: "all .2s ease",
                        "&:hover": { bgcolor: isPlaying ? `${COLOR}.dark` : "rgba(255,255,255,.12)" },
                    })}
                >
                    {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
                </IconButton>
            )}

        </Card>

    );

}
