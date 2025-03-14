import { useState, useRef, useEffect } from "react";
import { Play, Pause, RotateCcw, RotateCw, Maximize, Volume2, VolumeX } from "lucide-react";
import "./styles.css";

const Index = ({ videoUrl }) => {
    const videoRef = useRef(null);
    const containerRef = useRef(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [volume, setVolume] = useState(0.5);
    const [progress, setProgress] = useState(0);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [showControls, setShowControls] = useState(true);
    const timeoutRef = useRef(null);
    const [isSeeking, setIsSeeking] = useState(false);
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
    const [videoAspectRatio, setVideoAspectRatio] = useState(null);

    const handleSeek = (e) => {
        const progressBar = e.currentTarget;
        const rect = progressBar.getBoundingClientRect();
        const offsetX = e.clientX - rect.left;
        const newTime = (offsetX / rect.width) * videoRef.current.duration;
        videoRef.current.currentTime = newTime;
        setProgress((newTime / videoRef.current.duration) * 100);
    };

    useEffect(() => {
        const checkMobile = () => setIsMobile(window.innerWidth <= 768);
        window.addEventListener("resize", checkMobile);
        return () => window.removeEventListener("resize", checkMobile);
    }, []);

    useEffect(() => {
        const handleFullscreenChange = () => {
            if (document.fullscreenElement) {
                setIsFullscreen(true);
            } else {
                setIsFullscreen(false);
            }
        };

        document.addEventListener("fullscreenchange", handleFullscreenChange);

        return () => {
            document.removeEventListener("fullscreenchange", handleFullscreenChange);
        };
    }, []);

    const handleMouseDown = (e) => {
        setIsSeeking(true);
        handleSeek(e);
    };

    const handleMouseMove = (e) => {
        if (isSeeking) {
            handleSeek(e);
        }
    };

    const handleMouseUp = () => {
        setIsSeeking(false);
    };

    useEffect(() => {
        if (isSeeking) {
            window.addEventListener("mousemove", handleMouseMove);
            window.addEventListener("mouseup", handleMouseUp);
        } else {
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("mouseup", handleMouseUp);
        }

        return () => {
            window.removeEventListener("mousemove", handleMouseMove);
            window.removeEventListener("mouseup", handleMouseUp);
        };
    }, [isSeeking]);

    useEffect(() => {
        const handleMouseMove = () => {
            setShowControls(true);
            clearTimeout(timeoutRef.current);

            timeoutRef.current = setTimeout(() => setShowControls(false), 3000);
        };

        const videoContainer = videoRef.current?.parentElement;
        if (videoContainer) {
            videoContainer.addEventListener("mousemove", handleMouseMove);
        }

        return () => {
            if (videoContainer) {
                videoContainer.removeEventListener("mousemove", handleMouseMove);
            }
            clearTimeout(timeoutRef.current);
        };
    }, []);

    const togglePlay = () => {
        if (videoRef.current.paused) {
            videoRef.current.play();
            setIsPlaying(true);
        } else {
            videoRef.current.pause();
            setIsPlaying(false);
        }
    };

    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            if (containerRef.current.requestFullscreen) {
                containerRef.current.requestFullscreen();
            } else if (containerRef.current.webkitRequestFullscreen) {
                containerRef.current.webkitRequestFullscreen();
            } else if (containerRef.current.msRequestFullscreen) {
                containerRef.current.msRequestFullscreen();
            }
        } else {
            document.exitFullscreen();
        }
    };

    const handleVolumeChange = (e) => {
        setVolume(e.target.value);
        videoRef.current.volume = e.target.value;
    };

    const toggleMute = () => {
        if (volume > 0) {
            setVolume(0);
            videoRef.current.volume = 0;
        } else {
            setVolume(0.5);
            videoRef.current.volume = 0.5;
        }
    };

    const handleProgress = () => {
        setCurrentTime(videoRef.current.currentTime);
        setProgress((videoRef.current.currentTime / videoRef.current.duration) * 100);
    };

    const handleLoadedMetadata = () => {
        setDuration(videoRef.current.duration);
        const video = videoRef.current;
        const aspectRatio = video.videoWidth / video.videoHeight;
        setVideoAspectRatio(aspectRatio);
    };

    const formatTime = (time) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
    };

    return (
        <div
            ref={containerRef}
            className="relative w-full max-w-6xl mx-auto aspect-w-16 aspect-h-9 overflow-hidden rounded-xl shadow-lg"
            style={{
                width: isFullscreen ? "100vw" : "100%",
                height: isFullscreen ? "100vh" : "auto",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                backgroundColor: "black", // Background for fullscreen
            }}
        >
            <video
                ref={videoRef}
                src={videoUrl}
                className="w-full h-full object-contain" // Use object-contain to fit the video within the container
                onTimeUpdate={handleProgress}
                onLoadedMetadata={handleLoadedMetadata}
                controls={false}
            ></video>

            {/* Video Controls Overlay */}
            <div
                className={`absolute inset-0 transition-opacity duration-500 flex flex-col justify-between ${
                    showControls ? "opacity-100" : "opacity-0"
                }`}
                style={{ zIndex: isFullscreen ? 1000 : 1 }}
            >
                {/* Fullscreen Button */}
                <button
                    onClick={toggleFullscreen}
                    className="absolute top-4 left-4 text-white pointer-events-auto p-2 sm:p-3"
                >
                    <Maximize size={20} className="sm:size-7" />
                </button>

                {/* Volume Control */}
                <div className="absolute top-4 right-4 flex items-center gap-2">
                    <button onClick={toggleMute} className="text-white p-2 sm:p-3">
                        {volume > 0 ? <Volume2 size={24} /> : <VolumeX size={24} />}
                    </button>
                    <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={volume}
                        onChange={handleVolumeChange}
                        className="w-20 sm:w-24 appearance-none h-4 rounded-lg bg-white outline-none hidden sm:block"
                        style={{
                            WebkitAppearance: "none",
                            appearance: "none",
                            background: `linear-gradient(to right, #fff ${volume * 100}%, #444 ${volume * 100}%)`,
                        }}
                    />
                </div>

                {/* Centered Overlay UI */}
                <div className="absolute inset-0 flex items-center justify-center gap-4 pointer-events-none">
                    <button
                        onClick={() => (videoRef.current.currentTime -= 10)}
                        className="text-white p-4 pointer-events-auto text-lg sm:text-2xl"
                    >
                        <RotateCcw size={28} />
                    </button>
                    <button
                        onClick={togglePlay}
                        className="text-white p-4 pointer-events-auto text-lg sm:text-2xl"
                    >
                        {isPlaying ? <Pause size={32} /> : <Play size={32} />}
                    </button>
                    <button
                        onClick={() => (videoRef.current.currentTime += 10)}
                        className="text-white p-4 pointer-events-auto text-lg sm:text-2xl"
                    >
                        <RotateCw size={28} />
                    </button>
                </div>

                {/* Video Progress & Time */}
                <div className="absolute bottom-0 left-0 right-0 p-3 sm:p-4 bg-gradient-to-t transition-opacity duration-500">
                    <div className="text-white font-poppins text-sm sm:text-base">Example Video</div>
                    <div
                        className="relative w-full h-2 sm:h-3 bg-[#ffffff80] cursor-pointer mt-2 rounded-2xl z-10 overflow-hidden"
                        onMouseDown={handleMouseDown}
                    >
                        <div
                            className="absolute top-0 left-0 h-2 sm:h-3 bg-white"
                            style={{ width: `${progress}%`, borderRadius: "inherit" }}
                        ></div>
                    </div>
                    <div className="bottom-0 sm:p-3 text-white flex justify-between">
                        <span className="text-xs sm:text-sm">{formatTime(currentTime)}</span>
                        <span className="text-xs sm:text-sm">{formatTime(duration)}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Index;