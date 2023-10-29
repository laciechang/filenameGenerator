import datetime
import importlib.util
import tempfile
from xml.etree import ElementTree as ET

RESOLVE_NTSC_FPS_MAPPING = {
    '23': '2397',
    '29': '2997',
    '47': '4795',
    '59': '5994',
    '95': '9590',
    '119': '11988',
}

RESOLUTION_MAPPING  = {
    (1920, 1080):   'HD',
    (2048, 1080):   'C-190_2K',
    (2048, 858):    'S-239_2K',
    (1998, 1080):   'F-185_2K',
    (3840, 2160):   'UHD',
    (4096, 2160):   'C-190_4K',
    (4096, 1716):   'S-239_4K',
    (3996, 2160):   'F-185_4K',
}

AUDIOCHANNEL_MAPPING = {
    0: 'MUTE',
    1: 'MONO',
    2: 'STEREO',
    6: '5.1',
    8: '7.1'
}

AUDIOCODEC_MAPPING = {
    'lpcm': "PCM",
}

OrderBar = 'OrderBar'
ClosedTab = 'ClosedTab'
ResultName = 'ResultName'
ApplyName = 'ApplyName'
RefreshBt = 'RefreshBt'
InputTitle = 'InputTitle'
InputVCodec = 'InputVCodec'
InputACodec = 'InputACodec'
InputReso = 'InputReso'
InputACh = 'InputACh'
InputFPS = 'InputFPS'
InputAspect = 'InputAspect'
InputSubtitle = 'InputSubtitle'
InputDate = 'InputDate'
InputVersion = 'InputVersion'
InputComment = 'InputComment'
InputColorspace = 'InputColorspace'

Seperator = '_'

InputLineEdits = [InputTitle, InputFPS, InputAspect, InputVCodec, InputACh, InputACodec, InputDate, InputVersion, InputComment, InputReso, InputColorspace, InputSubtitle]
InputComboboxs = []

TabBarStyleSheet = "QTabBar::tab{background:#212121;border:1px solid #333333;border-radius:8px;height:40px}\nQTabBar::tab:hover{color:white;border:1px solid #73261F}\nQTabBar::close-button {image:null}\nQTabBar::close-button:hover {image: url(/Users/lc/Downloads/1193-2.png)}"
ClosedTabBarStyleSheet = "QTabBar::tab{color:#111111;background:#212121;border:1px solid #333333;border-radius:8px;height:40px}\nQTabBar::tab:hover{color:grey;border:1px solid #73261F}\nQTabBar::close-button {image:null}\nQTabBar::close-button:hover {image: url(/Users/lc/Downloads/1193-2.png)}"
ComboboxStyleSheet = "QComboBox:editable{border: 1px solid black;border-radius:3px}\nQComboBox::drop-down{background:#666666;border: 5px solid #1f1f1f;border-radius:3px;width: 10px;subcontrol-origin: padding;subcontrol-position: top left;}"

RenderSettings = {}
TimelineSettings = {}

BarNameList = {
    "片名":InputTitle,
    "视频编码":InputVCodec,
    "音频编码":InputACodec,
    "分辨率":InputReso,
    "声道数":InputACh,
    "FPS":InputFPS,
    "画面比例":InputAspect,
    "色彩空间":InputColorspace,
    "字幕":InputSubtitle,
    "日期":InputDate,
    "内容版本":InputVersion,
    "备注":InputComment,
}

def load_dynamic(module, path):
    loader = importlib.machinery.ExtensionFileLoader(module, path)
    module = loader.load_module()
    return module
bmd = load_dynamic('fusionscript', "/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Libraries/Fusion/fusionscript.so")

resolve = bmd.scriptapp('Resolve')
fu = bmd.scriptapp('Fusion')
ui = fu.UIManager
disp = bmd.UIDispatcher(ui)

class Project():
    def __init__(self) -> None:
        self.project_manager = resolve.GetProjectManager()
        self.media_storage = resolve.GetMediaStorage()
        self.current_project = self.project_manager.GetCurrentProject()
        self.project_name = self.current_project.GetName()
        self.projects = self.project_manager.GetProjectListInCurrentFolder()
        self.timeline = self.current_project.GetCurrentTimeline()

