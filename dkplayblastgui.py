"""Maya GUI script that creates playblasts and sends completed frames directly to FFmpeg."""
import os
import subprocess
import tempfile

from maya import cmds


class DkPlayblastGUI():
    """Defines a GUI class."""

    def __init__(self):
        super().__init__()
        self.window = "root"
        self.title = "DK MayaPlayblast"
        self.size = (610, 400)

        FFMPEG_PATH = r'\\5d-server\PLUGINS\ffmpeg\bin\ffmpeg.exe'
        PATH_ENTRY_WIDTH = 500
        RANGE_ENTRY_WIDTH = 70

        BROWSE_WIDTH = 100
        PLAYBLAST_WIDTH = 100

        OPT_WIDTH = 140

        LAY_HEIGHT = 30
        SEP_STYLE = 'in'
        SEP_STYLE2 = 'single'
        VERTICAL_SEP_WIDTH = 15

        SLIDER_WIDTH = 140
        SLIDER_FRAME_WIDTH = SLIDER_WIDTH + 30

        FPS_OPT = [24, 25, 30, 48, 60, 120]

        self.CODECS = ['libx264', 'libx265']
        self.PRESET_VALS = ['ultrafast', 'superfast', 'veryfast', 'faster',
                            'fast', 'medium', 'slow', 'slower', 'veryslow']

        self.ENCODERS = ['libx264', 'libx265']
        self.LIBX264_CONTAINERS = ['mp4', 'mkv', 'avi', 'mov']
        self.LIBX265_CONTAINERS = ['hevc', 'mp4', 'mov', 'mkv']

        CRF_MIN = 16
        CRF_MAX = 28

        self.IMG_EXT = 'png'

        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size, i=False, s=0)
        self.window_frame = cmds.columnLayout(adj=True)

        self.ffmpeg_frame = cmds.rowLayout(p=self.window_frame, nc=2, height=LAY_HEIGHT)
        self.ffmpeg_entry = cmds.textField(p=self.ffmpeg_frame, w=PATH_ENTRY_WIDTH, tx=FFMPEG_PATH, ann='FFmpeg.exe path')
        self.ffmpeg_btn = cmds.button(p=self.ffmpeg_frame, l='Browse', w=BROWSE_WIDTH, c=self.ff_browse_callback)

        self.range_sep = cmds.separator(p=self.window_frame, st=SEP_STYLE)
        self.range_frame = cmds.rowLayout(p=self.window_frame, nc=9, h=LAY_HEIGHT)
        self.sframe_entry = cmds.textField(p=self.range_frame, w=RANGE_ENTRY_WIDTH, tx=int(cmds.playbackOptions(q=True, min=True)))
        self.sframe_label = cmds.text(p=self.range_frame, l=' Start Frame ')
        self.eframe_entry = cmds.textField(p=self.range_frame, w=RANGE_ENTRY_WIDTH, tx=int(cmds.playbackOptions(q=True, max=True)))
        self.sframe_label = cmds.text(p=self.range_frame, l=' End Frame ')

        self.fps_opt = cmds.optionMenuGrp(p=self.range_frame, el=' FPS ', w=OPT_WIDTH - 40)
        for f in FPS_OPT:
            cmds.menuItem(f)
        cmds.optionMenuGrp(self.fps_opt, e=True, v='60')

        self.ornaments_sep = cmds.separator(p=self.range_frame, st=SEP_STYLE2, hr=0, w=VERTICAL_SEP_WIDTH, h=LAY_HEIGHT-5)
        self.ornaments_check = cmds.checkBox(p=self.range_frame, l='Ornaments', v=False)
        self.cleanup_check = cmds.checkBox(p=self.range_frame, l='Cleanup', v=True)

        self.options_sep = cmds.separator(p=self.window_frame, st=SEP_STYLE)
        self.options_frame = cmds.rowColumnLayout(p=self.window_frame, nc=8)

        self.codec_frame = cmds.rowLayout(p=self.options_frame, nc=1, w=OPT_WIDTH)
        self.codec_opt = cmds.optionMenuGrp(p=self.codec_frame, el=' Codec', cc=self.codecs_opt_callback)
        for e in self.ENCODERS:
            cmds.menuItem(e)

        self.presets_sep = cmds.separator(p=self.options_frame, hr=0, st=SEP_STYLE2, w=VERTICAL_SEP_WIDTH)
        self.presets_frame = cmds.rowLayout(p=self.options_frame, nc=1, w=OPT_WIDTH)
        self.presets_opt = cmds.optionMenuGrp(p=self.presets_frame, el=' Preset')
        for p in self.PRESET_VALS:
            cmds.menuItem(p)
        cmds.optionMenuGrp(self.presets_opt, e=True, v='medium')

        self.crf_sep = cmds.separator(p=self.options_frame, hr=0, st=SEP_STYLE2, w=VERTICAL_SEP_WIDTH)
        self.crf_frame = cmds.rowLayout(p=self.options_frame, nc=2, w=SLIDER_FRAME_WIDTH)
        self.crf_slider = cmds.intSliderGrp(p=self.crf_frame, el=' CRF', min=CRF_MIN, max=CRF_MAX, s=(CRF_MAX-CRF_MIN), w=SLIDER_WIDTH, v=23, dc=self.crf_slider_callback)
        self.crf_val = cmds.text(p=self.crf_frame, l=cmds.intSliderGrp(self.crf_slider, q=True, v=True))

        self.container_sep = cmds.separator(p=self.options_frame, hr=0, st=SEP_STYLE2, w=VERTICAL_SEP_WIDTH)
        self.container_frame = cmds.rowLayout(p=self.options_frame, nc=1, w=OPT_WIDTH)
        self.container_opt = cmds.optionMenuGrp(p=self.container_frame, el='', cc=self.container_callback)
        for c in self.LIBX264_CONTAINERS:
            cmds.menuItem(c)

        self.output_frame = cmds.rowLayout(p=self.window_frame, nc=3, h=LAY_HEIGHT)
        self.output_sep = cmds.separator(p=self.output_frame)
        self.output_entry = cmds.textField(p=self.output_frame, w=PATH_ENTRY_WIDTH, ann='Output path', ed=False)
        self.output_browse = cmds.button(p=self.output_frame, l='Browse', w=BROWSE_WIDTH, c=self.out_browse_callback)

        self.pblast_sep = cmds.separator(p=self.window_frame, st=SEP_STYLE)
        self.pblast_frame = cmds.columnLayout(p=self.window_frame, adj=True, h=LAY_HEIGHT)
        self.pblast_btn = cmds.button(p=self.pblast_frame, l='Playblast', w=PLAYBLAST_WIDTH, bgc=[0.1, 0.5, 0.3], al='center', c=self.playblast_callback)

        self.log_sep = cmds.separator(p=self.window_frame, st=SEP_STYLE)
        self.log_frame = cmds.columnLayout(p=self.window_frame)

        self.log_label = cmds.text(p=self.log_frame, l='Log', height=20)
        self.log = cmds.scrollField(p=self.log_frame, w=600, ed=False)

        cmds.showWindow()

    def ff_browse_callback(self, val):
        """Defines FFmpeg browse button behaviour."""
        result = cmds.fileDialog2(ds=2, fm=1)
        if result != "":
            cmds.textField(self.ffmpeg_entry, e=True, tx=result[0])

    def crf_slider_callback(self, val):
        """Defines CRF slider behaviour."""
        cmds.text(self.crf_val, e=True, l=val)

    def codecs_opt_callback(self, val):
        """Defines codecs optionsmenu behaviour."""
        if val == "libx264":
            cmds.optionMenuGrp(self.container_opt, e=True, dai=True)
            for c in self.LIBX264_CONTAINERS:
                cmds.menuItem(c)
        if val == "libx265":
            cmds.optionMenuGrp(self.container_opt, e=True, dai=True)
            for c in self.LIBX265_CONTAINERS:
                cmds.menuItem(c)
            filename = cmds.textField(self.output_entry, q=True, tx=True)
            if filename != "":
                filename = f"{os.path.splitext(filename)[0]}.{cmds.optionMenuGrp(self.container_opt, q=True, v=True)}"
                cmds.textField(self.output_entry, e=True, tx=filename)

    def container_callback(self, val):
        """Defines container optionsmenu behaviour."""
        filename = cmds.textField(self.output_entry, q=True, tx=True)
        if filename != "":
            filename = f"{os.path.splitext(filename)[0]}.{val}"
            cmds.textField(self.output_entry, e=True, tx=filename)

    def out_browse_callback(self, val):
        """Defines output path button behaviour."""
        result = cmds.fileDialog2(ff=f"{cmds.optionMenuGrp(self.container_opt, q=True, v=True)}", fm=0, ds=2)
        if result != "":
            cmds.textField(self.output_entry, e=True, tx=result[0])

    def playblast_callback(self, val):
        """Defines playblast button behaviour."""
        #Checks path.
        ff_path = os.path.normpath(cmds.textField(self.ffmpeg_entry, q=True, tx=True))
        if not os.path.isfile(ff_path):
            cmds.scrollField(self.log, e=True, tx=f"Deadline not found at: '{ff_path}'.")
            return

        #Checks frames.
        sframe = cmds.textField(self.sframe_entry, q=True, tx=True)
        eframe = cmds.textField(self.eframe_entry, q=True, tx=True)
        padding = len(str(eframe))
        if int(sframe) > int(eframe):
            cmds.scrollField(self.log, e=True, tx="Start Frame must be smaller than End Frame.")
            return

        #Checks output.
        output_entry = cmds.textField(self.output_entry, q=True, tx=True)
        if output_entry == "":
            cmds.scrollField(self.log, e=True, tx="Please choose an output filepath.")
            return
        container = cmds.optionMenuGrp(self.container_opt, q=True, v=True)
        if not output_entry.endswith(container):
            output_entry = f"{os.path.splitext(output_entry)[0]}.{container}"
            cmds.textField(self.output_entry, e=True, tx=output_entry)        
        #Get ornaments state.
        ornaments = cmds.checkBox(self.ornaments_check, q=True, v=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Temp dir path: {temp_dir}")
            playblast_out = (os.path.join(temp_dir, os.path.splitext(os.path.basename(output_entry))[0]))
            cmds.playblast(cc=True, c=self.IMG_EXT, fo=True, fmt='image', st=sframe, et=eframe, f=playblast_out, fp=padding, orn=ornaments, v=False, p=100)
            self.format_ffmpeg(ff_path, temp_dir)

    def format_ffmpeg(self, ff_path, directory):
        """Transforms arguments into ffmpeg command."""

        #writes a .txt list of files
        filelist = os.path.join(directory, "ffmpeg_input.txt")
        with open(filelist, "wb") as outfile:
            for file in os.listdir(directory):
                if file.endswith(self.IMG_EXT):
                    print(file)
                    outfile.write(f"file '{os.path.normpath(file)}'\n".encode())
        print(f"ffmpeg_input.txt path: {filelist}")

        #Get gui vars related to ffmpeg.
        fps = cmds.optionMenuGrp(self.fps_opt, q=True, v=True)
        encoder = cmds.optionMenuGrp(self.codec_opt, q=True, v=True)
        crf = cmds.intSliderGrp(self.crf_slider, q=True, v=True)
        preset = cmds.optionMenuGrp(self.presets_opt, q=True, v=True)
        out = os.path.normpath(cmds.textField(self.output_entry, q=True, tx=True))

        #Log command and submit to ffmpeg.
        # cmd = f"{ff_path} -y -r {fps} -f concat -safe 0 -i {filelist} -framerate {fps} -pix_fmt yuv420p -c:v {encoder} -crf {crf} -preset {preset} \"{out}\""
        cmd = f"{ff_path} -y -r {fps} -f concat -safe 0 -i {filelist} -framerate {fps} -c:v {encoder} -vf \"pad=ceil(iw/2)*2:ceil(ih/2)*2\" -crf {crf} -preset {preset} -pix_fmt yuv420p \"{out}\""
        print(f"FFmpeg command: {cmd}")
        cmds.scrollField(self.log, e=True, cl=True)
        cmds.scrollField(self.log, e=True, it=f"{cmd}\n\n")
        result = self.submit_ffmpeg(cmd)

        #Log results.
        cmds.scrollField(self.log, e=True, it=f"{result[1]}\n")
        if os.path.isfile(out):
            cmds.scrollField(self.log, e=True, it=f"Succesfully created:\n '{out}'\n")

    def submit_ffmpeg(self, ffmpeg_command):
        """Submits a constructed command to ffmpeg by subprocess."""

        p = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stdout.decode(), stderr.decode()


if __name__ == "__main__":
    app = DkPlayblastGUI()
