"""Make a 9:16 Story image and a 9:16 Reel video from one post image.
Usage: python3 make_vertical.py <input.jpg> <out_dir> <basename>
Writes <basename>_Story.jpg (1080x1920) and <basename>_Reel.mp4 (1080x1920, 9 s slow zoom, silent audio track).
"""
import sys, subprocess, os
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
src, out, base = sys.argv[1], sys.argv[2], sys.argv[3]
W, H = 1080, 1920
im = ImageOps.exif_transpose(Image.open(src)).convert('RGB')
# blurred fill background
s = max(W / im.width, H / im.height)
bg = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.6)
# sharp image centered, full width
f = W / im.width
fg = im.resize((W, int(im.height * f)), Image.LANCZOS)
if fg.height > H:
    fg = fg.crop((0, (fg.height - H) // 2, W, (fg.height - H) // 2 + H))
bg.paste(fg, (0, (H - fg.height) // 2))
story = os.path.join(out, f'{base}_Story.jpg')
bg.save(story, quality=90, optimize=True, progressive=True)
reel = os.path.join(out, f'{base}_Reel.mp4')
frames = 270  # 9 s at 30 fps
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', story,
    '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
    '-vf', f"scale=2160:3840,zoompan=z='1+0.08*on/{frames}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps=30,format=yuv420p",
    '-t', '9', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-c:a', 'aac', '-b:a', '128k',
    '-shortest', '-movflags', '+faststart', reel], check=True)
print(story); print(reel)
