ffmpeg -r 15 -f image2 -s 600x600 -i video/screen_%04d.png -vcodec libx264 -crf 25  video.mp4
