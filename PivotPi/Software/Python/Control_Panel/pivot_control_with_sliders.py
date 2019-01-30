from __future__ import print_function
from __future__ import division


import subprocess
from time import sleep
from pivotpi import *

try:
    import wx
except ImportError:
    raise ImportError,"The wxPython module is required to run this program"

detected_pivotpi = False
total_servos = 8
horizontal_spacer = 20
vertical_spacer = 30
total_ids_per_line = 5
degree_str = " Deg"

class MainPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.WHITE)
        self.frame = parent

        font = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        # font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, u'Helvetica')
        self.SetFont(font)

        self.txt = []
        self.fields = []
        self.field_lbl = []
        self.servo = []
        self.slider = []
        self.led = []

        self.vsizer = wx.BoxSizer(wx.VERTICAL)

        # contains the titlestr_sizer and the icon
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # contains the title and potential warning that pivotpi is not detected
        titlestr_sizer = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, -1,
                        label="PivotPi Control Panel", style=wx.ALIGN_CENTRE)
        title.SetFont(wx.Font(  20,
                                wx.FONTSTYLE_NORMAL,
                                wx.FONTFAMILY_DEFAULT,
                                wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD))
        titlestr_sizer.Add(title, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 20)

        if not detected_pivotpi:
            warning_str = wx.StaticText(self, -1,
                        label="PivotPi Not Detected", style=wx.ALIGN_CENTRE)
            warning_str.SetFont(wx.Font(  12,
                                wx.FONTSTYLE_NORMAL,
                                wx.FONTFAMILY_DEFAULT,
                                wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD))
            titlestr_sizer.Add(warning_str, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 20)

        bitmap = wx.Image("/home/pi/Dexter/PivotPi/Software/Python/Control_Panel/PivotPiIcon.jpg",wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        title_icon = wx.StaticBitmap(self, -1, bitmap)

        title_sizer.Add(titlestr_sizer, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 20)
        title_sizer.Add(title_icon,0,wx.ALIGN_CENTER_VERTICAL|wx.LEFT,40)
        self.vsizer.AddSpacer(20)
        self.vsizer.Add(title_sizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 20)
        self.vsizer.AddSpacer(20)

        for i in range(total_servos):

            self.fields.append(wx.BoxSizer(wx.HORIZONTAL))
            txt = wx.StaticText(self, label="Servo/Pivot {}:".format(i+1))
            txt.SetFont(wx.Font(  14,
                                wx.FONTSTYLE_NORMAL,
                                wx.FONTFAMILY_DEFAULT,
                                wx.FONTSTYLE_NORMAL,
                                wx.FONTWEIGHT_BOLD))
            self.servo.append(txt)
            self.fields[i].AddSpacer(horizontal_spacer)
            self.fields[i].Add(self.servo[i])

            self.slider.append(wx.Slider(self, id=i*total_ids_per_line, minValue=0, maxValue=180, size=(180,20)))
            self.fields[i].AddSpacer(horizontal_spacer)
            self.fields[i].Add(self.slider[i])

            self.field_lbl.append(wx.StaticText(self, label="target angle:"))
            self.txt.append(wx.TextCtrl(self, id=i*total_ids_per_line+3))
            self.fields[i].AddSpacer(horizontal_spacer)
            self.fields[i].Add(self.field_lbl[i])
            self.fields[i].AddSpacer(5)
            self.fields[i].Add(self.txt[i])
            self.fields[i].AddSpacer(horizontal_spacer)

            self.led.append(wx.CheckBox(self, id=i*total_ids_per_line+4, label="LED {}".format(i+1)))
            self.fields[i].Add(self.led[i])
            self.fields[i].AddSpacer(horizontal_spacer)

            self.vsizer.Add(self.fields[i])
            self.vsizer.AddSpacer(horizontal_spacer)

        self.vsizer.AddSpacer(vertical_spacer)

        for i in range(total_servos):
            self.slider[i].Bind(wx.EVT_LEFT_UP, self.on_left_click)
            self.slider[i].Bind(wx.EVT_SCROLL_THUMBTRACK, self.on_slide)
            self.Bind(wx.EVT_CHECKBOX, self.OnLED, self.led[i])
            self.txt[i].Bind(wx.EVT_CHAR, self.OnText, self.txt[i])

        exit_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.exit_btn = wx.Button(self, label="Exit")
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.exit_btn)
        self.exit_txt = wx.StaticText(self, label=" ")
        self.code_btn = wx.Button(self, label="Go to PivotPi Code Folder")
        self.Bind(wx.EVT_BUTTON, self.OnCode, self.code_btn)
        self.exit_btn.SetBackgroundColour("White")
        self.code_btn.SetBackgroundColour("White")
        exit_sizer.Add(self.exit_txt, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 100)
        exit_sizer.Add(self.code_btn, 0, wx.ALIGN_CENTER_VERTICAL|wx.CENTER, 60)
        # exit_sizer.Add(self.exit_txt, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.LEFT, 100)
        exit_sizer.Add(self.exit_btn, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 10)
        self.vsizer.Add(exit_sizer, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.BOTTOM, 10)

        self.SetSizer(self.vsizer)


    def OnExit(self, event):
        self.frame.Close()

    def OnCode(self, event):
        pivotpi_path_cmd = "pcmanfm /home/pi/Dexter/PivotPi"
        subprocess.Popen(pivotpi_path_cmd, shell=True)


    def on_left_click(self, event):
        event_id = event.GetId()
        event_obj = event.GetEventObject()
        position = event_obj.GetValue()   
        servo_angle = int(event_obj.GetValue())  
        servo_id = int(event_id)//total_ids_per_line
        print ("Setting Pivot {} to {}".format(servo_id+1, servo_angle))
        if detected_pivotpi:
            my_pivot.angle(servo_id, servo_angle )
        event.Skip() 

    def on_slide(self, event):
        event_id = event.GetId()
        event_obj = event.GetEventObject()
        servo_id = int(event_id)//total_ids_per_line
        position = event_obj.GetValue()
        self.txt[servo_id].SetValue(str(position))
        event.Skip()

    def OnText(self, event):
        event_id = event.GetId()
        event_obj = event.GetEventObject()
        servo_id = int(event_id)//total_ids_per_line
        key_code = (event.GetKeyCode())
        if key_code == 13 or key_code == 9:  # ENTER KEY or TAB
            try:
            # the try may fail on getting a servo_angle 
            # when the field is empty or not an int
                servo_angle = int(event_obj.GetValue())  
                print ("Setting Pivot {} to {}".format(servo_id+1, servo_angle))
                if detected_pivotpi:
                    my_pivot.angle(servo_id, servo_angle )
                self.slider[servo_id].SetValue(servo_angle)
            except:
                pass
            self.txt[(servo_id+1)].SetFocus() 

        event.Skip()        

    def OnLED(self, event):
        led_id = int(event.GetId()//total_ids_per_line)
        led_status = event.GetEventObject().GetValue()
        print("Setting LED {} to {}".format(led_id+1, led_status*254))
        if detected_pivotpi:
            my_pivot.led(led_id,led_status*254)


class MainFrame(wx.Frame):
    def __init__(self):
        """Constructor"""
        # wx.ComboBox

        # wx.Icon(ICON_PATH+'favicon.ico', wx.BITMAP_TYPE_ICO)
        wx.Log.SetVerbose(False)
        wx.Frame.__init__(self, None, title="PivotPi Control Panel", size=(650,600))		# Set the fram size

        panel = MainPanel(self)
        self.Center()

class Main(wx.App):
    def __init__(self, redirect=False, filename=None):
        """Constructor"""
        wx.App.__init__(self, redirect, filename)
        dlg = MainFrame()
        dlg.Show()

if __name__ == "__main__":
    try:
        my_pivot = PivotPi()
        detected_pivotpi = True
    except:
        detected_pivotpi = False
        # class NoPivot(wx.App):
        #     def OnInit(self):
        #         dlg = wx.MessageBox("Unfortunately no PivotPi is Detected\nhttp://DexterIndustries.com/pivotpi for more details", 
        #             "ERROR", wx.ICON_WARNING)
        #         return True                
        # app = NoPivot(False)

    app = Main()
    app.MainLoop()
        