import tkinter as tk




class Application(tk.Tk):
    '''
    这个是初始的GUI, 包含所有别的.
    正在编写菜单栏, 菜单栏包含: 帮助, 设置, 游戏
    有工具栏, 用frame来实现, 目前只包含好友列表功能(支持修改)
    窗口应该包含创建聊天室和连接好友功能. 还可以一键查找上线好友
    '''
    def __init__(self):
        super().__init__()
        self.create_widgets()

    def create_widgets(self):
        menubar = tk.Menu(self)

        #创建下拉菜单File，然后将其加入到顶级的菜单栏中
        gameMenu = tk.Menu(menubar,tearoff=0)
        gameMenu.add_command(label="Janken", command=lambda)
        filemenu.add_command(label="Save", command=hello)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        #创建另一个下拉菜单Edit
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Cut", command=hello)
        editmenu.add_command(label="Copy", command=hello)
        editmenu.add_command(label="Paste", command=hello)
        menubar.add_cascade(label="Edit",menu=editmenu)
        #创建下拉菜单Help
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=about)
        menubar.add_cascade(label="Help", menu=helpmenu)