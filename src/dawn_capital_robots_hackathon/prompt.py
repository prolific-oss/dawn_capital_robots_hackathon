from .extract_frames import FRAME_STEP

PROMPT = f"""\
You are given every {FRAME_STEP}th frame sampled from a video of a plug being plugged into a socket. \
Review all frames together and evaluate two tests independently.

1. stable_camera: The camera is not shaky and keeps a fixed angle for the whole video. \
Pass only if the framing, viewpoint and background stay the same across all frames \
(no panning, tilting, zooming or repositioning) and no frame shows camera-shake motion blur.

2. plug_and_socket_visible: Both the plug and the socket are clearly visible. \
Pass only if both are in frame, in focus, well lit and not blocked (e.g. by a hand) \
in enough frames to follow the plug going into the socket.

For each test, first write a short reason based on what you observe in the frames, \
then give the verdict passed=true or false that follows from that reason.
"""
