const { ipcRenderer } = require("electron");
const canvas = document.getElementById("dxfCanvas");
const RoadCanvas = document.getElementById("dxfRoadCanvas");
const context = canvas.getContext("2d");
const fs = require("fs");
const path = require("path");

const outJsonFilePath = "./out/";
const frameInputDataJsonFileName = "frame_input_data.json";
const roadInputDataJsonFileName = "road_input_data.json";

let rawDxfData = null;
let selectedFrameEdges = []; // 複数の選択されたエッジを保持
let selectedRoadEdges = []; // 複数の選択されたエッジを保持

let isFrameInput = true;

// dxfファイルの読み込み
// TODO: ファイル選択ダイアログを表示してファイルを選択するようにする
document.getElementById("loadDxfButton").addEventListener("click", () => {
  // メインプロセスにDXFファイル読み込みのリクエストを送信
  // filePath = "./dxf/30571-1.dxf";
  // filePath = "./dxf/sample.dxf";
  filePath = "./dxf/30571-1_only_one_frame.dxf";

  // 初期化処理
  isFrameInput = true;
  selectedFrameEdges = [];
  selectedRoadEdges = [];

  ipcRenderer.send("load-dxf-file", filePath);
});

// jsonファイルの作成処理
document.getElementById("makeJsonButton").addEventListener("click", () => {
  saveSelectedEdges();
});

// pythonスクリプトの実行
document.getElementById("runPythonButton").addEventListener("click", () => {
  // ./test.pyを実行
  console.log("runPythonButton clicked");
  const { spawn } = require("child_process");
  const pythonProcess = spawn("python", ["./test.py"]);
});

document
  .getElementById("inputLandFinishButton")
  .addEventListener("click", () => {
    console.log("inputLandFinishButton clicked");
    console.log("selectedEdges", selectedFrameEdges);
    // selectedEdgesをjsonに保存
    saveSelectedEdges();
    // selectedEdgesをcanvasに描画
    drawDxfOnCanvas(selectedFrameEdges);

    isFrameInput = false;
    this.targetEntityList = selectedFrameEdges;
  });

ipcRenderer.on("dxf-data", (event, dxfData) => {
  console.log("DXF data received:", dxfData);
  this.rawDxfData = dxfData;
  this.targetEntityList = getFormattedDxfEntitiesData(dxfData);
  drawDxfOnCanvas(this.targetEntityList);
});

