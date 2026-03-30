console.log('process.type:', process.type)
const _e = require('electron')
console.log('electron require result type:', typeof _e)
console.log('electron require result:', typeof _e === 'string' ? _e.slice(0, 60) : JSON.stringify(Object.keys(_e||{})).slice(0,100))
const { app, BrowserWindow, ipcMain } = _e
const path = require('node:path')
const url = require('node:url')

const appDir = __dirname

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

  // 默认半透明 + 鼠标穿透
  win.setOpacity(0.25)
  win.setIgnoreMouseEvents(true, { forward: true })

  ipcMain.on('mouse-enter', () => {
    win.setIgnoreMouseEvents(false)
    win.setOpacity(1)
  })
  ipcMain.on('mouse-leave', () => {
    win.setIgnoreMouseEvents(true, { forward: true })
    win.setOpacity(0.25)
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
