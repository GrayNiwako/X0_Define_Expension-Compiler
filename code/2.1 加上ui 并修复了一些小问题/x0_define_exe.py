# -*- coding: utf-8 -*-
import wx
import os
import compiler

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, u'x0_define编译器', size=(1200, 700))
        cursor = wx.Cursor(wx.CURSOR_ARROW)
        self.SetCursor(cursor)
        self.menuBar = wx.MenuBar()
        self.panel = wx.Panel(self)
        self.SetBackgroundColour('White')
        self.statusbar = self.CreateStatusBar()

        font1 = wx.Font(20, wx.SWISS, wx.NORMAL, wx.BOLD)
        self.fin_title = wx.StaticText(self, -1, u'fin', pos=(20, 20))
        self.ftable_title = wx.StaticText(self, -1, u'ftable', pos=(20, 450))
        self.input_title = wx.StaticText(self, -1, u'Input', pos=(380, 20))
        self.fresult_title = wx.StaticText(self, -1, u'fresult', pos=(380, 120))
        self.foutput_title = wx.StaticText(self, -1, u'foutput', pos=(380, 310))
        self.fcode_title = wx.StaticText(self, -1, u'fcode', pos=(710, 20))
        self.debug_title = wx.StaticText(self, -1, u'Debug', pos=(940, 20))
        self.stack_title = wx.StaticText(self, -1, u'Stack', pos=(940, 140))
        self.fin_title.SetFont(font1)
        self.ftable_title.SetFont(font1)
        self.input_title.SetFont(font1)
        self.fresult_title.SetFont(font1)
        self.foutput_title.SetFont(font1)
        self.fcode_title.SetFont(font1)
        self.debug_title.SetFont(font1)
        self.stack_title.SetFont(font1)

        wx.StaticText(self.panel, -1, u'<- bottom', pos=(1100, 170))
        wx.StaticText(self.panel, -1, u'<- top', pos=(1100, 580))

        About = wx.Menu()
        Instruction = wx.NewId()
        Author = wx.NewId()
        About.Append(Instruction, u'使用说明(&I)\tF1', u'使用说明指南')
        About.Append(Author, u'作者(&A)\tF2', u'作者信息')
        self.Bind(wx.EVT_MENU, self.OnHelpInstruction, id=Instruction)
        self.Bind(wx.EVT_MENU, self.OnHelpAuthor, id=Author)
        self.menuBar.Append(About, u'关于(&B)')

        self.SetMenuBar(self.menuBar)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.fin = wx.TextCtrl(self.panel, -1, '', size=(330, 390), style=wx.TE_MULTILINE | wx.HSCROLL, pos=(20, 50))
        self.ftable = wx.TextCtrl(self.panel, -1, '', size=(660, 120), style=wx.TE_MULTILINE | wx.TE_READONLY
                                                                             | wx.HSCROLL, pos=(20, 480))
        self.input = wx.TextCtrl(self.panel, -1, '', size=(300, 60), style=wx.TE_MULTILINE | wx.HSCROLL, pos=(380, 50))
        self.fresult = wx.TextCtrl(self.panel, -1, '', size=(300, 150), style=wx.TE_MULTILINE | wx.TE_READONLY
                                                                             | wx.HSCROLL, pos=(380, 150))
        self.foutput = wx.TextCtrl(self.panel, -1, '', size=(300, 100), style=wx.TE_MULTILINE | wx.TE_READONLY
                                                                             | wx.HSCROLL, pos=(380, 340))
        self.fcode = wx.TextCtrl(self.panel, -1, '', size=(200, 550), style=wx.TE_MULTILINE | wx.TE_READONLY
                                                                              | wx.HSCROLL, pos=(710, 50))
        self.debug = wx.TextCtrl(self.panel, -1, '', size=(100, -1), style=wx.TE_RICH, pos=(940, 50))
        self.stack = wx.TextCtrl(self.panel, -1, '', size=(150, 430), style=wx.TE_MULTILINE | wx.TE_READONLY
                                                                            | wx.HSCROLL, pos=(940, 170))

        Button1 = wx.Button(self.panel, -1, u'line', pos=(80, 10))
        Button2 = wx.Button(self.panel, -1, u'open', pos=(170, 10))
        Button3 = wx.Button(self.panel, -1, u'execute', pos=(260, 10))
        Button4 = wx.Button(self.panel, -1, u'back', pos=(1070, 30))
        Button5 = wx.Button(self.panel, -1, u'next', pos=(1070, 70))
        Button6 = wx.Button(self.panel, -1, u'debug', pos=(1070, 110))
        self.Bind(wx.EVT_BUTTON, self.OnLine, Button1)
        self.Bind(wx.EVT_BUTTON, self.OnOpen, Button2)
        self.Bind(wx.EVT_BUTTON, self.OnExecute, Button3)
        self.Bind(wx.EVT_BUTTON, self.OnBack, Button4)
        self.Bind(wx.EVT_BUTTON, self.OnNext, Button5)
        self.Bind(wx.EVT_BUTTON, self.OnDebug, Button6)

    def OnLine(self, evt):
        data = self.fin.GetValue()
        line_list = data.strip('\n').split('\n')
        line_data = ''
        if data.split('\t')[0] == '1':
            for i in range(len(line_list)):
                line_no = i + 1
                tmp = line_list[i]
                while line_no >= 10:
                    tmp = tmp[1:]
                    line_no /= 10
                tmp = tmp[2:]
                line_data = line_data + tmp + '\n'
        else:
            for i in range(len(line_list)):
                line_data = line_data + str(i + 1) + '\t' + line_list[i] + '\n'
        self.fin.SetValue(line_data)

    def OnOpen(self, evt):
        wildcard = "文本文档 (.txt)|*.txt| All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(), "", wildcard, style=wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            file0 = open(dialog.GetPath(), 'r')
            data = file0.read()
            file0.close()
            self.fin.SetValue(data)
        dialog.Destroy()

    def OnExecute(self, evt):
        self.ftable.Clear()
        self.fresult.Clear()
        self.foutput.Clear()
        self.fcode.Clear()
        self.debug.Clear()
        self.stack.Clear()

        argv_list = self.input.GetValue().strip('\n').split('\n')
        self.input.Clear()
        compiler.x0_compiler(self.fin.GetValue(), argv_list)

        file1 = open('../result_files/ftable.txt', 'r')
        self.ftable.SetValue(file1.read())
        file1.close()
        file2 = open('../result_files/fcode.txt', 'r')
        self.fcode.SetValue(file2.read())
        file2.close()

        file3 = open('../result_files/fresult.txt', 'r')
        if self.fcode.GetValue() != '':
            self.fresult.SetValue(file3.read())
        file3.close()

        file4 = open('../result_files/foutput.txt', 'r')
        self.foutput.SetValue(file4.read())
        file4.close()
        return

    def OnBack(self, evt):
        return

    def OnNext(self, evt):
        return

    def OnDebug(self, evt):
        return

    def OnHelpInstruction(self, evt):
        wx.MessageBox(u'使用说明指南\n\n1. 在fin框中直接输入源程序，或者点击open按钮打开相应文件\n'
                      u'2. 按照是否需要，在Input框中输入相应内容\n'
                      u'3. 再点击execute按钮执行\n'
                      u'4. 点击line按钮可以显示行号，再点击一次可以取消显示行号\n'
                      u'【注意】行号显示的状态下，无法执行程序\n',
                  u'编译原理实践课设', wx.OK | wx.ICON_INFORMATION, self)

    def OnHelpAuthor(self, evt):
        wx.MessageBox(u'x0_define编译器\n\n学号：10152130122\n姓名：钱庭涵\n',
                  u'编译原理实践课设', wx.OK | wx.ICON_INFORMATION, self)

    def OnClose(self, evt):
        dlg = wx.MessageDialog(None, u'确认离开？', u'关闭', wx.YES_NO | wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            evt.Skip()
        dlg.Destroy()


if __name__ == u'__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show(True)
    frame.Center(wx.BOTH)
    app.MainLoop()