// dxfの描写
function drawDxfOnCanvas(entityData) {
  console.log("drawDxfOnCanvas", canvas.id);
  context.clearRect(0, 0, canvas.width, canvas.height);
  console.log("drawDxfOnCanvas", entityData);

  selectedEdges = isFrameInput ? selectedFrameEdges : selectedRoadEdges;

  entityData.forEach((entity) => {
    if (entity === undefined) return;

    if (entity.type === "LINE") {
      context.beginPath();

      if (selectedEdges.includes(entity)) {
        context.strokeStyle = "red"; // 選択されたエッジは赤色で描画
      } else {
        context.strokeStyle = "black";
      }

      context.moveTo(entity.startX, entity.startY);
      context.lineTo(entity.endX, entity.endY);
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
      startX = entity.vertices[0].x * scale + offsetX;
      startY = canvas.height - (entity.vertices[0].y * scale + offsetY);
      endX = entity.vertices[1].x * scale + offsetX;
      endY = canvas.height - (entity.vertices[1].y * scale + offsetY);
      return {
        type: "LINE",
        startX: startX,
        startY: startY,
        endX: endX,
        endY: endY,
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
      startX = entity.vertices[0].x;
      startY = entity.vertices[0].y;
      endX = entity.vertices[1].x;
      endY = entity.vertices[1].y;

      minX = Math.min(minX, startX, endX);
      minY = Math.min(minY, startY, endY);
      maxX = Math.max(maxX, startX, endX);
      maxY = Math.max(maxY, startY, endY);
    }
  });

  return { minX, minY, maxX, maxY };
}

canvas.addEventListener("click", (event) => {
  const rect = canvas.getBoundingClientRect();
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  const clickedEdge = findClickedEdge(mouseX, mouseY, this.targetEntityList);
  console.log("canvas click event", mouseX, mouseY, clickedEdge);

  if (clickedEdge) {
    console.log("Clicked edge:", clickedEdge);
    // selectedEdge = clickedEdge; // エッジがクリックされたら選択
    const index = isFrameInput
      ? selectedFrameEdges.indexOf(clickedEdge)
      : selectedRoadEdges.indexOf(clickedEdge);

    if (index === -1) {
      // エッジが未選択なら追加
      isFrameInput
        ? selectedFrameEdges.push(clickedEdge)
        : selectedRoadEdges.push(clickedEdge);
    } else {
      // エッジが選択済みなら選択解除
      isFrameInput
        ? selectedFrameEdges.splice(index, 1)
        : selectedRoadEdges.splice(index, 1);
    }

    drawDxfOnCanvas(this.targetEntityList); // 再描画
  }
});

// クリックされた辺の探索
function findClickedEdge(x, y, dxfData) {
  const tolerance = 5; // クリック位置とエッジの距離の許容範囲
  let clickedEdge = null;

  dxfData.forEach((entity) => {
    if (entity === undefined) return;
    if (isEdgeClicked(x, y, entity)) {
      clickedEdge = entity;
    }
  });

  return clickedEdge;
}

// 辺を選択したかどうかの判定
function isEdgeClicked(x, y, dxfData) {
  const { startX, startY, endX, endY } = dxfData;
  const tolerance = 5; // クリック位置とエッジの距離の許容範囲

  // 辺が水平または垂直でない場合、エラーになることを避けるため計算
  const edgeLengthSquared = (endX - startX) ** 2 + (endY - startY) ** 2;
  if (edgeLengthSquared === 0) return false; // 辺が点になっている場合

  // 辺上の最近傍の点を計算する
  let t =
    ((x - startX) * (endX - startX) + (y - startY) * (endY - startY)) /
    edgeLengthSquared;
  t = Math.max(0, Math.min(1, t)); // tの範囲を0から1に制限

  const nearestX = startX + t * (endX - startX);
  const nearestY = startY + t * (endY - startY);

  // クリック位置と最近傍の点の距離を計算
  const distance = Math.sqrt((nearestX - x) ** 2 + (nearestY - y) ** 2);

  // 最近傍の点が辺の範囲内で、クリックが近ければその辺が選択される
  return distance < tolerance && t >= 0 && t <= 1;
}

function saveSelectedEdges() {
  console.log(selectedFrameEdges);
  console.log(selectedRoadEdges);

  const frame = edgeToFrame(selectedFrameEdges);
  const frameJson = JSON.stringify(frame, null, 2); // JSONに変換

  // 保存するファイルパスを指定
  const frameFilePath = path.join(
    __dirname,
    outJsonFilePath + frameInputDataJsonFileName
  );

  // ファイルに書き込む
  fs.writeFile(frameFilePath, frameJson, (err) => {
    if (err) {
      console.error("ファイルの保存に失敗しました:", err);
    } else {
      console.log("選択されたエッジを保存しました:", frameFilePath);
    }
  });

  const road = edgeToRoads(selectedRoadEdges);
  const roadWidth = document.getElementById("roadWidth").value * 1000; // m -> mm
  const minMaguchi = document.getElementById("minMaguchi").value * 1000; // m -> mm
  const maxMaguchi = document.getElementById("maxMaguchi").value * 1000; // m -> mm
  const targetMinArea =
    document.getElementById("targetMinArea").value * 1000 * 1000; // m2 -> mm2
  const targetMaxArea =
    document.getElementById("targetMaxArea").value * 1000 * 1000; // m2 -> mm2

  const roadJsonData = {
    road_width: roadWidth,
    min_maguchi: minMaguchi,
    max_maguchi: maxMaguchi,
    target_min_area: targetMinArea,
    target_max_area: targetMaxArea,
    road_edge_point_list: road.road_edge_point_list,
  };

  const roadJson = JSON.stringify(roadJsonData, null, 2); // JSONに変換

  // 保存するファイルパスを指定
  const roadFilePath = path.join(
    __dirname,
    outJsonFilePath + roadInputDataJsonFileName
  );

  // ファイルに書き込む
  fs.writeFile(roadFilePath, roadJson, (err) => {
    if (err) {
      console.error("ファイルの保存に失敗しました:", err);
    } else {
      console.log("選択されたエッジを保存しました:", roadFilePath);
    }
  });
}

function edgeToRoads(edges) {
  // edges: [{startX, startY, endX, endY}, ...]
  // frame: { [startX, startY], [endX, endY], ... }
  let pointList = [];
  edges.forEach((edge) => {
    pointList.push([edge.startX, edge.startY]);
    pointList.push([edge.endX, edge.endY]);
  });

  const roads = { road_edge_point_list: pointList };

  return roads;
}

function edgeToFrame(edges) {
  // edges: [{startX, startY, endX, endY}, ...]
  // frame: { [startX, startY], [endX, endY], ... }

  // このへんの処理は区画割処理の入力受け取り処理でやってもいいかも
  // 影響範囲が大きくなるのでい一旦現状の入力を再現するためにここでやる

  // pointList: [[startX, startY], [endX, endY], ...]
  let pointList = [];
  edges.forEach((edge) => {
    pointList.push([edge.startX, edge.startY]);
    pointList.push([edge.endX, edge.endY]);
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
  // points: [[startX, startY], [endX, endY], ...]
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
