#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实名核验 API 快速开始（Python 3.8+，只用标准库）

两种用法：

1) 演示模式（不发真实请求，验证代码结构，能直接跑）：
       python3 realname_quickstart.py --demo

2) 真实模式（填正式接口文档里的域名与密钥）：
       export RN_BASE_URL="https://<按正式文档填>"
       export RN_APP_ID="app_xxxxx"
       export RN_APP_SECRET="<开通时下发>"
       python3 realname_quickstart.py two   --name "张*" --idcard "110101********1234"
       python3 realname_quickstart.py three --name "张*" --idcard "110101********1234" --mobile "138****5678"

重要：
- 接口域名、路径、字段名、签名规则以开通时下发的正式文档为准。
- 本文件里的签名方式是“参数排序 + HMAC-SHA256”的通用示意，不是最终规则。
- 示例数据均为脱敏占位，换成自己的测试数据再跑。
"""

import argparse
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
import urllib.error
import urllib.request

# 【待确认】以下路径以正式文档为准
PATH_TWO = "/v1/realname/verify2"
PATH_THREE = "/v1/realname/verify3"


def mask_name(name: str) -> str:
    if len(name) <= 1:
        return "*"
    return name[0] + "*" * (len(name) - 1)


def mask_idcard(idcard: str) -> str:
    if len(idcard) < 10:
        return "****"
    return idcard[:6] + "*" * (len(idcard) - 10) + idcard[-4:]


def mask_mobile(mobile: str) -> str:
    if len(mobile) < 7:
        return "****"
    return mobile[:3] + "****" + mobile[-4:]


def build_sign(params: dict, secret: str) -> str:
    """签名示意：参数按 key 排序拼接 + HMAC-SHA256。规则以正式文档为准。"""
    items = sorted((k, str(v)) for k, v in params.items()
                   if k != "sign" and str(v) != "")
    raw = "&".join(f"{k}={v}" for k, v in items)
    return hmac.new(secret.encode("utf-8"), raw.encode("utf-8"),
                    hashlib.sha256).hexdigest()


def build_payload(app_id: str, secret: str, name: str, idcard: str,
                  mobile: str = None) -> dict:
    payload = {
        "app_id": app_id,
        "order_no": f"quickstart-{int(time.time())}-{uuid.uuid4().hex[:6]}",
        "name": name,
        "idcard": idcard,
        "timestamp": str(int(time.time())),
        "nonce": uuid.uuid4().hex[:16],
    }
    if mobile:
        payload["mobile"] = mobile
    payload["sign"] = build_sign(payload, secret)
    return payload


class DemoClient:
    """演示模式：不发网络请求，返回模拟结果，用来验证调用代码。"""

    def verify(self, product: str, name: str, idcard: str, mobile: str = None) -> dict:
        payload = build_payload("app_demo", "demo_secret", name, idcard, mobile)
        masked = dict(payload)
        masked["name"] = mask_name(name)
        masked["idcard"] = mask_idcard(idcard)
        if mobile:
            masked["mobile"] = mask_mobile(mobile)
        masked["sign"] = payload["sign"][:12] + "..."
        print("[demo] 将要发送的请求（已脱敏）：")
        print(json.dumps(masked, ensure_ascii=False, indent=2))
        return {
            "code": "0",
            "msg": "success (demo)",
            "request_id": "req_demo_" + uuid.uuid4().hex[:12],
            "order_no": payload["order_no"],
            "result": 1,
            "result_desc": "一致",
        }


class Client:
    def __init__(self, base_url: str, app_id: str, app_secret: str):
        self.base_url = base_url.rstrip("/")
        self.app_id = app_id
        self.app_secret = app_secret

    def verify(self, product: str, name: str, idcard: str, mobile: str = None) -> dict:
        path = PATH_TWO if product == "two" else PATH_THREE
        payload = build_payload(self.app_id, self.app_secret, name, idcard, mobile)
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + path, data=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            raise RuntimeError(f"HTTP {e.code}: {body}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"网络错误：{e.reason}") from e


def parse_args(argv):
    p = argparse.ArgumentParser(description="实名核验 API 快速开始")
    p.add_argument("product", nargs="?", choices=["two", "three"], default="two",
                   help="two=二要素，three=三要素")
    p.add_argument("--demo", action="store_true", help="演示模式，不发真实请求")
    p.add_argument("--name", default="张*")
    p.add_argument("--idcard", default="110101********1234")
    p.add_argument("--mobile", default="138****5678")
    p.add_argument("--base-url", default=os.environ.get("RN_BASE_URL", ""))
    p.add_argument("--app-id", default=os.environ.get("RN_APP_ID", ""))
    p.add_argument("--app-secret", default=os.environ.get("RN_APP_SECRET", ""))
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if args.product == "three" and not args.mobile:
        print("三要素需要 --mobile。")
        return 2

    if args.demo:
        client = DemoClient()
    else:
        missing = [k for k, v in {
            "base-url": args.base_url, "app-id": args.app_id,
            "app-secret": args.app_secret,
        }.items() if not v]
        if missing:
            print("缺少参数：" + ", ".join("--" + m for m in missing))
            print("先设置环境变量（RN_BASE_URL / RN_APP_ID / RN_APP_SECRET），或加 --demo 先跑演示。")
            return 2
        client = Client(args.base_url, args.app_id, args.app_secret)

    print(f"→ 发起{('二' if args.product == 'two' else '三')}要素核验……")
    try:
        result = client.verify(args.product, args.name, args.idcard,
                               args.mobile if args.product == "three" else None)
    except RuntimeError as e:
        print("请求失败：" + str(e))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))

    desc = {1: "一致", 2: "不一致", 3: "查无记录"}.get(result.get("result"))
    if desc:
        print(f"结论：{desc}（result={result.get('result')}）")
    print("提示：把 request_id 写进日志，排障和账单争议都靠它。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
