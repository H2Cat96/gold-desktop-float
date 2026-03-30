import { app, BrowserWindow, ipcMain } from 'electron'
import path from 'node:path'
import url from 'node:url'

const appDir = path.dirname(url.fileURLToPath(import.meta.url))

let win

function createWindow () {
  win = new BrowserWindow({
    width: 360,
    height: 480,
    minWidth: 300,
    minHeight: 340,
    frame: false,
    transparent: true,
    resizable: true,
    alwaysOnTop: true,
    backgroundColor: '#00000000',
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
      preload: path.join(appDir, 'preload.cjs')
    },
    titleBarStyle: 'hiddenInset'
  })

  win.setAlwaysOnTop(true, 'screen-saver')

  // 默认半透明，鼠标悬停时恢复不透明
  win.setOpacity(0.3)

  ipcMain.on('mouse-enter', () => {
    win.setOpacity(1)
  })
  ipcMain.on('mouse-leave', () => {
    win.setOpacity(0.3)
  })

  const indexUrl = url.pathToFileURL(path.join(appDir, 'index.html')).toString()

  win.loadURL(indexUrl)
  win.on('ready-to-show', () => win.show())
}

if (!app.requestSingleInstanceLock()) {
  app.quit()
} else {
  app.on('second-instance', () => {
    if (win) {
      if (win.isMinimized()) win.restore()
      win.focus()
    }
  })

  app.whenReady().then(() => {
    createWindow()
    app.on('activate', function () {
      if (BrowserWindow.getAllWindows().length === 0) createWindow()
    })
  })
}

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
