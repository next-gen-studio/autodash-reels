# SAFE AREA (IG/TikTok/YouTube Shorts UI): banner text, stickers and card stay inside y=230..1480 and x=90..890 (see SAFE_AREA.md).
# Per-video options (pick them to fit the video topic; see GUIDE.md rule 4):
#   --badge FILE    pop-in badge sticker (make it with make_badge.py), default sticker_new.png
#   --icon FILE     rising icon sticker, e.g. icons/fire.png, default sticker_spark.png
#   --sfx-start / --sfx-badge / --sfx-icon / --sfx-card FILE   sound effects from sfx/, defaults whoosh/whoosh/pop/pop
import subprocess,sys,json,argparse
ap=argparse.ArgumentParser();ap.add_argument('src');ap.add_argument('out')
ap.add_argument('--badge',default='sticker_new.png');ap.add_argument('--icon',default='sticker_spark.png')
ap.add_argument('--sfx-start',default='whoosh.wav');ap.add_argument('--sfx-badge',default='whoosh.wav')
ap.add_argument('--sfx-icon',default='pop.wav');ap.add_argument('--sfx-card',default='pop.wav')
A=ap.parse_args();src,out=A.src,A.out
D=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src]).decode())
D=round(D,2)
tc=0.15; tstar=round(min(D*0.45,6),2)
pulses=[1.2,tstar,round(D*0.5,2),tc]
z="1.03+0.03*sin(2*PI*t/9)+"+"+".join(f"if(gte(t,{p}),0.05*exp(-7*(t-{p})),0)" for p in pulses)
inputs=["-i",src]+sum([["-loop","1","-framerate","30","-t",str(D+1),"-i",f] for f in ["banner_tall.png",A.badge,A.icon,"lower.png"]],[])+["-i","music.wav","-i",A.sfx_start,"-i",A.sfx_badge,"-i",A.sfx_icon,"-i",A.sfx_card]
fc=[
 "[0:v]fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,eq=contrast=1.06:saturation=1.18,vignette=PI/5,fade=t=in:d=0.2[z]",
 "[1:v]format=rgba[ban]","[2:v]format=rgba[nw]",
 f"[3:v]format=rgba,scale=w=-2:h='max(4,230*pow(min(1,max(0,t-{tstar})/0.25),0.7))':eval=frame[st]","[4:v]format=rgba,scale=780:-2[cd]",
 "[z][ban]overlay=x=0:y=235:shortest=1[v1]",
 f"[v1][nw]overlay=x=600:y='500+330*exp(-9*(t-1.2))*cos(14*(t-1.2))+6*sin(8*t)':enable='between(t,1.2,3.2)'[v2]",
 f"[v2][st]overlay=x='120-w/2+90':y='1020-(t-{tstar})*40-h/2':enable='between(t,{tstar},{tstar+2.4})'[v3]",
 f"[v3][cd]overlay=x=90:y='1310+620*exp(-12*(t-{tc}))':enable='gte(t,{tc})'[v4]",
 f"color=c=0x00E5FF:s=1080x14:r=30:d={D+1}[bar]",
 f"[v4][bar]overlay=x='-W+W*t/{D}':y=H-14:shortest=1[v]",
 f"[0:a]aresample=48000,volume=1.0[a0]",
 f"[5:a]atrim=0:{D},afade=t=in:d=0.5,afade=t=out:st={D-1.5}:d=1.5,volume=0.12[mu]",
 "[6:a]aresample=48000,adelay=30|30,volume=0.8[wa]",
 f"[7:a]aresample=48000,adelay=1200|1200,volume=0.8[wb]",
 f"[8:a]aresample=48000,adelay={int(tstar*1000)}|{int(tstar*1000)},volume=0.8[pa]",
 f"[9:a]aresample=48000,adelay={int(tc*1000)}|{int(tc*1000)},volume=0.8[pb]",
 f"[a0][mu][wa][wb][pa][pb]amix=inputs=6:duration=first:normalize=0,alimiter=limit=0.95[a]"]
cmd=["ffmpeg","-v","error","-y"]+inputs+["-filter_complex",";".join(fc),"-map","[v]","-map","[a]","-t",str(D),"-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","160k","body.mp4"]
r=subprocess.run(cmd,capture_output=True,text=True); print(r.stderr[-1200:])
off=round(D-0.35,2)
cmd2=["ffmpeg","-v","error","-y","-i","body.mp4","-i","ad.mp4","-filter_complex",
 f"[0:v]fps=30,format=yuv420p[a];[1:v]fps=30,format=yuv420p[b];[a][b]xfade=transition=smoothleft:duration=0.35:offset={off}[v];[0:a]aresample=48000[a0];[1:a]aresample=48000[a1];[a0][a1]acrossfade=d=0.35[ao]",
 "-map","[v]","-map","[ao]","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",out]
r=subprocess.run(cmd2,capture_output=True,text=True); print(r.stderr[-800:])
