# Ultralytics Yolo v8 helper scripts

## Introduction
In order to facilitate the use of Yolo v8, I have created a number of helper scripts to make the process of training, testing and using models easier.  
These scripts are designed to be used with the Yolo v8 repository, which can be found [here](https://github.com/ultralytics/ultralytics).

## Installation
First of all, install torch (pytorch) and torchvision that are compatible with your system.  
Then, use `requirements.txt` to install the remaining dependencies.
Then, install ffmpeg.

## Usage
The scripts are designed to be used from the command line or used to create your own scripts.
### Stream live to YouTube (or any other platform using rmtp) the recognition of objects in a video
`stream_live_youtube.py` is a script that allows you to stream live to YouTube the recognition of objects in a video.  
It can be used in order to easily integrate your recognition system and display the results in real time.  
It can be useful on Ubuntu Server that has no graphical interface.  

Streaming to YouTube is done by rtmp with the use of ffmpeg.
```bash
sudo python3 stream_live_youtube.py --model yolov8n.pt --url "rtmp://a.rtmp.youtube.com/live2" --key "xxxx-xxxx-xxxx-xxxx-xxxx" --width 640 --height 480
```

In order to run in the background:
```bash
nohup sudo python3 stream_live_youtube.py --model yolov8n.pt --url "rtmp://a.rtmp.youtube.com/live2" --key "xxxx-xxxx-xxxx-xxxx-xxxx" --width 640 --height 480 >res.out 2>&1 &
echo $! > stream_live_youtube_pid.txt
```
Or use ` > /dev/null` not to save output.  

Stop:
```bash
sudo kill -9 `cat stream_live_youtube_pid.txt`
sudo rm stream_live_youtube_pid.txt
```
How to get url and key:  
[Streaming to YouTube via RTMP](https://stageten.tv/support/streaming-to-youtube-via-rtmp-1)  
Url is new for every stream.  

## Attention!
If you encounter any errors, try:
- running program as sudo
- use another console (not the one built in Pycharm, etc.)
- use VPN if rtmp is blocked in your network
- check ffmpeg arguments for streaming (they can depend on use case)