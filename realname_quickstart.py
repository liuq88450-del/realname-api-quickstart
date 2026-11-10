#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三要素实名核验 API 快速开始（Python 3.8+，只用标准库）

三要素 = 姓名 + 身份证号 + 本人照片（人脸比对）

演示模式（无需 Key，验证代码结构）：
    python3 realname_quickstart.py --demo

真实模式：
    export RN_BASE_URL="https://<开通时给的域名>"
    export RN_API_KEY="ak_live_xxx"
    python3 realname_quickstart.py --name "张三" --idcard "110101199001011234" --photo ./my-photo.jpg

说明：
- 请求头 X-API-Key 鉴权，JSON 进 JSON 出，不需要签名。
- 照片要求：JPG 格式，5–50KB，Base64 编码且不带 data: 前缀。本脚本会自动读取文件、校验、转换。
- 示例数据均为虚构占位；照片请用你自己的测试图，不要用真实他人的证件照。
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

PATH = "/v1/realname"

MIN_KB = 5
MAX_KB = 50


def mask_name(name):
    return name[0] + "*" * (len(name) - 1) if len(name) > 1 else "*"


def mask_idcard(s):
    return s[:6] + "*" * (len(s) - 10) + s[-4:] if len(s) >= 10 else "****"


def load_photo_base64(path):
    """读照片 → 校验格式和大小 → 转 Base64（去掉换行和 data: 前缀）。"""
    if path.startswith("data:"):
        raise SystemExit("image_base64 不要带 data: 前缀，直接传纯 Base64 字符串")
    with open(path, "rb") as f:
        raw = f.read()

    kb = len(raw) / 1024
    if kb < MIN_KB or kb > MAX_KB:
        raise SystemExit(f"照片大小 {kb:.1f}KB，要求 {MIN_KB}–{MAX_KB}KB。请先压缩或裁剪。")
    if not raw.startswith(b"\xff\xd8\xff"):
        raise SystemExit("照片不是 JPG 格式（文件头不对）。请转成 JPG 再试。")

    return base64.b64encode(raw).decode("ascii")


def build_payload(name, idcard, image_b64):
    return {"name": name, "id_number": idcard, "image_base64": image_b64}


def demo(payload):
    masked = {
        "name": mask_name(payload["name"]),
        "id_number": mask_idcard(payload["id_number"]),
        "image_base64": f"<照片 Base64，长度 {len(payload['image_base64'])} 字符>",
    }
    print("[demo] 将要发送的请求（已脱敏）：")
    print(json.dumps(masked, ensure_ascii=False, indent=2))
    print(json.dumps({
        "code": "OK",
        "request_id": "r_demo_000000000000",
        "result": {"match": True, "level": "realname"},
        "billed": True,
    }, ensure_ascii=False, indent=2))


def call(base_url, api_key, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + PATH,
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "X-API-Key": api_key,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            return json.loads(body)
        except Exception:
            raise RuntimeError(f"HTTP {e.code}: {body[:200]}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误：{e.reason}") from e


def main(argv=None):
    p = argparse.ArgumentParser(description="三要素实名核验 API 快速开始")
    p.add_argument("--demo", action="store_true", help="演示模式，不发真实请求")
    p.add_argument("--base-url", default=os.environ.get("RN_BASE_URL", ""))
    p.add_argument("--api-key", default=os.environ.get("RN_API_KEY", ""))
    p.add_argument("--name", default="张三")
    p.add_argument("--idcard", default="110101199001011234")
    p.add_argument("--photo", default="", help="本人照片文件路径（JPG，5–50KB）")
    p.add_argument("--image-base64", default="", help="也可以直接传 Base64 字符串（不带 data: 前缀）")
    args = p.parse_args(argv or sys.argv[1:])

    if args.image_base64:
        image_b64 = args.image_base64
    elif args.photo:
        image_b64 = load_photo_base64(args.photo)
    else:
        # 演示用的假 Base64，真实调用必须传你自己的照片
        image_b64 = base64.b64encode(b"\xff\xd8\xff" + b"0" * 6000 + b"\xff\xd9").decode("ascii")

    payload = build_payload(args.name, args.idcard, image_b64)

    if args.demo:
        demo(payload)
        return 0

    if not args.photo and not args.image_base64:
        print("缺照片：加 --photo ./your-photo.jpg（JPG，5–50KB）")
        return 2

    missing = [k for k, v in {"RN_BASE_URL": args.base_url, "RN_API_KEY": args.api_key}.items() if not v]
    if missing:
        print("缺少参数：" + ", ".join(missing))
        print("先设置环境变量，或加 --demo 先跑演示。")
        return 2

    print("→ 发起三要素核验（姓名 + 身份证号 + 人脸比对）……")
    try:
        result = call(args.base_url, args.api_key, payload)
    except RuntimeError as e:
        print("请求失败：" + str(e))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))

    code = result.get("code")
    if code == "OK":
        print("→ 一致：信息和照片属于同一人。")
    elif code == "NO_MATCH":
        print("→ 不一致（" + str(result.get("reason", "")) + "）：核验完成但没对上，本次计费。")
    elif code == "IMAGE_INVALID":
        print("→ 照片不合格：换一张清晰的 JPG（5–50KB）再试，本次不计费。")
    else:
        print("→ 未完成核验（" + str(code) + "）：本次不计费。")

    print("提示：把 request_id 写进日志，排障和对账都靠它。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