class GrabInfo():
    def __init__(self, fromrender, fromtimeline) -> None:
        self.rendersettings = fromrender
        self.timelinesettings = fromtimeline
    
    def getVideoCodec(self):
        codec = str(self.rendersettings['VideoCodec'])
        alpha = self.rendersettings['ExportAlpha']
        if alpha:
            codec = codec+"A"
        codec = codec.replace('.', '')
        codec = codec.replace('Apple ProRes', 'ProRes')
        return codec
    
    def getAudioCodec(self):
        if self.rendersettings['IsExportAudio']:
            codec = self.rendersettings['AudioCodec']
            try:
                codec = AUDIOCODEC_MAPPING[codec]
            except KeyError:
                pass
        else:
            codec = ''
        return codec
    
    def getImageRatio(self):
        timeline = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline()
        tmp_file = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
        timeline.Export(tmp_file.name, resolve.EXPORT_DOLBY_VISION_VER_2_9)
        tree = ET.parse(tmp_file)
        root = tree.getroot()
        image = float(root.find('./Outputs/Output/ImageAspectRatio').text)
        canvas = float(root.find('./Outputs/Output/CanvasAspectRatio').text)
        if image != canvas:
            output = str(int(image*100))
        else:
            output = None
        return output
    
    def getDate(self):
        return str(datetime.date.today().strftime("%Y%m%d"))

    def getFPS(self):
        fps_raw = self.rendersettings['FrameRate']
        if fps_raw in list(RESOLVE_NTSC_FPS_MAPPING.keys()):
            fps_raw = RESOLVE_NTSC_FPS_MAPPING[fps_raw]
        return str(fps_raw)
    
    def getResolution(self):
        width = int(self.rendersettings['FormatWidth'])
        height = int(self.rendersettings['FormatHeight'])
        resolution = (width, height)
        if resolution in list(RESOLUTION_MAPPING.keys()):
            output = RESOLUTION_MAPPING[resolution]
        else:
            output = str(width) + 'x' + str(height)
        return output

    def getAudioChannel(self):
        if not self.rendersettings['IsExportAudio']:
            channel = AUDIOCHANNEL_MAPPING[0]
        else:
            try:
                channel = self.timelinesettings['audioPlayoutNumChannels']
                channel = AUDIOCHANNEL_MAPPING[int(channel)]
            except KeyError:
                channel = AUDIOCHANNEL_MAPPING[2]
        return channel

    def getColorspace(self):
        print(self.timelinesettings)
        mode = self.timelinesettings['colorScienceMode']
        odt = self.timelinesettings['colorAcesODT']
        outputspace = self.timelinesettings['colorSpaceOutput']
        timelinespace = self.timelinesettings['colorSpaceTimeline']

        if mode.startswith('aces'):
            colorspace = odt
        elif outputspace == 'Same as Timeline':
            colorspace = timelinespace
        else:
            colorspace = outputspace
        return colorspace
    
    def getName(self):
        return Project().project_name
    
    def getAll(self):
        return {
            InputTitle: self.getName(),
            InputVCodec: self.getVideoCodec(),
            InputACodec: self.getAudioCodec(),
            InputReso: self.getResolution(),
            InputACh: self.getAudioChannel(),
            InputFPS: self.getFPS(),
            InputAspect: self.getImageRatio(),
            InputDate: self.getDate(),
            InputColorspace: self.getColorspace()
        }

def getCurrentRenderSettings() -> dict:
    p = Project()
    proj = p.current_project
    temp_id = proj.AddRenderJob()
    if not temp_id:
        temp_path = p.media_storage.GetMountedVolumeList()[0]
        proj.SetRenderSettings({'TargetDir': temp_path})
        temp_id = proj.AddRenderJob()
    renderqueue = proj.GetRenderJobList()
    current_detail = list(d for d in renderqueue if d['JobId'] == temp_id)[0]
    proj.DeleteRenderJob(temp_id)
    return current_detail

def RefreshRenderSettings():
    global RenderSettings, TimelineSettings
    RenderSettings = getCurrentRenderSettings()
    TimelineSettings = resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline().GetSetting()






inputlist = [
                ui.VGroup({"Spacing": 10},[
                    ui.HGroup([
                        ui.Label({"Text": "片名", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputTitle}),
                    ]),
                    ui.HGroup([
                        ui.Label({"Text": "分辨率", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputReso}),
                    ]),
                    ui.HGroup([
                        ui.Label({"Text": "FPS", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputFPS}),
                    ]),
                    ui.HGroup([
                        ui.Label({"Text": "画面比例", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputAspect}),
                    ]),
                    ui.HGroup([
                        ui.Label({"Text": "视频编码", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputVCodec}),
                    ]),
                    ui.HGroup([
                        ui.Label({"Text": "色彩空间", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputColorspace}),
                    ]),
                ]),
                ui.VGroup({"Spacing": 10},[
                    ui.HGroup([
                        ui.Label({"Text": "音频通道", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputACh}),
                    ]),
                    ui.HGroup([
                        ui.Label({"Text": "音频编码", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputACodec}),
                    ]),
                    ui.HGroup([
                        ui.Label({"Text": "字幕类型", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputSubtitle}),
                    ]),
                    ui.HGroup([
                        ui.Label({"Text": "日期", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputDate}),
                    ]),
                    ui.HGroup([
                        ui.Label({"Text": "内容版本", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputVersion}),
                    ]),
                    ui.HGroup([
                        ui.Label({"Text": "备注", "Alignment": {'AlignRight': True}}),
                        ui.LineEdit({"ID": InputComment}),
                    ]),
                ]),
                ui.Label({"StyleSheet": "max-width: 80px"}),
            ]

