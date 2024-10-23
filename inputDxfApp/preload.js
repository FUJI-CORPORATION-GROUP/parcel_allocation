const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("dxfLoader", {
  loadDXF: (filePath) => ipcRenderer.invoke("load-dxf", filePath),
});
