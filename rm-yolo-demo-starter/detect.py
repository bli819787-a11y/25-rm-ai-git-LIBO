from argparse import ArgumentParser
from pathlib import Path
import cv2
import time
from ultralytics import YOLO

# 支持的文件后缀
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent


def parse_args():
    """解析命令行参数 DAY3基础参数 + DAY4视频扩展参数"""
    parser = ArgumentParser(description="RM YOLOv8 Detection Demo (DAY3 Image + DAY4 Video)")
    parser.add_argument("--source", required=True, help="输入源：图片路径/视频路径/摄像头编号0/1")
    parser.add_argument("--model", default="models/best.pt", help="YOLO模型权重路径")
    parser.add_argument("--output", default="outputs/result.jpg", help="输出文件路径，视频自动替换后缀为mp4")
    parser.add_argument("--conf", type=float, default=0.25, help="检测置信度阈值")
    parser.add_argument("--max-det", type=int, default=None, help="保留置信度最高的前N个目标")
    parser.add_argument("--show", action="store_true", help="弹出窗口实时显示结果")
    parser.add_argument("--fps", type=int, default=30, help="视频输出帧率")
    return parser.parse_args()


def get_class_name(names, class_id):
    """兼容数字/列表/字典类别映射"""
    if isinstance(names, dict):
        return names.get(class_id, str(class_id))
    if isinstance(names, list) and class_id < len(names):
        return names[class_id]
    return str(class_id)


def resolve_input_path(path):
    """输入路径标准化，兼容摄像头数字"""
    if str(path).isdigit():
        return int(path)
    p = Path(path)
    if p.is_absolute() or p.exists():
        return p
    return PROJECT_ROOT / p


def resolve_output_path(path, is_video=False):
    """输出路径标准化，视频强制后缀mp4"""
    p = Path(path)
    if p.is_absolute():
        out_p = p
    else:
        out_p = PROJECT_ROOT / p
    # 视频输出统一后缀mp4
    if is_video:
        out_p = out_p.with_suffix(".mp4")
    # 自动创建输出目录
    out_p.parent.mkdir(parents=True, exist_ok=True)
    return out_p


