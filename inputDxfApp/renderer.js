const { ipcRenderer } = require("electron");
const canvas = document.getElementById("dxfCanvas");
const context = canvas.getContext("2d");
const fs = require("fs");
const path = require("path");

const outJsonFilePath = "./out/";
const frameInputDataJsonFileName = "frame_input_data.json";
const roadInputDataJsonFileName = "road_input_data.json";

let selectedEdges = []; // 複数の選択されたエッジを保持

document.getElementById("loadDxfButton").addEventListener("click", () => {
  // メインプロセスにDXFファイル読み込みのリクエストを送信
  filePath = "./dxf/30571-1.dxf";
  // filePath = "./dxf/sample.dxf";
  filePath = "./dxf/30571-1_only_one_frame.dxf";
  selectedEdges = [];
  ipcRenderer.send("load-dxf-file", filePath);
});

document.getElementById("makeJsonButton").addEventListener("click", () => {
  saveSelectedEdges();
});

document.getElementById("runPythonButton").addEventListener("click", () => {
  // ./test.pyを実行
  console.log("runPythonButton clicked");
  const { spawn } = require("child_process");
  const pythonProcess = spawn("python", ["./test.py"]);
});

ipcRenderer.on("dxf-data", (event, dxfData) => {
  console.log("DXF data received:", dxfData);
  this.formattedDxfEntityData = getFormattedDxfEntitiesData(dxfData);
  drawDxfOnCanvas(this.formattedDxfEntityData);
});

function drawDxfOnCanvas(entityData) {
  context.clearRect(0, 0, canvas.width, canvas.height);
  console.log("drawDxfOnCanvas", entityData);
  entityData.forEach((entity) => {
    if (entity === undefined) return;

    if (entity.type === "LINE") {
      context.beginPath();

      if (selectedEdges.includes(entity)) {
        context.strokeStyle = "red"; // 選択されたエッジは赤色で描画
      } else {
        context.strokeStyle = "black";
      }

      context.moveTo(entity.x1, entity.y1);
      context.lineTo(entity.x2, entity.y2);
      context.stroke();
    }
  });
}

function getFormattedDxfEntitiesData(dxfData) {
  // DXFデータの座標の範囲を計算
  const { minX, minY, maxX, maxY } = calculateBoundingBox(dxfData);
  console.log("min-max", minX, minY, maxX, maxY);

  // Canvasのサイズに合わせてスケールとオフセットを計算
  const dxfWidth = maxX - minX;
  const dxfHeight = maxY - minY;

  // Canvasに収めるためのスケーリング
  const scaleX = canvas.width / dxfWidth;
  const scaleY = canvas.height / dxfHeight;
  const scale = Math.min(scaleX, scaleY); // 横と縦のスケールを同じにするため、最小値を使用

  // DXF全体をCanvasの中央に配置するためのオフセット
  const offsetX = -minX * scale + (canvas.width - dxfWidth * scale) / 2;
  const offsetY = -minY * scale + (canvas.height - dxfHeight * scale) / 2;

  // エンティティをCanvasに描画
  console.log("scale", scale, offsetX, offsetY);
  const formattedDxfEntitiesData = dxfData.entities.map((entity) => {
    if (entity.type === "LINE") {
      return {
        type: "LINE",
        x1: entity.vertices[0].x * scale + offsetX,
        y1: entity.vertices[0].y * scale + offsetY,
        x2: entity.vertices[1].x * scale + offsetX,
        y2: entity.vertices[1].y * scale + offsetY,
      };
    }
  });

  console.log("getFormattedDxfEntitiesData", formattedDxfEntitiesData);

  return formattedDxfEntitiesData;
}

/// DXFデータのバウンディングボックスを計算
function calculateBoundingBox(dxfData) {
  let minX = Infinity,
    minY = Infinity,
    maxX = -Infinity,
    maxY = -Infinity;

  dxfData.entities.forEach((entity) => {
    if (entity.type === "LINE") {
      x1 = entity.vertices[0].x;
      y1 = entity.vertices[0].y;
      x2 = entity.vertices[1].x;
      y2 = entity.vertices[1].y;

      minX = Math.min(minX, x1, x2);
      minY = Math.min(minY, y1, y2);
      maxX = Math.max(maxX, x1, x2);
      maxY = Math.max(maxY, y1, y2);
    }
  });

  return { minX, minY, maxX, maxY };
}

