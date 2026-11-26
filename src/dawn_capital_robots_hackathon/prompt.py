from .extract_frames import FRAME_STEP

PROMPT = f"""\
You are given every {FRAME_STEP}th frame sampled from a video of a plug being plugged into a socket. \
Review all frames together and evaluate three tests independently.

1. stable_camera: The camera is not shaky and keeps a fixed angle for the whole video. \
Pass only if the framing, viewpoint and background stay the same across all frames \
(no panning, tilting, zooming or repositioning) and no frame shows camera-shake motion blur.

2. plug_and_socket_visible: Both the plug and the socket are clearly visible. \
Pass only if both are in frame, in focus, well lit and not blocked (e.g. by a hand) \
in enough frames to follow the plug going into the socket.

3. privacy_safe: No frame shows information that could identify a person. \
Fail if ANY frame shows a face or any recognisable part of one (including partial, profile or reflected faces), \
readable personal text (names, addresses, documents, mail, name tags, screens), \
a photo or screen showing a person, or a distinctive tattoo, scar or birthmark that is clearly visible. \
Ordinary hands, arms, clothing and plain jewellery are fine, and so is printed text on clothing or products \
(slogans, brand names) unless it names a person. One frame is enough to fail. \
List every issue with the t value from that frame's label and a short description; \
leave the list empty when nothing is found.

For each test, first write a short reason based on what you observe in the frames, \
then give the verdict passed=true or false that follows from that reason.
"""
