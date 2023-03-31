import maya.cmds as cmds

class MayaPlayblast(object):
    """Defines a GUI class."""
    def __init__(self):
        # super().__init__()
        self.window = "root"
        self.title = "DK MayaPlayblast"
        self.size = (610,400)
        
        PATH_ENTRY_WIDTH = 500
        FFMPEG_PATH = r'\\5d-server\PLUGINS\ffmpeg\ffmpeg.exe'
        F_ENTRY_WIDTH = 100
        BROWSE_WIDTH = 100
        PLAYBLAST_WIDTH = 100
        LAY_HEIGHT = 30
        OPT_WIDTH = 140
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

        CRF_MIN=16
        CRF_MAX=28

        if cmds.window(self.window, exists = True):
            cmds.deleteUI(self.window, window=True)

        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size)
        self.window_frame = cmds.columnLayout(adj=True)

        self.ffmpeg_frame = cmds.rowLayout(p=self.window_frame, nc=2, height = LAY_HEIGHT)
        self.ffmpeg_entry = cmds.textField(p=self.ffmpeg_frame, w=PATH_ENTRY_WIDTH, tx=FFMPEG_PATH, ann='FFmpeg.exe path')
        self.ffmpeg_btn = cmds.button(p=self.ffmpeg_frame, l='Browse', w=BROWSE_WIDTH, c=self.ff_browse_callback)
        
        self.range_sep = cmds.separator(p=self.window_frame, st=SEP_STYLE)
        self.range_frame = cmds.rowLayout(p=self.window_frame, nc=5, h=LAY_HEIGHT)
        self.sframe_entry = cmds.textField(p=self.range_frame, w=F_ENTRY_WIDTH, tx=int(cmds.playbackOptions(q=True,min=True)))
        self.sframe_label = cmds.text(p=self.range_frame, l=' Start Frame ')
        self.eframe_entry = cmds.textField(p=self.range_frame, w=F_ENTRY_WIDTH, tx=int(cmds.playbackOptions(q=True,max=True)))
        self.sframe_label = cmds.text(p=self.range_frame, l=' End Frame ')

        self.fps_opt = cmds.optionMenuGrp(p=self.range_frame, el=' FPS ', w=OPT_WIDTH)
        for f in FPS_OPT:
            cmds.menuItem(f)

        self.options_sep = cmds.separator(p=self.window_frame, st=SEP_STYLE)
        self.options_frame = cmds.rowColumnLayout(p=self.window_frame, nc=8)
        
        self.codec_frame = cmds.rowLayout(p=self.options_frame, nc=1, w=OPT_WIDTH)
        self.codec_opt = cmds.optionMenuGrp(p=self.codec_frame, el=' Codec', cc=self.codecs_opt_callback)
        for e in self.ENCODERS:
            cmds.menuItem(e)

        self.presets_sep=cmds.separator(p=self.options_frame, hr=0, st=SEP_STYLE2, w=VERTICAL_SEP_WIDTH)
        self.presets_frame = cmds.rowLayout(p=self.options_frame, nc=1, w=OPT_WIDTH)
        self.presets_opt = cmds.optionMenuGrp(p=self.presets_frame, el=' Preset')
        for p in self.PRESET_VALS:
            cmds.menuItem(p)
        cmds.optionMenuGrp(self.presets_opt, e=True, v='medium')

        self.crf_sep=cmds.separator(p=self.options_frame, hr=0, st=SEP_STYLE2, w=VERTICAL_SEP_WIDTH)
        self.crf_frame = cmds.rowLayout(p=self.options_frame, nc=2, w=SLIDER_FRAME_WIDTH)
        self.crf_slider = cmds.intSliderGrp(p=self.crf_frame, el=' CRF', min=CRF_MIN, max=CRF_MAX, s=(CRF_MAX-CRF_MIN), w=SLIDER_WIDTH, v=23, dc=self.crf_slider_callback)
        self.crf_val = cmds.text(p=self.crf_frame, l=cmds.intSliderGrp(self.crf_slider, q=True, v=True))
        
        self.container_sep=cmds.separator(p=self.options_frame, hr=0, st=SEP_STYLE2, w=VERTICAL_SEP_WIDTH)
        self.container_frame = cmds.rowLayout(p=self.options_frame, nc=1, w=OPT_WIDTH)
        self.container_opt = cmds.optionMenuGrp(p=self.container_frame, el='')
        for c in self.LIBX264_CONTAINERS:
            cmds.menuItem(c)

        self.output_frame = cmds.rowLayout(p=self.window_frame, nc=3, h=LAY_HEIGHT)
        self.output_sep = cmds.separator(p=self.output_frame)
        self.output_entry = cmds.textField(p=self.output_frame, w=PATH_ENTRY_WIDTH, ann='Output path')
        self.output_browse = cmds.button(p=self.output_frame, l='Browse', w=BROWSE_WIDTH, c=self.out_browse_callback)

        self.pblast_sep = cmds.separator(p=self.window_frame, st=SEP_STYLE)
        self.pblast_frame = cmds.rowLayout(p=self.window_frame,nc=1, h=LAY_HEIGHT, cl1='center')
        self.pblast_btn = cmds.button(p=self.pblast_frame, l='Playblast', w=PLAYBLAST_WIDTH, bgc=[0.1, 0.5, 0.3], al='center')


        self.log_sep = cmds.separator(p=self.window_frame, st=SEP_STYLE)
        self.log_frame = cmds.columnLayout(p=self.window_frame)
        
        self.log_label = cmds.text(p=self.log_frame, l='Log', height = 20)
        self.log = cmds.scrollField(p=self.log_frame, w=600, ed=False)

        cmds.showWindow()

    def ff_browse_callback(self, val):
        result = cmds.fileDialog2(ds=2, fm=1)
        if result != "":
            cmds.textField(self.ffmpeg_entry, e=True, tx=result[0])

    def crf_slider_callback(self, val):
        cmds.text(self.crf_val, e=True, l=val)

    def codecs_opt_callback(self, val):
        if val == "libx264":
            cmds.optionMenuGrp(self.container_opt, e=True, dai=True)
            for c in self.LIBX264_CONTAINERS:
                cmds.menuItem(c)
        if val == "libx265":
            cmds.optionMenuGrp(self.container_opt, e=True, dai=True)
            for c in self.LIBX265_CONTAINERS:
                cmds.menuItem(c)

    def out_browse_callback(self, val):
        result = cmds.fileDialog2(fm=0, ds=2)
        if result != "":
            cmds.textField(self.output_entry, e=True, tx=result[0])


        


    # cmds.playblast( p=60, s="ohNo", f="C:/Users/T480/Desktop/myMovie2.mv", v=True )

if __name__ == "__main__":
    
    app = MayaPlayblast()
    