def draw_detections(image, result):
    """统一绘图函数（DAY3封装，图片/视频帧共用）"""
    if not result.boxes:
        return
    for box in result.boxes:
        # 框坐标
        x1, y1, x2, y2 = box.xyxy[0].int().tolist()
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        cls_name = get_class_name(result.names, cls_id)
        label = f"{cls_name} {conf:.2f}"
        # 绘制框与文字
        cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 255), 2)
        cv2.putText(
            image, label,
            (max(0, x1), max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (255, 0, 255), 2, lineType=cv2.LINE_AA
        )


def run_image(source, model_path, output, conf, args, show=False):
    """DAY3 图片检测主逻辑，传入args使用max‑det参数"""
    # 读取图片
    img = cv2.imread(str(source))
    if img is None:
        raise FileNotFoundError(f"无法读取图片：{source}")
    # 加载模型推理
    model = YOLO(str(model_path))
    results = model.predict(img, conf=conf, verbose=False)

    # DAY‑3 max‑det 筛选目标，缩进4空格
    boxes = results[0].boxes
    if args.max_det is not None and boxes is not None:
        confs = boxes.conf
        sorted_idx = confs.argsort(descending=True)[:args.max_det]
        results[0].boxes = boxes[sorted_idx]

    annot_img = img.copy()
    draw_detections(annot_img, results[0])

    # 统计检测数量
    detect_num = len(results[0].boxes) if results[0].boxes else 0
    print(f"图片检测完成，共检测到 {detect_num} 个目标")

    # 保存结果
    if not cv2.imwrite(str(output), annot_img):
        raise RuntimeError(f"图片保存失败：{output}")
    print(f"图片结果已保存至：{output}")

    # 窗口展示
    if show:
        cv2.imshow("RM YOLO DAY3 Image Detect", annot_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def run_video(source, model_path, output, conf, args, out_fps=30, show=False):
    """DAY4 视频/摄像头检测完整实现，传入args"""
    # 打开视频流
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频/摄像头：{source}")

    # 获取视频基础参数
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    src_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"视频分辨率：{w}×{h}，源帧率：{src_fps:.1f}，总帧数：{total_frames}")

    # 视频写入器
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output), fourcc, out_fps, (w, h))
    model = YOLO(str(model_path))

    frame_idx = 0
    total_detect = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1

        # 单帧推理
        results = model.predict(frame, conf=conf, verbose=False)
        # max‑det筛选每一帧的目标
        boxes = results[0].boxes
        if args.max_det is not None and boxes is not None:
            confs = boxes.conf
            sorted_idx = confs.argsort(descending=True)[:args.max_det]
            results[0].boxes = boxes[sorted_idx]

        annot_frame = frame.copy()
        draw_detections(annot_frame, results[0])

        # 累计检测数量
        frame_det = len(results[0].boxes) if results[0].boxes else 0
        total_detect += frame_det

        # 实时FPS文字
        cost = time.time() - start_time
        real_fps = frame_idx / cost if cost > 0 else 0
        cv2.putText(
            annot_frame, f"FPS:{real_fps:.1f}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )

        # 写入输出视频
        writer.write(annot_frame)

        # 窗口显示
        if show:
            cv2.imshow("RM YOLO DAY4 Video Detect", annot_frame)
            # 按q/ESC退出
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                print("手动终止视频检测")
                break

        # 每50帧打印进度
        if frame_idx % 50 == 0:
            print(f"已处理帧：{frame_idx}/{total_frames}，当前帧目标数：{frame_det}")

    # 释放资源
    cap.release()
    writer.release()
    cv2.destroyAllWindows()
    print(f"视频处理完成，总检测目标数：{total_detect}")
    print(f"标注视频已保存至：{output}")


def main():
    args = parse_args()
    source = resolve_input_path(args.source)
    model_path = resolve_input_path(args.model)

    # 校验模型文件
    if not Path(model_path).exists():
        raise FileNotFoundError(f"模型文件不存在：{model_path}")

    # ==========DAY‑4：批量图片处理（source为文件夹）==========
    if isinstance(source, Path) and source.is_dir():
        out_dir = resolve_output_path(args.output, is_video=False)
        out_dir.mkdir(exist_ok=True, parents=True)
        img_list = []
        for file in source.iterdir():
            suffix = file.suffix.lower()
            if suffix in IMAGE_EXTENSIONS:
                img_list.append(file)
        if len(img_list) == 0:
            print("文件夹内没有找到支持格式的图片！")
            return

        total_target = 0
        for img_file in img_list:
            out_img = out_dir / img_file.name
            img = cv2.imread(str(img_file))
            model = YOLO(str(model_path))
            results = model.predict(img, conf=args.conf, verbose=False)
            # max‑det筛选
            boxes = results[0].boxes
            if args.max_det is not None and boxes is not None:
                confs = boxes.conf
                sorted_idx = confs.argsort(descending=True)[:args.max_det]
                results[0].boxes = boxes[sorted_idx]

            annot_img = img.copy()
            draw_detections(annot_img, results[0])
            detect_num = len(results[0].boxes) if results[0].boxes else 0
            total_target += detect_num
            cv2.imwrite(str(out_img), annot_img)
            print(f"{img_file.name} 检测到：{detect_num} 个目标，保存至 {out_img}")
        print(f"\n批量处理完毕，总共检测到目标数量：{total_target}")
        return

    # 摄像头输入
    if isinstance(source, int):
        output = resolve_output_path(args.output, is_video=True)
        run_video(source, model_path, output, args.conf, args, args.fps, args.show)
    else:
        suffix = source.suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            # DAY3 单张图片检测
            output = resolve_output_path(args.output, is_video=False)
            if not source.exists():
                raise FileNotFoundError(f"图片文件不存在：{source}")
            run_image(source, model_path, output, args.conf, args, args.show)
        elif suffix in VIDEO_EXTENSIONS:
            # DAY4 视频文件检测
            output = resolve_output_path(args.output, is_video=True)
            if not source.exists():
                raise FileNotFoundError(f"视频文件不存在：{source}")
            run_video(source, model_path, output, args.conf, args, args.fps, args.show)
        else:
            raise ValueError(f"不支持的输入格式：{source.name}，仅支持图片{IMAGE_EXTENSIONS}、视频{VIDEO_EXTENSIONS}、摄像头0/1")


if __name__ == "__main__":
    main()



    