canvas.addEventListener("click", (event) => {
  const rect = canvas.getBoundingClientRect();
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  const clickedEdge = findClickedEdge(
    mouseX,
    mouseY,
    this.formattedDxfEntityData
  );
  console.log("canvas click event", mouseX, mouseY, clickedEdge);
  if (clickedEdge) {
    console.log("Clicked edge:", clickedEdge);
    // selectedEdge = clickedEdge; // エッジがクリックされたら選択
    const index = selectedEdges.indexOf(clickedEdge);

    if (index === -1) {
      // エッジが未選択なら追加
      selectedEdges.push(clickedEdge);
    } else {
      // エッジが選択済みなら選択解除
      selectedEdges.splice(index, 1);
    }

    drawDxfOnCanvas(this.formattedDxfEntityData); // 再描画
  }
});

function findClickedEdge(x, y, dxfData) {
  const tolerance = 5; // クリック位置とエッジの距離の許容範囲
  let clickedEdge = null;
  console.log("findClickedEdge", x, y);
  console.log("findClickedEdge", dxfData);

  dxfData.forEach((entity) => {
    if (entity === undefined) return;
    if (entity.type === "LINE") {
      x1 = entity.x1;
      y1 = entity.y1;
      x2 = entity.x2;
      y2 = entity.y2;
      console.log("x-y", x1, y1, x2, y2);

      if (isPointNearLineSegment(x, y, x1, y1, x2, y2, tolerance)) {
        clickedEdge = entity;
      }
    }
  });

  return clickedEdge;
}

function saveSelectedEdges() {
  console.log(selectedEdges);
  const frame = edgeToFrame(selectedEdges);
  const json = JSON.stringify(frame, null, 2); // JSONに変換

  // 保存するファイルパスを指定
  const filePath = path.join(
    __dirname,
    outJsonFilePath + frameInputDataJsonFileName
  );

  // ファイルに書き込む
  fs.writeFile(filePath, json, (err) => {
    if (err) {
      console.error("ファイルの保存に失敗しました:", err);
    } else {
      console.log("選択されたエッジを保存しました:", filePath);
    }
  });
}

// 点と線分の距離を計算して、クリックがエッジに近いかどうかを判定
function isPointNearLineSegment(px, py, x1, y1, x2, y2, tolerance) {
  const dist =
    Math.abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1) /
    Math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2);

  console.log("isPointNearLineSegment", dist <= tolerance);
  return dist <= tolerance;
}

function edgeToFrame(edges) {
  // edges: [{x1, y1, x2, y2}, ...]
  // frame: { [x1, y1], [x2, y2], ... }

  // このへんの処理は区画割処理の入力受け取り処理でやってもいいかも
  // 影響範囲が大きくなるのでい一旦現状の入力を再現するためにここでやる

  // pointList: [[x1, y1], [x2, y2], ...]
  let pointList = [];
  edges.forEach((edge) => {
    pointList.push([edge.x1, edge.y1]);
    pointList.push([edge.x2, edge.y2]);
  });

  console.log("pointList", pointList);

  // 重複削除
  console.log("pointList", pointList);
  pointList = pointList.filter(
    (pos, index, self) =>
      self.findIndex(
        (otherPos) => otherPos[0] === pos[0] && otherPos[1] === pos[1]
      ) === index
  );
  console.log("delete same point pointList", pointList);

  // pointListを時計回り順にソート
  let framePosList = sortPointsClockwise(pointList);

  const frame = { frame: framePosList };

  return frame;
}

function sortPointsClockwise(points) {
  // points: [[x1, y1], [x2, y2], ...]
  // 重心を求める
  let cx = 0;
  let cy = 0;
  for (let i = 0; i < points.length; i++) {
    cx += points[i][0];
    cy += points[i][1];
  }
  cx /= points.length;
  cy /= points.length;

  // 重心からの角度でソート
  points.sort((a, b) => {
    let angleA = Math.atan2(a[1] - cy, a[0] - cx);
    let angleB = Math.atan2(b[1] - cy, b[0] - cx);
    return angleA - angleB;
  });

  return points;
}
