import cv2


def rescale_frame(frame_input, percent=10):
    width = int(frame_input.shape[1] * percent / 100)
    height = int(frame_input.shape[0] * percent / 100)

    dim = (width, height)

    return cv2.resize(frame_input, dim, interpolation=cv2.INTER_AREA)
