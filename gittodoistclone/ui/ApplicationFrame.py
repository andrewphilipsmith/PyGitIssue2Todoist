
from typing import Tuple

from logging import Logger
from logging import getLogger

from wx import BOTH
from wx import DEFAULT_FRAME_STYLE
from wx import EVT_CLOSE
from wx import EVT_MENU
from wx import EXPAND
from wx import FRAME_EX_METAL
from wx import HORIZONTAL
from wx import OK

from wx import BoxSizer
from wx import Size
from wx import CommandEvent
from wx import Frame
from wx import Menu
from wx import MenuBar
from wx import Window

from wx import NewIdRef as wxNewIdRef

from wx.adv import AboutDialogInfo
from wx.adv import AboutBox

from gittodoistclone.general.Preferences import Preferences
from gittodoistclone.general.Version import Version

from gittodoistclone.ui.CustomEvents import EVT_ISSUES_SELECTED
from gittodoistclone.ui.CustomEvents import IssuesSelectedEvent

from gittodoistclone.ui.GitHubPanel import GitHubPanel
from gittodoistclone.ui.TodoistPanel import CloneInformation
from gittodoistclone.ui.TodoistPanel import TodoistPanel

from gittodoistclone.ui.dialogs.DlgConfigure import DlgConfigure


class ApplicationFrame(Frame):

    def __init__(self, parent: Window, wxID: int, title: str):

        self._preferences: Preferences = Preferences()
        appSize: Size = Size(self._preferences.startupWidth, self._preferences.startupHeight)

        super().__init__(parent=parent, id=wxID, title=title, size=appSize, style=DEFAULT_FRAME_STYLE | FRAME_EX_METAL)

        self.logger: Logger = getLogger(__name__)

        self._status = self.CreateStatusBar()
        self._status.SetStatusText('Ready!')

        self._createApplicationMenuBar()
        self._githubPanel, self._todoistPanel = self._createApplicationContentArea()
        self.SetThemeEnabled(True)

        x, y = self._preferences.appStartupPosition

        if x == str(Preferences.NO_DEFAULT_X) or y == str(Preferences.NO_DEFAULT_Y):
            self.Center(BOTH)  # Center on the screen
        else:
            appPosition: Tuple[int, int] = self._preferences.appStartupPosition
            self.SetPosition(pt=appPosition)

        self.Bind(EVT_CLOSE, self.Close)
        self.Bind(EVT_ISSUES_SELECTED, self._onIssuesSelected)

    def Close(self, force=False):

        ourSize: Tuple[int, int] = self.GetSize()
        self._preferences.startupWidth  = ourSize[0]
        self._preferences.startupHeight = ourSize[1]

        pos: Tuple[int, int] = self.GetPosition()
        self._preferences.appStartupPosition = pos

        self.Destroy()

    def _createApplicationMenuBar(self):

        menuBar:  MenuBar = MenuBar()
        fileMenu: Menu = Menu()
        helpMenu: Menu = Menu()

        idExit:      int = wxNewIdRef()
        idConfigure: int = wxNewIdRef()
        idAbout:     int = wxNewIdRef()

        fileMenu.Append(idConfigure, 'Configure', 'Configure Application IDs')
        fileMenu.AppendSeparator()
        fileMenu.Append(idExit, '&Quit', "Quit Application")

        helpMenu.AppendSeparator()
        helpMenu.Append(idAbout, '&About', 'Tell you about me')

        menuBar.Append(fileMenu, 'File')
        menuBar.Append(helpMenu, 'Help')

        self.SetMenuBar(menuBar)

        self.Bind(EVT_MENU, self._onConfigure, id=idConfigure)
        self.Bind(EVT_MENU, self._onAbout,     id=idAbout)
        self.Bind(EVT_MENU, self.Close,        id=idExit)

    def _createApplicationContentArea(self) -> Tuple[GitHubPanel, TodoistPanel]:

        leftPanel:  GitHubPanel  = GitHubPanel(self)
        rightPanel: TodoistPanel = TodoistPanel(self)

        mainSizer: BoxSizer = BoxSizer(orient=HORIZONTAL)
        mainSizer.Add(leftPanel,  1, EXPAND)
        mainSizer.Add(rightPanel, 1, EXPAND)

        self.SetSizer(mainSizer)
        # mainSizer.Fit(self)       # Don't do this or setting of frame size won't work

        return leftPanel, rightPanel

    def _onIssuesSelected(self, event: IssuesSelectedEvent):

        cloneInformation: CloneInformation = CloneInformation()

        cloneInformation.repositoryTask    = event.repositoryName
        cloneInformation.milestoneNameTask = event.milestoneName
        cloneInformation.tasksToClone      = event.selectedIssues

        self.logger.info(f'{event.selectedIssues=}')

        self._todoistPanel.tasksToClone = cloneInformation

    # noinspection PyUnusedLocal
    def _onConfigure(self, event: CommandEvent):

        dlg: DlgConfigure = DlgConfigure(self)
        if dlg.ShowModal() == OK:
            todoistToken: str = dlg.todoistToken
            githubToken:  str = dlg.githubToken
            self.logger.info(f'{todoistToken=} - {githubToken=}')

    # noinspection PyUnusedLocal
    def _onAbout(self, event: CommandEvent):

        info: AboutDialogInfo = AboutDialogInfo()

        info.Name    = Version.applicationName()
        info.Version = Version.applicationVersion()
        info.Website = ('https://github.com/hasii2011/gittodoistclone/wiki', 'Get the best information')

        info.Developers = ["Humberto A. Sanchez II", "Opie Dope Baby Jesus", "Gabby 10Meows"]

        AboutBox(info)
