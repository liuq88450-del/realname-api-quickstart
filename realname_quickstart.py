#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三要素实名核验 API 快速开始（Python 3.8+，只用标准库）

演示模式（无需 Key，验证代码结构）：
    python3 realname_quickstart.py --demo

真实模式：
    export RN_BASE_URL="https://<开通时给的域名>"
    export RN_API_KEY="ak_live_xxx"
    python3 realname_quickstart.py --name "张*" --idcard "110101********1234" --mobile "138****5678"

说明：
- 请求头 X-API-Key 鉴权，JSON 进 JSON 出，不需要签名。
- 示例数据均为脱敏占位；换成自己的测试数据再跑。
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

PATH = "/v1/id3"


def mask_name(name):
    return name[0] + "*" * (len(name) - 1) if len(name) > 1 else "*"


def mask_idcard(s):
    return s[:6] + "*" * (len(s) - 10) + s[-4:] if len(s) >= 10 else "****"


def mask_mobile(s):
    return s[:3] + "****" + s[-4:] if len(s) >= 7 else "****"


def build_payload(name, idcard, mobile):
    return {"name": name, "id_number": idcard, "mobile": mobile}


def demo(payload):
    masked = {
        "name": mask_name(payload["name"]),
        "id_number": mask_idcard(payload["id_number"]),
        "mobile": mask_mobile(payload["mobile"]),
    }
    print("[demo] 将要发送的请求（已脱敏）：")
    print(json.dumps(masked, ensure_ascii=False, indent=2))
    print(json.dumps({
        "code": "OK",
        "request_id": "r_demo_000000000000",
        "result": {"match": True, "level": "id3"},
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
        with urllib.request.urlopen(req, timeout=10) as resp:
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
    p.add_argument("--name", default="张*")
    p.add_argument("--idcard", default="110101********1234")
    p.add_argument("--mobile", default="138****5678")
    args = p.parse_args(argv or sys.argv[1:])

    payload = build_payload(args.name, args.idcard, args.mobile)

    if args.demo:
        demo(payload)
        return 0

    missing = [k for k, v in {"RN_BASE_URL": args.base_url, "RN_API_KEY": args.api_key}.items() if not v]
    if missing:
        print("缺少参数：" + ", ".join(missing))
        print("先设置环境变量，或加 --demo 先跑演示。")
        return 2

    print("→ 发起三要素核验……")
    try:
        result = call(args.base_url, args.api_key, payload)
    except RuntimeError as e:
        print("请求失败：" + str(e))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("提示：把 request_id 写进日志，排障和对账都靠它。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
