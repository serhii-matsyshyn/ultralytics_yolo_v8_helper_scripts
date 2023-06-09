import argparse
import subprocess

import cv2
import supervision as sv
from ultralytics import YOLO


class YouTubeVideoStreamer:
    def __init__(self, url, key, width=640, height=480):
        self.url = url
        self.key = key
        self.width = width
        self.height = height
        self.writer = None

    def start_streaming(self):
        command = ['ffmpeg',
                   '-use_wallclock_as_timestamps', '1',  ###
                   '-y',  # overwrite output file if it exists
                   '-f', 'rawvideo',
                   '-vcodec', 'rawvideo',
                   '-pixel_format', 'bgr24',
                   '-s', "{}x{}".format(self.width, self.height),
                   '-re',  # Fix 2
                   # '-r', str(20),

                   '-i', '-',  # input comes from a pipe
                   '-vsync', 'cfr',  # Fix
                   '-r', '25',  # Fix
                   # '-re',
                   '-f', 'lavfi',  # <<< YouTube Live requires a audio stream
                   '-i', 'anullsrc',  # <<< YouTube Live requires a audio stream
                   '-c:v', 'libx264',
                   '-c:a', 'aac',  # <<< YouTube Live requires a audio stream
                   # '-x264opts', "keyint=40:min-keyint=40:no-scenecut",
                   "-crf", "24",
                   '-pix_fmt', 'yuv420p',
                   '-preset', 'medium',
                   '-f', 'flv',
                   f'{self.url}/{self.key}']

        self.writer = subprocess.Popen(command, stdin=subprocess.PIPE)

    def stream_frame(self, frame):
        self.writer.stdin.write(frame.tobytes())

    def stop_streaming(self):
        self.writer.stdin.close()
        self.writer.wait()


class AiStreamer:
    def __init__(self, model_filename, url, key, width=640, height=480, external_streamer=None, debug=False):
        self.model_filename = model_filename
        self.url = url
        self.key = key
        self.width = width
        self.height = height
        self.debug = debug

        if external_streamer is None:
            external_streamer = YouTubeVideoStreamer

        self.model = YOLO(self.model_filename)
        self.box_annotator = sv.BoxAnnotator(
            thickness=1,
            text_thickness=2,
            text_scale=1
        )

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self.streamer = external_streamer(url=url, key=key, width=width, height=height)
        self.streamer.start_streaming()

    def stream_frame(self, frame):
        result = self.model(frame, agnostic_nms=True,
                            verbose=False,
                            batch=1)[0]
        detections = sv.Detections.from_yolov8(result)
        labels = [
            f"{self.model.model.names[class_id]} {confidence:0.2f}"
            for _, confidence, class_id, _
            in detections
        ]
        frame = self.box_annotator.annotate(
            scene=frame,
            detections=detections,
            labels=labels
        )

        fps = 1000 / (result.speed['preprocess'] + result.speed['inference'] + result.speed['postprocess'])

        # add additional text to video
        text = f"FPS: {fps:.2f}, Pr: {result.speed['preprocess']:.2f}ms, In: {result.speed['inference']:.2f}ms, Post: {result.speed['postprocess']:.2f}ms"
        cv2.putText(frame, text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

        self.streamer.stream_frame(frame)
        if self.debug:
            cv2.imshow("yolov8", frame)

    def stop_streaming(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.streamer.stop_streaming()

    def main(self):
        while True:
            ret, frame = self.cap.read()
            self.stream_frame(frame)

            if cv2.waitKey(30) == 27:  # break with escape key
                break

        self.stop_streaming()


class ArgumentsParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--model', type=str, default='yolov8n.pt', help='model path')
        self.parser.add_argument('--url', type=str, default='rtmp://a.rtmp.youtube.com/live2', help='streaming url')
        self.parser.add_argument('--key', type=str, default='xxxx-xxxx-xxxx-xxxx-xxxx', help='streaming key')
        self.parser.add_argument('--width', type=int, default=640, help='streaming width')
        self.parser.add_argument('--height', type=int, default=480, help='streaming height')

    def parse(self):
        return self.parser.parse_args()


if __name__ == "__main__":
    # debug
    # streamer_ai = AiStreamer(model_filename="yolov8n.pt",
    #                          url='rtmp://a.rtmp.youtube.com/live2',
    #                          key='xxxx-xxxx-xxxx-xxxx-xxxx',
    #                          width=640, height=480, external_streamer=YouTubeVideoStreamer,
    #                          debug=True)
    # streamer_ai.main()

    # production
    args = ArgumentsParser().parse()
    streamer_ai = AiStreamer(model_filename=args.model,
                             url=args.url,
                             key=args.key,
                             width=args.width, height=args.height,
                             external_streamer=YouTubeVideoStreamer)
    streamer_ai.main()
