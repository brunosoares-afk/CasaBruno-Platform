import { useEffect, useState } from "react";
import { Card, Box, Typography, IconButton, Slider } from "@mui/material";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PauseIcon from "@mui/icons-material/Pause";
import SkipPreviousIcon from "@mui/icons-material/SkipPrevious";
import SkipNextIcon from "@mui/icons-material/SkipNext";
import VolumeUpIcon from "@mui/icons-material/VolumeUp";
import VolumeOffIcon from "@mui/icons-material/VolumeOff";
import MusicNoteIcon from "@mui/icons-material/MusicNote";
import { entityPictureUrl } from "../../api/homeassistantService";

const COLOR = "primary";

export default function MediaPlayerCard({ entity, onPlayPause, onNext, onPrevious, onVolumeChange }) {

    const attrs = entity?.attributes || {};
    const isPlaying = entity?.state === "playing";
    const canToggle = entity?.state === "playing" || entity?.state === "paused";
    const title = attrs.media_title || attrs.friendly_name || entity?.entity_id;
    const artist = attrs.media_artist;
    const supportedVolume = typeof attrs.volume_level === "number";
    const picture = attrs.entity_picture ? entityPictureUrl(entity.entity_id) : null;

    const [localVolume, setLocalVolume] = useState(attrs.volume_level ?? 0);
    const [pictureFailed, setPictureFailed] = useState(false);

    useEffect(() => {
        if (supportedVolume) setLocalVolume(attrs.volume_level);
    }, [attrs.volume_level, supportedVolume]);

    useEffect(() => {
        setPictureFailed(false);
    }, [picture]);

    if (!entity) return null;

    const showPicture = picture && !pictureFailed;

    return (

        <Card
            sx={(theme) => ({
                flex: 1,
                p: 2,
                position: "relative",
                overflow: "hidden",
                border: "1px solid",
                borderColor: isPlaying ? `${COLOR}.main` : "rgba(255,255,255,.08)",
                boxShadow: isPlaying ? `0 0 18px -4px ${theme.palette[COLOR].main}` : "none",
                transition: "box-shadow .2s ease, border-color .2s ease",
            })}
        >

            {/* Fundo com a própria capa borrada, só um clima ambiente por trás */}
            {showPicture && (
                <Box
                    sx={{
                        position: "absolute",
                        inset: 0,
                        backgroundImage: `url(${picture})`,
                        backgroundSize: "cover",
                        backgroundPosition: "center",
                        filter: "blur(24px) brightness(0.35) saturate(1.4)",
                        transform: "scale(1.3)",
                        opacity: isPlaying ? 1 : 0.5,
                        transition: "opacity .3s ease",
                    }}
                />
            )}

            <Box sx={{ position: "relative", display: "flex", alignItems: "center", gap: 1.5 }}>

                <Box
                    sx={{
                        width: 56,
                        height: 56,
                        borderRadius: 2,
                        flexShrink: 0,
                        overflow: "hidden",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        bgcolor: "rgba(255,255,255,.06)",
                        boxShadow: showPicture && isPlaying ? `0 0 16px -2px ${COLOR === "primary" ? "rgba(90,140,255,.6)" : "rgba(255,255,255,.4)"}` : "none",
                    }}
                >
                    {showPicture ? (
                        <Box
                            component="img"
                            src={picture}
                            onError={() => setPictureFailed(true)}
                            sx={{ width: "100%", height: "100%", objectFit: "cover" }}
                        />
                    ) : (
                        <MusicNoteIcon sx={{ color: "text.secondary", fontSize: 26 }} />
                    )}
                </Box>

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
                    <Box sx={{ display: "flex", alignItems: "center", gap: 0.5, flexShrink: 0 }}>

                        {onPrevious && (
                            <IconButton size="small" onClick={onPrevious} sx={{ color: "text.secondary" }}>
                                <SkipPreviousIcon />
                            </IconButton>
                        )}

                        <IconButton
                            onClick={onPlayPause}
                            sx={(theme) => ({
                                width: 42,
                                height: 42,
                                bgcolor: isPlaying ? `${COLOR}.main` : "rgba(255,255,255,.06)",
                                color: isPlaying ? "#fff" : "text.secondary",
                                boxShadow: isPlaying ? `0 0 14px -2px ${theme.palette[COLOR].main}` : "none",
                                transition: "all .2s ease",
                                "&:hover": { bgcolor: isPlaying ? `${COLOR}.dark` : "rgba(255,255,255,.12)" },
                            })}
                        >
                            {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
                        </IconButton>

                        {onNext && (
                            <IconButton size="small" onClick={onNext} sx={{ color: "text.secondary" }}>
                                <SkipNextIcon />
                            </IconButton>
                        )}

                    </Box>
                )}

            </Box>

            {supportedVolume && onVolumeChange && (
                <Box sx={{ position: "relative", display: "flex", alignItems: "center", gap: 1, mt: 1.5 }}>
                    {localVolume > 0
                        ? <VolumeUpIcon sx={{ fontSize: 18, color: "text.secondary" }} />
                        : <VolumeOffIcon sx={{ fontSize: 18, color: "text.secondary" }} />}
                    <Slider
                        size="small"
                        min={0}
                        max={1}
                        step={0.05}
                        value={localVolume}
                        onChange={(_, v) => setLocalVolume(v)}
                        onChangeCommitted={(_, v) => onVolumeChange(v)}
                        color={COLOR}
                        sx={{ mx: 0.5 }}
                    />
                </Box>
            )}

        </Card>

    );

}