window_01 = [
        ui.VGroup({"Spacing": 5},
        [
            ui.Label({"ID": ResultName,"Text": "test", "StyleSheet": "max-height: 100px","Font": ui.Font({ 'PixelSize': 18 }),'Alignment': { 'AlignCenter' : True }}),
            ui.HGroup(inputlist),
            ui.Label({"StyleSheet": "max-height: 30px"}),
            ui.HGroup({"Weight": 0},[
                ui.Button({"ID":"showswitcher", "Weight": 0, "Text": "排序"}),
                ui.HGap(),
                ui.Button({"ID": RefreshBt, "Weight": 0, "Text": "刷新"}),
                ui.Button({"ID": ApplyName, "Weight": 0, "Text": "应用文件名"}),
            ]),
        ])
]

dlg = disp.AddWindow({
                        "WindowTitle": "Filename Generator", 
                        "ID": "MyWin", 
                        "Geometry": [ 
                                    600, 300, # position when starting
                                    1000, 400 #width, height
                         ], 
                        "WindowFlags":{
                            "Window": True,
                        }
                        }, window_01)

switcher = disp.AddWindow({
    "WindowTitle": "Switcher", 
    "ID":"switcher",
    "WindowFlags": {"SplashScreen" : True},
    "Geometry":[
        600, 750,
        1200, 170
    ]
    }, [
        ui.VGroup([
            ui.TabBar({"ID": OrderBar, "Movable": True, "TabsClosable": True, "StyleSheet": TabBarStyleSheet,'Events': {'CloseRequested': True, 'TabMoved': True, 'TabBarClicked': True} }),
            ui.TabBar({"ID": ClosedTab, "TabsClosable": True, "StyleSheet": ClosedTabBarStyleSheet, 'Events': {'CloseRequested': True, 'TabBarClicked': True} }),
            ui.HGroup({"Weight": 0},[
                ui.HGap(),
                ui.Button({"ID": 'reset', "Text": "重置", "Weight": 0, "Enabled": False}),
                ui.HGap(),
            ]),
        ])
])

itm = dlg.GetItems()
itm2 = switcher.GetItems()

def completeLineEdit():
    info = GrabInfo(RenderSettings, TimelineSettings)
    all_info = info.getAll()
    print(all_info)
    for i in list(all_info.keys()):
        itm[i].Text = all_info[i]

def buildTab():
    for i in list(BarNameList.keys()):
        itm2[OrderBar].AddTab(i)

def buildPreview():
    
    txt = []
    tabcount = itm2[OrderBar].Count()
    for i in range(0, tabcount):
        tab = itm2[OrderBar].GetTabText(i)
        tabname = BarNameList[tab]
        content = itm[tabname].Text
        if len(content) > 0:
            txt.append(content)
    output = Seperator.join(txt)
    output = output.replace(' ', Seperator)
    output = output.replace('.', '-')
    itm[ResultName].Text = output


# The window was closed
def _close(ev):
    switcher.Hide()
    disp.ExitLoop()

def _closetab(ev):
    tabname = itm2[OrderBar].GetTabText(ev['Index'])
    itm2[OrderBar].RemoveTab(ev['Index'])
    itm2[ClosedTab].AddTab(tabname)
    _refresh_name(None)

def _rescuetab(ev):
    tabname = itm2[ClosedTab].GetTabText(ev['Index'])
    itm2[ClosedTab].RemoveTab(ev['Index'])
    itm2[OrderBar].AddTab(tabname)
    _refresh_name(None)

def _refresh(ev):
    RefreshRenderSettings()
    completeLineEdit()
    _refresh_name(None)

def _refresh_name(ev):
    buildPreview()

def _apply_name(ev):
    Project().current_project.SetRenderSettings({'CustomName': itm[ResultName].Text})

def _showswitcher(ev):
    if not itm2['reset'].GetEnabled():
        itm['showswitcher'].Down = True
        pos = itm['MyWin'].GetGeometry()
        geo = itm2['switcher'].GetGeometry()
        pos = [pos[1]-(geo[3]-pos[3])/2, pos[2]+pos[4]]
        itm2['switcher'].Move(pos)
        itm2['reset'].Enabled = True
        switcher.Show()
    else:
        switcher.Hide()
        itm2['reset'].Enabled = False
        itm['showswitcher'].Down = False

def cleanAllTab(tabitem):
    tabcount = tabitem.Count()
    for i in range(0, tabcount):
        tabitem.RemoveTab(0)

def _resetswitcher(ev):
    cleanAllTab(itm2[OrderBar])
    cleanAllTab(itm2[ClosedTab])
    buildTab()
    buildPreview()

def _test(ev):
    print(ev)

dlg.On.MyWin.Close = _close
for i in InputLineEdits:
    dlg.On[i].TextChanged = _refresh_name

switcher.On['reset'].Clicked = _resetswitcher
switcher.On[OrderBar].CloseRequested = _closetab
switcher.On[ClosedTab].CloseRequested = _rescuetab
switcher.On[OrderBar].TabMoved = _refresh_name
dlg.On[ApplyName].Clicked = _apply_name
dlg.On[RefreshBt].Clicked = _refresh
dlg.On["showswitcher"].Clicked = _showswitcher

RefreshRenderSettings()
buildTab()
completeLineEdit()
buildPreview()

switcher.Hide()
dlg.Show()
disp.RunLoop()
dlg.Hide()